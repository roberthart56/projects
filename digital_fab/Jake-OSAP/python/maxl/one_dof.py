import asyncio 
from dataclasses import dataclass 
from collections import deque 
from typing import Callable, Awaitable, Tuple, Deque 

import numpy as np 

from .types import MAXLInterpolationIntervals
from .queue_planner_functional import MAXLQueueSegment 
from .core import get_states_from_spline_pts 

@dataclass 
class MAXLOneDOFConfig:
    interpolation_interval: MAXLInterpolationIntervals
    twin_to_real_gap_ms: int 
    history_length_ms: int 
    max_accel: float 
    max_vel: float 

@dataclass 
class MAXLOneDOFControlPoint:
    time_us: int 
    position: float 

class MAXLOneDOF:
    def __init__(self, config: MAXLOneDOFConfig):

        self.interpolation_interval_us = config.interpolation_interval.value[0]
        self.twin_to_real_gap_us = config.twin_to_real_gap_ms * 1000
        self.history_length_us = config.history_length_ms * 1000 

        num_ctrl_pts_in_time_gap = int(np.floor(self.twin_to_real_gap_us / self.interpolation_interval_us))
        num_ctrl_pts_in_history = int(np.ceil(self.history_length_us / self.interpolation_interval_us))

        # our pts are simpler, just time, pos... 
        self._control_points: Deque[MAXLOneDOFControlPoint] = deque(maxlen = num_ctrl_pts_in_time_gap + num_ctrl_pts_in_history)

        self.max_accel = config.max_accel 
        self.max_vel = config.max_vel 
        self._position = 0 
        self._velocity = 0 
        self._velocity_target = 0 
        self._most_recent_timestamp = 0 
        # self._prior_adhoc_stamp = 0 
        self._segment: MAXLQueueSegment | None = None 


    def on_time_step(self, time: int, offset: float):
        self._most_recent_timestamp = time 

        # positional control 
        if self._segment is not None:
            if self._segment.end_time() < time:
                self._position = self._segment.p_end[0] 
                self._segment = None 
            else: 
                # segments render time 0 - t_end, not w/r/t global time 
                self._position = self._segment.states_at_time(time - self._segment.t_start_us).pos[0] 

        # velocity control
        else:
            if self._velocity < self._velocity_target:
                accel = self.max_accel
            elif self._velocity > self._velocity_target:
                accel = - self.max_accel
            else:
                accel = 0 

            # integrate velocity (interval is microseconds)
            self._velocity += accel * (self.interpolation_interval_us / 1000000)
            # check for overshoots 
            if accel > 0 and self._velocity > self._velocity_target:
                self._velocity = self._velocity_target 
            elif accel < 0 and self._velocity < self._velocity_target:
                self._velocity = self._velocity_target 
            # integrate positions, 
            self._position += self._velocity * (self.interpolation_interval_us / 1000000)                             

        # stash it all, deque auto deletes from the tail, 
        self._control_points.append(MAXLOneDOFControlPoint(time, self._position))

        return offset + self._position 
    

    def goto_velocity(self, velocity: float):
        self._velocity_target = np.clip(velocity, - self.max_vel, self.max_vel)


    async def halt(self, velocity_epsilon = 0.001):
        self.goto_velocity(0)
        while True:
            if np.abs(self._velocity_target - self._velocity) <= velocity_epsilon:
                return 
            else:
                interval = self.interpolation_interval_us / 100000
                await asyncio.sleep(interval)


    async def goto_position(self, position: float):
        # we should be able to use a little trapezoid to do this... 
        if self._velocity != 0:
            # I'm pretty sure this can be made to work just fine, but we need to set `vi` - 
            # the only thing that I would hope to test would be that negative vi (or vf ?) work 
            # with the simple trapezoidal model... it seems as though they should, but IDK for sure 
            raise ValueError(f"you called goto_position on this OneDOF while it was in motion, IDK how robust it is to that")

        if position < self._position:
            unit = -1 
        else:
            unit = 1 

        seg = MAXLQueueSegment(
            p_end = np.array([position]),
            p_start = np.array([self._position]),
            inertial_axes_count = 0,
            target_vel = self.max_vel, 
            unit = np.array([unit]),
            distance = np.abs(self._position - position),
            accel = self.max_accel, 
            vmax = self.max_vel, 
            inertial_unit = np.array([]),
            inertial_distance = 0, 
            vi = 0, vf = 0,
            t_start_us =  self._most_recent_timestamp 
        )
        self._segment = seg 
        ### uuuh, actually that's it now though:
        print(f"MAXL OneDOF: to goto {position:.3f} from {self._position:.3f}, seg should run from {self._most_recent_timestamp} to {seg.end_time()}")
        # then hangup until that is done, 
        while True:
            if self._segment is None:
                await asyncio.sleep(self.twin_to_real_gap_us / 1000000)
                return 
            else:
                await asyncio.sleep(0.01)

    async def goto_position_relative(self, delta: float):
        await self.goto_position(self._position + delta)

    
    def get_states_at_time(self, time_us: int):
        # index of the *most recently passed* control point, 
        index = next((i for i, pt in enumerate(self._control_points) if (pt.time_us < time_us and time_us < (pt.time_us + self.interpolation_interval_us))), None)
        if index is None:
            oldest_pt_time = self._control_points[0].time
            newest_pt_time = self._control_points[-1].time
            raise Exception(F"MAXL couldn't find any control points around {time_us}, history spans {oldest_pt_time} ... {newest_pt_time}")
        
        if index < 0 or (index + 2) > len(self._control_points):
            oldest_pt_time = self._control_points[0].time
            newest_pt_time = self._control_points[-1].time
            raise Exception(F"MAXL doesn't have enough local history around {time_us} to resolve states, history spans {oldest_pt_time} ... {newest_pt_time}, {index} of {len(self._control_points)}")

        local_pts = [
            self._control_points[index - 1].position,
            self._control_points[index].position,
            self._control_points[index + 1].position,
            self._control_points[index + 2].position
        ]

        t1 = self._control_points[index].time_us

        return get_states_from_spline_pts(*local_pts, t1, time_us, self.interpolation_interval_us)

    # rate is direction-and-rate, backoff = abs(backoff) 
    async def home(self, switch: Callable[[], Awaitable[Tuple[int, bool]]], rate: float, backoff: float):
        backoff = abs(backoff)
        if rate > 0:
            backoff = -backoff 

        time, limit = await switch()

        if limit:
            await self.goto_position_relative(backoff * 1.5)
            await asyncio.sleep(0.25)

        self.goto_velocity(rate) 

        while True:
            time, limit = await switch()
            if limit:
                # get our posn wherence we were whence the switch doth hit 
                states = self.get_states_at_time(time)
                pos_at_hit = states[0] 
                print(F"whack at {pos_at_hit}, now halt!")
                await self.halt()
                break 
            else: 
                await asyncio.sleep(0)

        await self.goto_position(pos_at_hit + backoff)
        # await self.goto_position_relative(backoff) 
