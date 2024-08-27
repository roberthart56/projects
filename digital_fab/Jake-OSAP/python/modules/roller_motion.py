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

# maxl's internal units are motor revolutions,
# with xy we have a 20T, 2mm pitch belt, 40mm *units* per revolution
# with z we have an 8mm pitch leadscrew, so, well, 8mm per rev 
x_rpu = 1 / 40

# diameter is 59mm, 
y_diameter = 59 
# y_rpu = x_rpu
y_rpu = 1 / (np.pi * y_diameter)

# servo units are 500-2500, we have about 5mm throw within 
z_upu = - 2000 / 5 

class RollerMachineMotion:
    def __init__(self, osap: OSAP, interpolation_interval: MAXLInterpolationIntervals, twin_to_real_ms: int):
        self.osap = osap 

        self.interpolation_interval = interpolation_interval
        self.twin_to_real_ms = twin_to_real_ms
        self.history_length_ms = 1000

        self.xy_after_home = [0, 0]
        self.xy_extents = [260, 500]

        self._graph_on_point_callback = None 

        self._maxl_core = None 

        self._motor_x = None
        self._motor_y = None 
        self._servo_z = None 

        self.queue_planner = MAXLQueuePlanner(MAXLQueueConfig(
            axes = ['X', 'Y', 'Z'],
            inertial_axes_count = 3, 
            max_accels = [500, 150, 150],
            max_vels = [150, 50, 10],
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms, 
            lookahead_queue_length = 64,
            junction_deviation = 0.75,
            min_distance = 0.01,
        ))

        self._xy_dof_configs = MAXLOneDOFConfig(
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms,
            history_length_ms = self.history_length_ms,
            max_accel = 1000, 
            max_vel = 100
        )

        self._z_dof_configs = MAXLOneDOFConfig(
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms,
            history_length_ms = self.history_length_ms,
            max_accel = 500, 
            max_vel = 50
        )

        # # modal in cartesian space 
        # self.x_back_dof = MAXLOneDOF(self._xy_dof_configs)
        # self.x_front_dof = MAXLOneDOF(self._xy_dof_configs)
        # self.y_dof = MAXLOneDOF(self._xy_dof_configs)
    

    def system_graph(self, time: int):
        # using the queue planner to do queue planner things 
        # and also to go from a time input to a set of pts, 
        axes_pt = self.queue_planner.on_new_control_point(time)

        actu_pts = [axes_pt[0] * x_rpu, axes_pt[1] * y_rpu, 500 + axes_pt[2] * z_upu] 

        # print(actu_pts[2])

        # returning (axes, actuator)
        return axes_pt, actu_pts
    

    async def begin(self):

        self._motor_x = MAXLStepper(self.osap, "motor_x")
        self._motor_y = MAXLStepper(self.osap, "motor_y")
        self._servo_z = ServoThing(self.osap, "servo_z")

        self._maxl_core = MAXLCore(self.osap, MAXLCoreConfig(
            actuators = [self._motor_x, self._motor_y, self._servo_z],
            actuator_currents = [0.35, 0.35, 0.2],
            interpolation_interval = self.interpolation_interval, 
            twin_to_real_gap_ms = self.twin_to_real_ms,
            history_length_ms = self.history_length_ms, 
            graph = self.system_graph,
            print_point_transmits = False  
        ), self.queue_planner)

        print("Machine / Begin: Startup MAXL... ")
        await self._maxl_core.begin()
        print("Machine / Begin: ... done ")
        await asyncio.sleep(0.25)


    async def shutdown(self):
        if self._maxl_core is not None: 
            await self._maxl_core.shutdown() 


    async def home(self):
        return 


    async def tour_extents(self):
        await self.queue_planner.goto_and_await([0,0,0],                                        100)
        await self.queue_planner.goto_and_await([self.xy_extents[0],    0,                  0], 100)
        await self.queue_planner.goto_and_await([self.xy_extents[0],    self.xy_extents[1], 0], 100)
        await self.queue_planner.goto_and_await([0,                     self.xy_extents[1], 0], 100)
        await self.queue_planner.goto_and_await([0,0,0],                                        100)


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