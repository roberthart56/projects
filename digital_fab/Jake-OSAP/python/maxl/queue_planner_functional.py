import numpy as np 
import numpy.typing as npt 
from dataclasses import dataclass, field 
from typing import List 

@dataclass 
class MAXLTrajectoryStates:
    pos: npt.NDArray
    direction: npt.NDArray
    v: float 
    a: float 


@dataclass
class MAXLQueueBlock:
    p_start: npt.NDArray 
    unit: npt.NDArray
    vi: float 
    accel: float 
    t_total: float 


@dataclass 
class MAXLQueueSegment:
    p_end: npt.NDArray
    p_start: npt.NDArray
    inertial_axes_count: int 
    target_vel: float 
    # cached after add_segment, 
    unit: npt.NDArray 
    distance: float
    accel: float
    vmax: float 
    # inertia-only axes, 
    inertial_unit: npt.NDArray
    inertial_distance: float 
    # unconstrained / planned, 
    vi: float = 0 
    vf: float = 0 
    # it should be that if we have a start_time, 
    # we are moving or have been transmitted... 
    # / we are locked 
    blocks: List[MAXLQueueBlock] = field(default_factory = list)
    t_start_us: int = 0 

    def end_time(self):
        if self.t_start_us == 0:
            raise ValueError("MAXL: ERROR: shouldn't be calculating end_time with no t_start_us")

        if len(self.blocks) == 0:
            make_blocks(self)

        seg_time = 0 
        for block in self.blocks:
            seg_time += block.t_total 

        # blocks render time in floating point seconds, 
        # here we are resolving integer microseconds - 
        return self.t_start_us + int(seg_time * 1000000)

    # time_us in microseconds from the start of the block... 
    def states_at_time(self, time_us: int):
        if len(self.blocks) == 0:
            make_blocks(self)

        # blocks render in floating point seconds 
        time = time_us / 1000000

        for block in self.blocks:
            if time > block.t_total:
                time -= block.t_total
                continue 
            if time < block.t_total:
                # print("interval, accel ", interval, block.accel)
                dist_travelled = block.vi * time + (block.accel * np.power(time, 2) / 2)
                pos = block.p_start + block.unit * dist_travelled
                direction = block.unit
                v = block.vi + block.accel * time
                a = block.accel 

                return MAXLTrajectoryStates(pos, direction, v, a)
  
        return None 


