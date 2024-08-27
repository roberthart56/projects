import asyncio 
import traceback 
from asyncio import Task 
from collections import deque 
from dataclasses import dataclass 
from typing import List, Callable, Deque, TYPE_CHECKING

import numpy as np 
import numpy.typing as npt 

from .types import MAXLControlPoint, MAXLInterpolationIntervals, MAXLStates
from .queue_planner import MAXLQueuePlanner

from modules.maxl_stepper import MAXLStepper 

if TYPE_CHECKING:
    from ..osap.osap import OSAP 

# returns [pos, vel, acc, jerk]
def get_states_from_spline_pts(p0, p1, p2, p3, t1, t_now, t_interval_length):
    # time as 0...1 in the interval, 
    t = (t_now - t1) / t_interval_length
    # double, triple, 
    tt = np.power(t, 2) 
    ttt = np.power(t, 3) 
    # conform as np 
    p0 = np.array(p0)
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    # params, 
    a = 1/6 * p0 + 2/3 * p1 + 1/6 * p2 
    b = - 1/2 * p0 + 1/2 * p2 
    c = 1/2 * p0 - p1 + 1/2 * p2 
    d = - 1/6 * p0 + 1/2 * p1 - 1/2 * p2 + 1/6 * p3 

    # now we can get 'em all w/ 
    pos  = a + b * t + c * tt + d * ttt
    vel  = (b + c * 2 * t + d * 3 * tt) * (1000000 / t_interval_length)
    acc  = (c * 2 + d * 6 * t) #TODO ?? * (1000000 / t_interval_length)
    jerk = (d * 6) # * (1000000 / t_interval_length)

    return [
        pos, 
        vel, 
        acc, 
        jerk
    ]
    
MAXL_REMOTE_BUFFER_SIZE = 128
MAXL_RESPONSIBLE_GAP_MAXIMUM = MAXL_REMOTE_BUFFER_SIZE - 6
MAXL_RESPONSIBLE_GAP_MINIMUM = 8

@dataclass 
class MAXLCoreConfig:
    interpolation_interval: MAXLInterpolationIntervals 
    twin_to_real_gap_ms: int
    history_length_ms: int 
    actuators: List["MAXLStepper"]
    actuator_currents: List[float]
    graph: Callable[[int], npt.NDArray]
    print_point_transmits: bool = False 


