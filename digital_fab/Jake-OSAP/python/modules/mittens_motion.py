import asyncio 
import traceback 
import numpy as np 
import numpy.typing as npt 

from osap.osap import OSAP 

from modules.maxl_stepper import MAXLStepper 
from modules.servo_thing import ServoThing
from modules.dual_h_bridge import DualHBridge

from maxl.types import MAXLInterpolationIntervals 
from maxl.core import MAXLCore, MAXLCoreConfig 
from maxl.queue_planner import MAXLQueuePlanner, MAXLQueueConfig 
from maxl.one_dof import MAXLOneDOF, MAXLOneDOFConfig 

from maxl.kinematics.five_bar import FiveBar

theta_rpu = (1/360) * 5

class MittensMachineMotion:
    def __init__(self, osap: OSAP, interpolation_interval: MAXLInterpolationIntervals, twin_to_real_ms: int, extents):
        self.osap = osap 

        self.interpolation_interval = interpolation_interval
        self.twin_to_real_ms = twin_to_real_ms
        self.history_length_ms = 1000

        self.five_bar = FiveBar(
            a_xy=[-145/2, 0],
            b_xy=[145/2, 0], 
            len_a1=213, 
            len_b1=213,
            len_a2=237,
            len_b2=237
        )

        # self.xy_after_home = [0, 0]
        # self.xy_extents = extents

        self._maxl_core = None 

        self._motor_a = None
        self._motor_b = None
        self._servo_z = None 

        # xy accels are: 100 for clean drawings, 500 for speed, 1500 for ludicrous 
        self.queue_planner = MAXLQueuePlanner(MAXLQueueConfig(
            axes = ['X', 'Y', 'Z'],
            inertial_axes_count = 3, 
            max_accels = [500, 500, 1500],
            max_vels = [3000, 3000, 500],
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms, 
            lookahead_queue_length = 64,
            junction_deviation = 0.75,
            min_distance = 0.01,
        ))
    

    def system_graph(self, time: int):
        # using the queue planner to do queue planner things 
        # and also to go from a time input to a set of pts, 
        axes_pt = self.queue_planner.on_new_control_point(time)

        # re-locate downwards by some, 
        axes_pt[1] = axes_pt[1] - 350

        actu_posns = self.five_bar.cart_to_actu(axes_pt)

        # print(F"{actu_posns[0] * theta_rpu:.6f}, {actu_posns[1] * theta_rpu:.6f}")

        axes_pt[2] = axes_pt[2] + 1000
        # print(axes_pt[2])

        # returning (axes, actuator)
        return axes_pt, [actu_posns[0] * theta_rpu, actu_posns[1] * theta_rpu, axes_pt[2]]
    

    async def begin(self):

        self._motor_a = MAXLStepper(self.osap, "motor_a")
        self._motor_b = MAXLStepper(self.osap, "motor_b")
        self._servo_z = ServoThing(self.osap, "servo_z")

        self._maxl_core = MAXLCore(self.osap, MAXLCoreConfig(
            actuators = [self._motor_a, self._motor_b, self._servo_z],
            actuator_currents = [0.6, 0.6, 0.2],
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms,
            history_length_ms = self.history_length_ms, 
            graph = self.system_graph, 
            print_point_transmits = False  
        ), self.queue_planner)

        # print("Machine / Begin: Waiting for Clocks... ")
        # await asyncio.sleep(3)
        print("Machine / Begin: Startup MAXL... ")
        await self._maxl_core.begin()
        print("Machine / Begin: ... done ")
        await asyncio.sleep(0.25)

    async def shutdown(self):
        if self._maxl_core is not None: 
            await self._maxl_core.shutdown() 

    async def home(self):
        return 

    # TODO: should these be within queue_planner ? 
    async def goto_relative(self, xyz_rel, e_length_scalar, rate):
        # ... from this posn, 
        xyze = await self.queue_planner.halt()

        # ... moving this len, 
        rel_dist = np.linalg.norm(xyz_rel)

        rel_vect = np.zeros(4)
        rel_vect[:3] += xyz_rel
        rel_vect[3] = rel_dist * e_length_scalar

        xyze += rel_vect
        print(F"REL {rel_vect} GOTO {xyze}")
        await self.queue_planner.goto_and_await(xyze, rate)

    # TODO: likewise, most API should be able to exclude DOF at will ? 
    async def goto_absolute_sloppy(self, xyze_targ, rate):
        # ... from this posn, 
        xyze = await self.queue_planner.halt()
        xyze[:len(xyze_targ)] = xyze_targ 
        await self.queue_planner.goto_and_await(xyze, rate) 