def recalculate_queue(queue: List[MAXLQueueSegment], junction_deviation: float, max_accels: npt.NDArray):
    # print("----- recalculating")
    # fwds, reverse pass, junctions...

    # --------------------------------------- 1: max junction velocities w/ jd 
    # print("\n----- jd pass")
    for i in range(len(queue) - 1):
        curr_seg = queue[i]
        next_seg = queue[i + 1]
        # if both segments have motion on real axes, we can do jd (and will need to clip units)
        # otherwise we should do... minimum velocity action as linkage 
        if curr_seg.inertial_distance == 0 or next_seg.inertial_distance == 0:
            # segments with zero inertial distance should have vi, vf == 0 ? 
            # TODO: maybe we can deploy some heuristic here so that we aren't crash stopping 
            # every gd retract... 
            # TODO: use a better heuristic than '2' haha 
            pit_speed = np.min([3, curr_seg.vmax, next_seg.vmax])
            curr_seg.vf = pit_speed
            next_seg.vi = pit_speed 
        else: 
            # incoming and outgoing axes have real motion, do JD 
            # angle betwixt, 
            dot_prod = np.clip(np.dot(curr_seg.inertial_unit, next_seg.inertial_unit), -1.0, 1.0)
            rads_between = np.arccos(dot_prod)
            # radius of arc, given jd:
            # w/ note that 0-angle moves (straight lines) would produce infinite radii, so we clip 
            jd_radius = junction_deviation / (1 - np.cos(max(0.001, rads_between) / 2))
            # now, for angular acceleration, we have a = v^2/r where v is our linear speed, 
            # so we could work out, given a max accel, what our v should be: v = sqrt(a*r)
            # but we need a limiting accel... we have three accel limits but only one will 
            # be limiting... 

            # so, the cross product of our two units is going to be perpendicular, it's the 
            # axis that we are rotating around:
            perp_vect = np.cross(curr_seg.inertial_unit, next_seg.inertial_unit)
            perp_norm = np.linalg.norm(perp_vect)

            # pick an accel, 
            jd_accel = 0 
            # use minimum when we have two-dof (producing scalars) or where 
            # the 180' turnaround produces nan since vectors are parallel, 
            if perp_vect.size == 1:
                jd_accel = np.min(max_accels)
            elif perp_norm == 0.0:
                jd_accel = np.min(max_accels)
            else:
                # otherwise we use the vector that is perpendicular to our corner to determine 
                # which axes are dominating in acceleration thru this arc (we use its compliment)
                perp_vect_unit = perp_vect * (1 / perp_norm)
                complimentary_perp = np.ones(len(max_accels[:curr_seg.inertial_axes_count])) - np.abs(perp_vect_unit)
                # where the biggest is the axis that this move is "mostly happening on", 0's are axes 
                # we don't accel thru at all, etc, so we can pick and accel like:
                # rm all zeroes, 
                jd_accel = np.min((1 / complimentary_perp[complimentary_perp != 0]) * np.asarray(max_accels[:curr_seg.inertial_axes_count])[complimentary_perp != 0])

            # now with an acceleration and radius of our "junction" we can select a maximum velocity 
            # to make along this arc.
            # todo would be to add a genuine arc in here... but perhaps better done with even more generic 
            # spline fitting step... 
            jd_velocity = np.sqrt(jd_accel * jd_radius)

            # junction velocity also cannot be any greater than the surrounding vmaxes 
            jd_velocity = np.min([jd_velocity, curr_seg.vmax, next_seg.vmax])

            # this is our first set of vi / vf values, we stash 'em, 
            curr_seg.vf = jd_velocity 
            next_seg.vi = jd_velocity 

            # print("---     seg:")
            # print("       this: ", curr_seg.unit)
            # print("       next: ", next_seg.unit, rads_between, jd_radius)
            # print("       perp: ", perp_vect)
            # print("       proj: ", complimentary_perp)
            # print("  accs, rad: ", jd_accel, jd_radius)
            # print("jd_velocity: ", jd_velocity)

    # --------------------------------------- 2: forwards pass 
    # print("\n----- fwds pass")
    for i in range(len(queue) - 1):
        curr_seg = queue[i]
        next_seg = queue[i + 1]

        # to see what our *max* final velocity would be (if we were to do max accel during this period)
        # we use use v_f^2 = v_i^2 + 2ad, 
        vf_max = np.sqrt(np.power(curr_seg.vi, 2) + 2 * curr_seg.accel * curr_seg.distance)
        
        # if our current end-velocity is larger than this max, pinch it, 
        if curr_seg.vf > vf_max:
            curr_seg.vf = vf_max 
            next_seg.vi = vf_max 


        # print("---     seg:")
        # print("  vi, accel: ", curr_seg.vi, curr_seg.accel)
        # print("     vf_max: ", vf_max)

    # --------------------------------------- 3: reverse pass 
    # print("\n----- rev pass")
    for i in range(len(queue) - 1):
        curr_seg = queue[len(queue) - i - 1]
        prev_seg = queue[len(queue) - i - 2]

        # to see what our *max* final velocity would be (if we were to max accel during this period)
        # we use use v_f^2 = v_i^2 + 2ad, 
        vi_max = np.sqrt(np.power(curr_seg.vf, 2) + 2 * curr_seg.accel * curr_seg.distance)

        # if we couldn't possibly deccel enough to meet this, pinch it 
        if curr_seg.vi > vi_max:
            curr_seg.vi = vi_max 
            prev_seg.vf = vi_max 

        # print("---     seg:")
        # print("  vi, accel: ", curr_seg.vi, curr_seg.accel)
        # print("     vi_max: ", vi_max)
        # print("         vf: ", curr_seg.vf)

    # --------------------------------------- 4: checkup pass 
    # print("\n----- check pass")
    for i in range(len(queue) - 1):
        curr_seg = queue[i]
        next_seg = queue[i + 1]
        # print("---     seg:")
        # print("         vi: ", curr_seg.vi)
        # print("       vmax: ", curr_seg.vmax)
        # print("         vf: ", curr_seg.vf)
        if curr_seg.vf != next_seg.vi:
            raise Exception("badness betwixt segments")

    # --------------------------------------- 5: reset blocks (for recalc once they're needed)
    for i in range(len(queue)):
        queue[i].blocks = [] 


