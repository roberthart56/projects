import asyncio 
import numpy as np 
import numpy.typing as npt 
from collections import deque 
from typing import List, Deque
from dataclasses import dataclass, field 

from .types import MAXLInterpolationIntervals
from .queue_planner_functional import MAXLQueueSegment, recalculate_queue, make_blocks 

import time 

def get_microsecond_timestamp() -> float:
    return time.time_ns() // 1e3 

@dataclass 
class HWMProfiler:
    hwm: float = 0 
    avg: float = 0 
    _start_time: int = 0 

    def start(self):
        self._start_time = get_microsecond_timestamp() 

    def stop(self):
        run_time = get_microsecond_timestamp() - self._start_time
        if run_time > self.hwm:
            self.hwm = run_time 
        
        self.avg = self.avg * 0.99 + run_time * 0.01 


@dataclass
class MAXLQueueConfig:
    axes: List[str]
    inertial_axes_count: int 
    max_accels: npt.ArrayLike
    max_vels: npt.ArrayLike

    interpolation_interval: MAXLInterpolationIntervals
    twin_to_real_gap_ms: int 
    lookahead_queue_length: int 

    junction_deviation: float 
    min_distance: float 


class MAXLQueuePlanner:
    # TBD if we need an osap 
    def __init__(self, config: MAXLQueueConfig):
        # con-figgy 
        self.axes = config.axes 
        self.inertial_axes_count = config.inertial_axes_count 
        self.max_accels = np.array(config.max_accels)
        self.max_vels = np.array(config.max_vels)
        self.junction_deviation = config.junction_deviation 
        self.min_distance = config.min_distance 

        self.interpolation_interval = config.interpolation_interval.value[0]
        self.twin_to_real_gap_us = config.twin_to_real_gap_ms * 1000 
        self.lookahead_queue_length = config.lookahead_queue_length 

        # for blockage / unblockage during perf hotness times 
        self.do_recalculations = True 

        # states 
        self.p_tail = np.zeros(len(self.axes))
        self.queue: Deque[MAXLQueueSegment] = deque(maxlen = self.lookahead_queue_length + 64)
        self._offset = np.zeros(len(self.axes))
        self._last_pos_out = None 

        # profiling 
        self._profiler_addsegment = HWMProfiler() 
        self._profiler_newcp = HWMProfiler() 
        self._profiler_replan = HWMProfiler() 

        # check for odditees 
        if self.inertial_axes_count > len(self.axes):
            raise ValueError(f"num. interial axes exceeds len(self.axes)")
        if self.inertial_axes_count > 3:
            raise ValueError(f"num inertial axes exceeds '3' - current MAXL is not properly equipped for this")

        if len(self.max_accels) != len(self.axes) or len(self.max_vels) != len(self.axes):
            raise ValueError(f"max_accels ({len(self.max_accels)}), max_vels ({len(self.max_vels)}), and axes ({len(self.axes)}) should all be of equal length")


    # ----------------------------------------------------- flow ? 

    def on_new_control_point(self, time: int):
        self._profiler_newcp.start() 
        if len(self.queue) > 0:
            # firstly we need to assign a zero-time if our first element doesn't have one, 
            # this will be basically right-now, i.e. at the next control point, 
            if self.queue[0].t_start_us == 0:
                self.queue[0].t_start_us = time

            # now we can try to remove oldies / cycle the queue, 
            for _ in range(len(self.queue)):
                if self.queue[0].end_time() < time:
                    # assign the next start if we have it, 
                    if len(self.queue) > 1:
                        self.queue[1].t_start_us = self.queue[0].end_time() 
                    # pop all historic segments, and track tail position, 
                    self.p_tail = (self.queue.popleft()).p_end 
                else:
                    # we are done clearing historical segments 
                    break 
        
        # we changed the length of the queue, do we still have items ?
        if len(self.queue) > 0:
            # now the 0th is the current, 
            states = self.queue[0].states_at_time(time - self.queue[0].t_start_us)
            self._profiler_newcp.stop()
            self._last_pos_out = states.pos  
            return states.pos.copy()

        else:
            # we are totally queue-less, just ship the same point (we are stopped) 
            # return MAXLControlPoint(self.p_tail, time, point.flags)
            self._profiler_newcp.stop() 
            return self.p_tail.copy()


    # ----------------------------------------------------- queue API

    async def goto_via_queue(self, position: npt.ArrayLike, target_vel: float):
        position = np.array(position) - self._offset 
        while True:
            if len(self.queue) >= self.lookahead_queue_length or self.do_recalculations != True:
                await asyncio.sleep(0.1)
            else:
                # shim with breather for control point generation 
                await asyncio.sleep(0)
                return self._add_segment(position, target_vel)
    
    async def goto_and_await(self, position: npt.ArrayLike, target_vel: float):
        await self.goto_via_queue(position, target_vel)
        await self.flush_queue()
        await asyncio.sleep(0.1) 

    async def halt(self):
        # a little more complex, 
        self.queue = deque(maxlen = self.lookahead_queue_length + 64)
        self.p_tail = self._last_pos_out 
        await self.flush_queue() 
        return self.p_tail + self._offset

    async def flush_queue(self):
        while True:
            if len(self.queue) > 0:
                await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(self.twin_to_real_gap_us / 1000000)
                return 
    
    def set_current_position(self, position_set: npt.ArrayLike):
        position_set = np.array(position_set)
        current_position = self._get_position_tail()
        # self._offset = current_position - position_set
        self._offset = position_set - current_position
        print(f"MAXL: current: {current_position}, set offset for {position_set}: {self._offset}")


    # ----------------------------------------------------- internal use (?) 

    def _get_position_tail(self):
        # returns *either* the end of the current queue *or* our most-latest control point, 
        # i.e. where we would be starting from... back of the positions queue... 
        if len(self.queue) > 0:
            return self.queue[-1].p_end.copy() 
        else:
            return self.p_tail.copy()

    def _add_segment(self, p_end: npt.ArrayLike, target_vel: float):
        self._profiler_addsegment.start() 
        # assign a p_start to the segment, and walk the tail
        p_end = np.asarray(p_end)
        if p_end.size != len(self.axes):
            raise ValueError("p_end must be the same len as axes")

        p_start = self._get_position_tail()

        p_delta = p_end - p_start
        p_distance = np.linalg.norm(p_delta)

        if p_distance < self.min_distance:
            print(f"MAXL: WARNING: rejecting move of {p_distance:.6f} for all axes vs min {self.min_distance}")
            self._profiler_addsegment.stop() 
            return 
        
        p_unit = p_delta / p_distance

        # pick max accel to fit bounds, 
        acc_factor = np.abs(p_unit / np.asarray(self.max_accels))
        max_acc_factor = np.max(acc_factor)
        accels = p_unit * (1 / max_acc_factor)
        accel = float(np.linalg.norm(accels))

        # and a max vel to fit bounds, 
        vel_factor = np.abs(p_unit / np.asarray(self.max_vels))
        max_vel_factor = np.max(vel_factor)
        vels = p_unit * (1 / max_vel_factor)
        vmax = min(target_vel, float(np.linalg.norm(vels)))

        # calculate inertial distance and unit, 
        # ... which are used in jd maths 
        inertial_delta = p_end[:self.inertial_axes_count] - p_start[:self.inertial_axes_count] 
        inertial_distance = np.linalg.norm(inertial_delta) 
        if self.inertial_axes_count != 0 and inertial_distance != 0:
            inertial_unit = inertial_delta / inertial_distance 
        else:
            # uuuh... 
            inertial_unit = np.array([])

        # print("--- add seg:")
        # print("       unit: ", p_unit, self.max_accels)
        # print(" acc_factor: ", acc_factor)
        # print(" accel pick: ", accels, accel)
        # print(" vel_factor: ", vel_factor)
        # print("   vel pick: ", vels, vmax)

        # we should stick it in a queue then
        self.queue.append(MAXLQueueSegment(
            p_end, p_start, 
            self.inertial_axes_count, 
            target_vel, 
            p_unit, 
            float(p_distance), 
            accel, 
            vmax,
            inertial_unit, 
            inertial_distance 
        ))

        self._profiler_addsegment.stop() 

        # print(f"MAXL: popped new queue item on, to {p_end} from {p_start}")
        # print(f"MAXL: popped new queue item on, len {p_distance} at {vmax}")

        # we'll just do this whenever we add a new chunk... 
        # nevermind: we will do it only when we need to send a new chunk ... 
        if self.do_recalculations:
            self._profiler_replan.start()
            recalculate_queue(self.queue, self.junction_deviation, self.max_accels)
            self._profiler_replan.stop() 
