import numpy as np 
from numba import jit

@jit(nopython=True)
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

@jit(nopython=True)
def is_intersecting(p1, p2, q1, q2):
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

@jit(nopython=True)
def det(a, b):
    return a[0] * b[1] - a[1] * b[0]

@jit(nopython=True)
def line_intersection(p1, p2, q1, q2):
    x_diff = (p1[0] - p2[0], q1[0] - q2[0])
    y_diff = (p1[1] - p2[1], q1[1] - q2[1])

    div = det(x_diff, y_diff)
    if div == 0:
        return (np.nan, np.nan)  # Return invalid point if lines are parallel or collinear

    d = (det(p1, p2), det(q1, q2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return x, y

@jit(nopython=True)
def parameter_on_segment(p, q1, q2):
    if q2[0] != q1[0]:  # If x-coordinates are not the same
        return (p[0] - q1[0]) / (q2[0] - q1[0])
    else:  # If x-coordinates are the same, use y-coordinates
        return (p[1] - q1[1]) / (q2[1] - q1[1])

@jit(nopython=True)
def find_intersection(a_x, a_y, b_x, b_y):
    for i in range(len(a_x) - 1):
        p1 = (a_x[i], a_y[i])
        p2 = (a_x[i + 1], a_y[i + 1])

        for j in range(len(b_x) - 1):
            q1 = (b_x[j], b_y[j])
            q2 = (b_x[j + 1], b_y[j + 1])

            if is_intersecting(p1, p2, q1, q2):
                intersection = line_intersection(p1, p2, q1, q2)
                if not np.isnan(intersection[0]) and not np.isnan(intersection[1]):
                    p_a = parameter_on_segment(intersection, p1, p2)
                    p_b = parameter_on_segment(intersection, q1, q2)
                    return i, j, p_a, p_b
    return -1, -1, np.nan, np.nan  # Return invalid indices and NaNs if no intersection

# Example usage
# a_x = np.array([0, 1, 2, 3], dtype=np.float64)
# a_y = np.array([0, 1, 0, -1], dtype=np.float64)
# b_x = np.array([0, 1, 2, 3], dtype=np.float64)
# b_y = np.array([1, 0, -1, -2], dtype=np.float64)

# result = find_intersection(a_x, a_y, b_x, b_y)
# print(result)


class TorqueLikeSegmentSolver:
    def __init__(self, max_static_accel, max_steadystate_velocity, target_velocity, time_step = 0.001):
        self.max_accel = max_static_accel 
        self.max_velocity = max_steadystate_velocity 
        self.target_velocity = target_velocity 

        self.time_step = time_step 

        self._velocity = 0 
        self._position = 0 

        # initializing these ahead-of the .solve call, 
        self._fwds_times = np.arange(0, 10, self.time_step)
        self._fwds_velos = np.zeros(self._fwds_times.shape)
        self._fwds_posns = np.zeros(self._fwds_times.shape)

        self._rev_times = np.arange(-10, 0, self.time_step)
        self._rev_velos = np.zeros(self._rev_times.shape)
        self._rev_posns = np.zeros(self._rev_times.shape)

    # this thing approximates a linear torque curve a-la: 
    #  `.   |
    #     `.|
    #       |`.  < max_static_accel  (at zero velocity, -ves will be bigger) 
    #       |   `.
    #       |      `.
    # ------|---------x---
    #                  ^ max_steadystate_velocity 
    # these are not perfect, but do much better than simple "max_accel, max_v" trapezoids, 
    # the linear plot in accel-vs-v leads to segments with curvature in the accel-vs-t plot,
    # which can be fit perfectly with a quartic spline (!) 

    def get_min_max_accel(self, velocity: float):
        if velocity < 0:
            span = velocity / self.max_velocity 
            return - (1 + span) * self.max_accel, (1 - span) * self.max_accel # self.max_accel 
        else:
            span = velocity / self.max_velocity 
            return - (1 + span) * self.max_accel, (1 - span) * self.max_accel
        
    def set_states(self, position: float, velocity: float):
        self._position = position 
        self._velocity = velocity

    # returns position, velocity 
    def get_states(self):
        return self._position, self._velocity
    
    # TODO: integrate with RK4 if perf is punishing 
    # effort: float [-1, 1]
    def integrate(self, effort: float, time_step: float):
        effort = np.clip(effort, -1, 1)
        min_accel, max_accel = self.get_min_max_accel(self._velocity)

        effort_span = (effort + 1) / 2

        self._accel = min_accel + effort_span * (max_accel - min_accel) 

        self._velocity += self._accel * time_step 

        # a bit of a quick-hack, we only do this going fwds, 
        # so that reversals can intersect (!) 
        if time_step > 0:
            if self._velocity > self.target_velocity:
                self._velocity = self.target_velocity 

        self._position += self._velocity * time_step 

        return self._velocity, self._position 
    
    # solve from initial pos, vel to final pos, vel, 
    def solve(self, p_i, v_i, p_f, v_f):
        # all solved in +ve land, 
        if p_i < 0 or v_i < 0 or p_f < 0 or v_f < 0:
            raise ValueError("TorqueLikeSegmentSolver lives in +ve plane only for now!")

        # (1) integrate forwards .. 
        # 10s is a guess at maximum segment time, this will probably cause an error soon 
        # TODO: initialize these once, not on every solve, if perf is punishing (and re-solving common)
        fwds_max_vel = 0 
        fwds_i = 0 

        self.set_states(p_i, v_i) 

        # TODO: could we hit this with some numba ?
        for i in range(len(self._fwds_times)): #, t in enumerate(self._fwds_times):
            self._fwds_velos[i], self._fwds_posns[i] = self.integrate(1, self.time_step)
            if self._fwds_posns[i] >= p_f:
                fwds_max_vel = self._fwds_velos[i] 
                fwds_i = i 
                # print(f"fwds: {fwds_i}")
                break 

        if fwds_i == 0:
            raise Exception("TLSS failed to hit final position after 10s integration.")

        # (2) integrate backwards 
        rev_i = 0 

        self.set_states(p_f, v_f)

        for i in range(len(self._rev_times)): #, t in enumerate(self._rev_times):
            self._rev_velos[i], self._rev_posns[i] = self.integrate(-1, - self.time_step) 
            # warning that 0.1 maybe not big enough surplus here 
            # to cross with fwds pass (esp. if mm/sec) 
            if self._rev_velos[i] > fwds_max_vel + 0.1:
                rev_i = i 
                # print(f"rev: {rev_i}")
                break 

        if rev_i == 0:
            raise Exception("TLSS failed to hit fwds_max_vel while backing up")

        # flip, TODO: could probably figure how to not-flip, for perf ? 
        rev_posns = self._rev_posns[:rev_i][::-1]
        rev_times = self._rev_times[:rev_i][::-1]
        rev_velos = self._rev_velos[:rev_i][::-1]

        # (3) cross 'em, 
        i, j, p_a, p_b = find_intersection(rev_posns, rev_velos, self._fwds_posns, self._fwds_velos)
        exact_forwards_time = self._fwds_times[j] + self.time_step * p_b 
        exact_stopping_time = 10 + rev_times[i] - self.time_step * p_a 
        exact_total_time = exact_forwards_time + exact_stopping_time

        # actually not totally sure what returns we'll need, 
        return exact_forwards_time, exact_stopping_time 

        # return rev_times[i - 1], self._fwds_times[i - 1] 


    def solve_max_vf(self, p_i, v_i, p_f):
        pass 

    def solve_max_vi(self, p_i, p_f, v_f):
        pass 