def make_blocks(seg: MAXLQueueSegment) -> List[MAXLQueueBlock]:
    max_vi = np.sqrt(np.power(seg.vf, 2) + 2 * seg.accel * seg.distance)
    max_vf = np.sqrt(np.power(seg.vi, 2) + 2 * seg.accel * seg.distance)

    if max_vf <= seg.vf:
        # seg is /
        seg.blocks = [MAXLQueueBlock(
            p_start = seg.p_start,
            unit = seg.unit,
            vi = seg.vi, 
            accel = seg.accel, 
            t_total = seg.distance / ((seg.vi + seg.vf) / 2)
        )]
    elif max_vi <= seg.vi:
        # seg is \ 
        seg.blocks = [MAXLQueueBlock(
            p_start = seg.p_start,
            unit = seg.unit,
            vi = seg.vi, 
            accel = - seg.accel,
            t_total = seg.distance / ((seg.vi + seg.vf) / 2)
        )]
    elif seg.vi == seg.vmax and seg.vi == seg.vf:
        # seg is --- 
        seg.blocks = [MAXLQueueBlock(
            p_start = seg.p_start,
            unit = seg.unit,
            vi = seg.vi,
            accel = 0,
            t_total =  seg.distance / seg.vmax
        )]
    elif seg.vi == seg.vmax:
        # seg is ---\ 
        deccel_dist = (np.power(seg.vmax, 2) - np.power(seg.vf, 2)) / (2 * seg.accel) 
        # we have to mint two segments, 
        seg.blocks = [MAXLQueueBlock(
            p_start = seg.p_start,
            unit = seg.unit,
            vi = seg.vi, 
            accel = 0,
            t_total = (seg.distance - deccel_dist) / seg.vmax
        ), MAXLQueueBlock(
            p_start = seg.p_start + seg.unit * (seg.distance - deccel_dist),
            unit = seg.unit, 
            vi = seg.vmax,
            accel = - seg.accel, 
            t_total = deccel_dist / ((seg.vmax + seg.vf) / 2)
        )]
    elif seg.vf == seg.vmax:
        # seg is /--- 
        accel_dist = (np.power(seg.vmax, 2) - np.power(seg.vi, 2)) / (2 * seg.accel)
        # two seggies 
        seg.blocks = [MAXLQueueBlock(
            p_start = seg.p_start,
            unit = seg.unit, 
            vi = seg.vi,
            accel = seg.accel,
            t_total = accel_dist / ((seg.vmax + seg.vi) / 2)
        ), MAXLQueueBlock(
            p_start = seg.p_start + seg.unit * (accel_dist),
            unit = seg.unit, 
            vi = seg.vmax,
            accel = 0, 
            t_total = (seg.distance - accel_dist) / seg.vmax 
        )]
    else:
        # seg is either /--\ or /\ 
        # vi^2 = vf^2 + 2ad 
        # (vi^2 - vf^2) / 2a = d
        accel_dist = (np.power(seg.vmax, 2) - np.power(seg.vi, 2)) / (2 * seg.accel)
        deccel_dist = (np.power(seg.vmax, 2) - np.power(seg.vf, 2)) / (2 * seg.accel)
        if accel_dist < 0 or deccel_dist < 0 or seg.accel < 0:
            print(seg)
            raise ValueError(f"-ves where there shouldn't be any... accel: {seg.accel}, a_dist: {accel_dist}, d_dist: {deccel_dist}")

        if accel_dist + deccel_dist >= seg.distance:
            # it's /\ ... we need to figure where the crossover is
            # (seg doesn't actually reach vmax) 
            # we know that we have this equality:
            # v_peak^2 = vi^2 + 2*a*accel_dist
            # v_peak^2 = vf^2 + 2*a*deccel_dist 
            # and total dist is the sum of the two, 
            # dist = accel_dist + deccel_dist 
            # let's try like 
            # vi^2 + 2*a*accel_dist = vf^2 + 2*a*(d - accel_dist)
            # vi^2 - vf^2 = 2*a*(d - accel_dist) - 2*a*accel_dist 
            # vi^2 - vf^2 = 2*a*d - 2*a*accel_dist - 2*a*accel_dist 
            # vi^2 - vf^2 = 2*a*(d - accel_dist - accel_dist)
            # (vi^2 - vf^2) / 2*a = d - 2*accel_dist
            # ((vi^2 - vf^2) / 2*a - d) / (- 2) = accel_dist
            accel_dist = ((np.power(seg.vi, 2) - np.power(seg.vf, 2)) / (2 * seg.accel) - seg.distance) / (- 2)
            if accel_dist < 0:
                raise ValueError("badness of less-than-zero accel phase for /\\ peaky blunder")
            deccel_dist = seg.distance - accel_dist 
            # print("/\\ vi, vf: ", seg.vi, seg.vf)
            # print("... ", accel_dist, deccel_dist)
            # and that the final accel_dist will be equal to deccel_dist, 
            # shit lol, `accel_dist = seg.dist / 2`
            v_max = np.sqrt(np.power(seg.vi, 2) + 2 * seg.accel * accel_dist)
            seg.blocks = [MAXLQueueBlock(
                p_start = seg.p_start,
                unit = seg.unit,
                vi = seg.vi,
                accel = seg.accel, 
                t_total = accel_dist / ((v_max + seg.vi) / 2)
            ), MAXLQueueBlock(
                p_start = seg.p_start + seg.unit * accel_dist, 
                unit = seg.unit, 
                vi = v_max, 
                accel = - seg.accel, 
                t_total = deccel_dist / ((v_max + seg.vf) / 2) 
            )]
        else:
            # the full trapezoid, /--\ 
            seg.blocks = [MAXLQueueBlock(
                p_start = seg.p_start,
                unit = seg.unit, 
                vi = seg.vi,
                accel = seg.accel, 
                t_total = accel_dist / ((seg.vi + seg.vmax) / 2)
            ), MAXLQueueBlock(
                p_start = seg.p_start + seg.unit * accel_dist,
                unit = seg.unit, 
                vi = seg.vmax,
                accel = 0,
                t_total = (seg.distance - accel_dist - deccel_dist) / seg.vmax 
            ), MAXLQueueBlock(
                p_start = seg.p_start + seg.unit * (seg.distance - deccel_dist),
                unit = seg.unit,
                vi = seg.vmax, 
                accel = - seg.accel,
                t_total = deccel_dist / ((seg.vmax + seg.vf) / 2) 
            )]