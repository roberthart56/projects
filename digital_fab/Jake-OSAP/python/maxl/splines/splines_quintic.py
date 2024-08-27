import numpy as np 
from scipy.optimize import minimize 

def quintic_bezier(t, params):
    p0, p1, p2, p3, p4, p5 = params

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    uuuu = uuu * u
    tttt = ttt * t
    uuuuu = uuuu * u
    ttttt = tttt * t

    p = (uuuuu * p0) + (5 * uuuu * t * p1) + (10 * uuu * tt * p2) + (10 * uu * ttt * p3) + (5 * u * tttt * p4) + (ttttt * p5)

    return p

def quintic_bezier_dot(t, params):
    p0, p1, p2, p3, p4, p5 = params

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    uuuu = uuu * u

    d = (5 * uuuu * (p1 - p0)) + (20 * uuu * t * (p2 - p1)) + (30 * uu * tt * (p3 - p2)) + (20 * u * ttt * (p4 - p3)) + (5 * tt * tt * (p5 - p4))

    return d

def quintic_bezier_ddot(t, params):
    p0, p1, p2, p3, p4, p5 = params

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u

    dd = (20 * uuu * (p2 - 2 * p1 + p0)) + (60 * uu * t * (p3 - 2 * p2 + p1)) + (60 * u * tt * (p4 - 2 * p3 + p2)) + (20 * tt * t * (p5 - 2 * p4 + p3))
    
    return dd

def do_fit_quintic(posns):
    fit_posn = posns
    fit_times = np.linspace(0, 1, len(posns))

    def bz_quint_err_func(params):
        total_err = 0

        params = [0, params[0], params[1], params[2], params[3], 1.0]

        for t in range(len(fit_times)):
            bz_pt = quintic_bezier(fit_times[t], params)
            total_err += (bz_pt - fit_posn[t]) ** 2

        return total_err

    res = minimize(bz_quint_err_func, [0.2, 0.4, 0.6, 0.8])
    
    opt_params = [0, res.x[0], res.x[1], res.x[2], res.x[3], 1.0]
    
    return opt_params