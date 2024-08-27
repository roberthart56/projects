import asyncio 
import traceback 
import numpy as np 
import numpy.typing as npt 

from osap.osap import OSAP 

from modules.maxl_stepper import MAXLStepper 
from modules.low_fet import LowFet
from modules.servo_thing import ServoThing
from modules.dual_h_bridge import DualHBridge

from maxl.types import MAXLInterpolationIntervals 
from maxl.core import MAXLCore, MAXLCoreConfig 
from maxl.queue_planner import MAXLQueuePlanner, MAXLQueueConfig 
from maxl.one_dof import MAXLOneDOF, MAXLOneDOFConfig 

# 30 teeth, 2mm per tooth
xy_rpu = 1 / 60

xy_accels = 10000
xy_max_rates = 10000

class VVelocityMachineMotion:
    def __init__(self, osap: OSAP, interpolation_interval: MAXLInterpolationIntervals, twin_to_real_ms: int, extents):
        self.osap = osap 

        self.interpolation_interval = interpolation_interval
        self.twin_to_real_ms = twin_to_real_ms
        self.history_length_ms = 1000

        self._maxl_core = None 

        self._motor_a = None
        self._motor_b = None
        self._low_fet = None 

        self._y_correct = np.sin(np.deg2rad(25))

        # xy accels are: 100 for clean drawings, 500 for speed, 1500 for ludicrous 
        self.queue_planner = MAXLQueuePlanner(MAXLQueueConfig(
            axes = ['X', 'Y', 'Z'],
            inertial_axes_count = 3, 
            max_accels = [xy_accels, xy_accels, 1000],
            max_vels = [xy_max_rates, xy_max_rates, 1000],
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

        # print(F"{axes_pt[0]:.2f}, {axes_pt[1]:.2f}")

        # it's the same as corexy ? 
        actu_pts = [
            xy_rpu * (axes_pt[0] + axes_pt[1] * self._y_correct) / 2,
            xy_rpu * (axes_pt[0] - axes_pt[1] * self._y_correct) / 2,
            axes_pt[2]
        ]

        # returning (axes, actuator)
        return axes_pt, actu_pts
    

    async def begin(self):

        self._motor_a = MAXLStepper(self.osap, "motor_a")
        self._motor_b = MAXLStepper(self.osap, "motor_b")

        self._maxl_core = MAXLCore(self.osap, MAXLCoreConfig(
            actuators = [self._motor_a, self._motor_b, self._low_fet],
            actuator_currents = [0.5, 0.5, 0.2],
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms,
            history_length_ms = self.history_length_ms, 
            graph = self.system_graph, 
            print_point_transmits = False  
        ), self.queue_planner)

        self._maxl_core._do_unsafe_recalculations = False 

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