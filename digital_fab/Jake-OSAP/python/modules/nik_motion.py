import asyncio 
import traceback 
import numpy as np 
import numpy.typing as npt 

from osap.osap import OSAP 

from modules.maxl_stepper import MAXLStepper 
from modules.servo_thing import ServoThing
from modules.low_fet import LowFet
from modules.dual_h_bridge import DualHBridge

from maxl.types import MAXLInterpolationIntervals 
from maxl.core import MAXLCore, MAXLCoreConfig 
from maxl.queue_planner import MAXLQueuePlanner, MAXLQueueConfig 
from maxl.one_dof import MAXLOneDOF, MAXLOneDOFConfig 

from maxl.kinematics.intersect_circles import intersect_circles

# maxl's internal units are motor revolutions,
# we'll use degrees... so 360 per rev, 
# gear ratio is 16:110, 
shoulder_rpu = 1 / (360 * (16/110))

# the elbow is additionally geared down... 56:48 
elbow_rpu = 1 / (360 * ((16/110) * (75/48)))

class NikMotion:
    def __init__(self, osap: OSAP, interpolation_interval: MAXLInterpolationIntervals, twin_to_real_ms: int):
        self.osap = osap 

        self.interpolation_interval = interpolation_interval
        self.twin_to_real_ms = twin_to_real_ms
        self.history_length_ms = 1000

        self.xy_after_home = [0, 0]
        self.xy_extents = [25, 25]

        self.l_shoulder = 140 
        self.l_elbow = 90

        self._maxl_core = None 

        self._motor_shoulder = None
        self._motor_elbow = None 
        self._low_fet = None 

        self.queue_planner = MAXLQueuePlanner(MAXLQueueConfig(
            axes = ['X', 'Y', 'Z'],
            inertial_axes_count = 3, 
            max_accels = [1500, 1500, 10],
            max_vels = [50, 50, 5],
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

        axes_pt[0] = axes_pt[0] + 220

        # if axes_pt[0] < 15 and axes_pt[1] < 15:
        #     axes_pt[0] = 15
        #     axes_pt[1] = 15 

        p0 = np.array([0,0])
        p2 = np.array([axes_pt[0], axes_pt[1]])

        # axes_pt is in cartesian space 
        inter_a, inter_b = intersect_circles(
            p0[0], p0[1], self.l_shoulder, 
            p2[0], p2[1], self.l_elbow
        )

        if inter_a is None:
            print(p0, p2)
            raise Exception("transform singularity ?")

        p1 = inter_a if inter_a[1] > inter_b[1] else inter_b 

        theta_shoulder = np.rad2deg(np.arccos(p1[0]/self.l_shoulder))

        dist_c = np.linalg.norm(p2 - p0)

        theta_elbow = np.arccos((self.l_elbow ** 2 + self.l_shoulder ** 2 - dist_c ** 2)/(2 * self.l_shoulder * self.l_elbow))
        theta_elbow = np.rad2deg(theta_elbow) + theta_shoulder

        # and we have... that the elbow thinks it is at zero when it is at 45, 
        # and the elbow thinks it is at zero when it is at 135 ... (the motors think this) 
        actu_pts = [(theta_shoulder) * shoulder_rpu, (theta_elbow) * elbow_rpu, axes_pt[2]] 

        return axes_pt, actu_pts 
        # cosine law edition (not working) below 

        # then we need some cosine law ?    
        # c^2 = a^2 + b^2 - 2*a*b*cos(_c)
        # 2*a*b*cos(ang_c) = a^2 + b^2 - c^2 
        # cos(ang_c) = (a^2 + b^2 - c^2) / (2*a*b)
        # so the included angle we want is across from this distance 
        dist_c = np.linalg.norm(p2-p0)
        cos_ang_c = (self.l_shoulder ** 2 + self.l_elbow ** 2 - dist_c ** 2) / (2 * self.l_shoulder * self.l_elbow)

        # that ang is 
        ang_c =  np.rad2deg(np.arccos(cos_ang_c))
        # and the one we are interested in is 
        # 0 = 180 - theta_shoulder - theta_elbow - ang_c 
        theta_elbow = 180 - theta_shoulder - ang_c 

        # but we have an additional tricky inversion, where actually we are going the other way (diagram error)
        theta_elbow = theta_shoulder + ang_c 

        # and we have... that the elbow thinks it is at zero when it is at 45, 
        # and the elbow thinks it is at zero when it is at 135 ... (the motors think this) 
        actu_pts = [(theta_shoulder - 45) * theta_rpu, - (theta_elbow - 135) * theta_rpu, axes_pt[2]] 

        # returning (axes, actuator)
        return axes_pt, actu_pts
    
    async def begin(self):

        self._motor_shoulder = MAXLStepper(self.osap, "motor_shoulder")
        self._motor_elbow = MAXLStepper(self.osap, "motor_elbow")
        # self._low_fet = LowFet(self.osap, "low_fet")

        self._maxl_core = MAXLCore(self.osap, MAXLCoreConfig(
            actuators = [self._motor_shoulder, self._motor_elbow, self._low_fet],
            actuator_currents = [0.45, 0.45, 0.2],
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
        if self._low_fet is not None:
            await self._low_fet.set_gate(0)


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