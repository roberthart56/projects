import numpy as np 

# position 
def cubic_basis(t, params):
    p0, p1, p2, p3 = params 

    tt = t * t 
    ttt = tt * t 

    a = p0 + 4 * p1 + p2 
    b = - 3 * p0 + 3 * p2
    c = 3 * p0 - 6 * p1 + 3 * p2
    d = - p0 + 3 * p1 - 3 * p2 + p3

    return 1/6 * (a + b * t + c * tt + d * ttt)

# velocity 
def cubic_basis_dot(t, params):
    p0, p1, p2, p3 = params 

    tt = t * t 

    # a = p0 + 4 * p1 + p2 
    b = - 3 * p0 + 3 * p2
    c = 3 * p0 - 6 * p1 + 3 * p2
    d = - p0 + 3 * p1 - 3 * p2 + p3

    return 1/6 * (b + c * 2 * t + d * 3 * tt)

# acceleration 
def cubic_basis_ddot(t, params):
    p0, p1, p2, p3 = params 

    # a = p0 + 4 * p1 + p2 
    # b = - 3 * p0 + 3 * p2
    c = 3 * p0 - 6 * p1 + 3 * p2
    d = - p0 + 3 * p1 - 3 * p2 + p3

    return 1/6 * (c * 2 + d * 6 * t)

# jerk 
def cubic_basis_dddot(t, params):
    p0, p1, p2, p3 = params 

    # a = p0 + 4 * p1 + p2 
    # b = - 3 * p0 + 3 * p2
    # c = 3 * p0 - 6 * p1 + 3 * p2
    d = - p0 + 3 * p1 - 3 * p2 + p3

    return 1/6 * (d * 6)