class MAXLCore:
    def __init__(self, osap: "OSAP", config: MAXLCoreConfig, queue_planner: MAXLQueuePlanner):
        self.osap = osap 

        self.system_graph = config.graph 

        # a hookup - maybe temporary (or invertible) to do 
        # blockage on recalculating (for sluggishness conditions) 
        self.queue_planner = queue_planner

        self.twin_to_real_gap_us = config.twin_to_real_gap_ms * 1000
        self.history_length_us = config.history_length_ms * 1000 
        self.interpolation_interval_us = config.interpolation_interval.value[0]
        self.interpolation_bits = config.interpolation_interval.value[1] 

        self.actuators = config.actuators 
        self.actuator_currents = config.actuator_currents 

        self.print_point_transmits = config.print_point_transmits

        # how long will the gap be, in no. of pts ?
        num_ctrl_pts_in_time_gap = int(np.floor(self.twin_to_real_gap_us / self.interpolation_interval_us))
        num_ctrl_pts_in_history = int(np.ceil(self.history_length_us / self.interpolation_interval_us))
        print(F"MAXL expects {num_ctrl_pts_in_time_gap} control pts between pt-gen and pt-consume, {num_ctrl_pts_in_history} of history")

        if num_ctrl_pts_in_time_gap > MAXL_RESPONSIBLE_GAP_MAXIMUM:
            raise Exception(
                f"with a gap of {self.twin_to_real_gap_us} and an interval of {self.interpolation_interval_us}, "
                f"this config will result in overfull buffers... please decrease the gap so that it does not exceed "
                f"{MAXL_RESPONSIBLE_GAP_MAXIMUM * self.interpolation_interval_us}"
            )

        if num_ctrl_pts_in_time_gap < MAXL_RESPONSIBLE_GAP_MINIMUM:
            raise Exception(
                f"with a gap of {self.twin_to_real_gap_us} and an interval of {self.interpolation_interval_us}, "
                f"this config will probably result in starved buffers... please increase the gap so that it exceeds "
                f"{MAXL_RESPONSIBLE_GAP_MINIMUM * self.interpolation_interval_us}"
            )

        self.control_points: Deque[MAXLControlPoint] = deque(maxlen = num_ctrl_pts_in_time_gap + num_ctrl_pts_in_history + 100)
        self.main_loop_task: Task | None = None 
        self._run_main_loop = False 
        self._actuator_polling_interval_us = 1000000
        self._actuator_polling_last_time = 0 

        self._do_unsafe_recalculations = False 


    async def begin(self):
        now = self.osap.get_system_microseconds()

        for a, actuator in enumerate(self.actuators):
            if actuator is not None:
                print(f"MAXL: starting up {actuator.device_name} ...")
                await actuator.begin()
                await actuator.maxl_set_interval(self.interpolation_bits)
                if isinstance(actuator, MAXLStepper):
                    await actuator.set_current_scale(self.actuator_currents[a])

        self.control_points.append(MAXLControlPoint(np.zeros(len(self.queue_planner.axes)), np.zeros(len(self.actuators)), now + self.twin_to_real_gap_us, 1))

        self._actuator_polling_last_time = now 

        self._run_main_loop = True 
        self.main_loop_task = asyncio.create_task(self.main_loop())


    async def shutdown(self):
        print("MAXL: ... shutting down")
        self._run_main_loop = False 
        await self.main_loop_task
        for a, actuator in enumerate(self.actuators):
            if actuator is not None:
                print(f"MAXL: attempting shutdown of {actuator.device_name} ...")
                if isinstance(actuator, MAXLStepper):
                    await actuator.set_current_scale(0) 
                print(f"MAXL: ... shutdown of {actuator.device_name} OK")
        print("MAXL: ... shutdown OK")


    async def main_loop(self):
        while True:
            try:
                if not self._run_main_loop:
                    print("MAXL: ... loop exit")
                    return 
                
                now = self.osap.get_system_microseconds()

                # check / generate new (future) control points, 
                if (self.control_points[-1].time + self.interpolation_interval_us) < (now + self.twin_to_real_gap_us):
                    sluggishness_gap = (now + self.twin_to_real_gap_us) - (self.control_points[-1].time + self.interpolation_interval_us * 2)
                    if sluggishness_gap > 10000:
                        print(f"MAXL: WARNING: pt gen is sluggish by {sluggishness_gap}us")
                        if not self._do_unsafe_recalculations:
                            self.queue_planner.do_recalculations = False 
                    else:
                        self.queue_planner.do_recalculations = True 
                    previous_point = self.control_points[-1]
                    time = previous_point.time + self.interpolation_interval_us 

                    # use ... a buncha transforms to make actuator points, 
                    next_cartesian, next_actuators = self.system_graph(time)
                    self.control_points.append(MAXLControlPoint(next_cartesian, next_actuators, time, 0))

                # check / transmit points, 
                for pt in self.control_points:
                    if pt.tx_time == 0:
                        if self.print_point_transmits:
                            print(f"MAXL: TX point to {[f"{x:.5f}" for x in pt.position_actuator]} for {pt.time} w/ flag {pt.flags}")
                        tasks = [] 
                        for a, actuator in enumerate(self.actuators):
                            if actuator is not None:
                                if pt.position_actuator[a] > 16000 or pt.position_actuator[a] < -16000:
                                    print(f"MAXL: WARNING: you are getting close to wrapping fxp16_16 * 1.5625 w/ \
                                          {pt.position_actuator[a]:.3f} ... time to finish that project !")
                                tasks.append(actuator.maxl_add_control_point(pt.time, pt.position_actuator[a], pt.flags))
                        pt.tx_time = now
                        self.control_point_most_recent_tx = pt 
                        await asyncio.gather(*tasks) 

                # rm historical control pts, 
                if self.control_points[0].time < now - self.history_length_us:
                    old_pt = self.control_points.popleft()
                    # print(F"popped to len {len(self.control_points)}, times: {old_pt.time} at {now}")

                # check for error msgs from actuators 
                if self._actuator_polling_last_time + self._actuator_polling_interval_us < now:
                    self._actuator_polling_last_time = now 
                    tasks = [] 
                    real_actuators = [] 
                    for actuator in self.actuators:
                        if actuator is not None:
                            tasks.append(actuator.maxl_get_error_message())
                            real_actuators.append(actuator)

                    messages = await asyncio.gather(*tasks)
                    for actuator, message in zip(real_actuators, messages):
                        if message:
                            print(f"{actuator.device_name}: {message}")

                # else carry on... 
                await asyncio.sleep(0)

            except Exception as err:
                print(err)         
                print(traceback.format_exc())
                self._run_main_loop = False 

        # end main_loop

    # returns a tuple of cartesian_states, actuator_states, with t[0] = posns ... t[3] = jerk 
    def get_states_at_us(self, time_us: int):
        # index of the *most recently passed* control point, 
        index = next((i for i, pt in enumerate(self.control_points) if (pt.time < time_us and time_us < (pt.time + self.interpolation_interval_us))), None)
        if index is None:
            oldest_pt_time = self.control_points[0].time
            newest_pt_time = self.control_points[-1].time
            raise Exception(F"MAXL couldn't find any control points around {time_us}, history spans {oldest_pt_time} ... {newest_pt_time}")
        
        if index < 0 or (index + 2) > len(self.control_points):
            oldest_pt_time = self.control_points[0].time
            newest_pt_time = self.control_points[-1].time
            raise Exception(F"MAXL doesn't have enough local history around {time_us} to resolve states, history spans {oldest_pt_time} ... {newest_pt_time}, {index} of {len(self.control_points)}")

        local_cartesian_pts = [
            self.control_points[index - 1].position_cartesian,
            self.control_points[index].position_cartesian,
            self.control_points[index + 1].position_cartesian,
            self.control_points[index + 2].position_cartesian
        ]

        local_actuator_pts = [
            self.control_points[index - 1].position_actuator,
            self.control_points[index].position_actuator,
            self.control_points[index + 1].position_actuator,
            self.control_points[index + 2].position_actuator
        ]

        t1 = self.control_points[index].time

        return (
            get_states_from_spline_pts(*local_cartesian_pts, t1, time_us, self.interpolation_interval_us), 
            get_states_from_spline_pts(*local_actuator_pts, t1, time_us, self.interpolation_interval_us)
        )

