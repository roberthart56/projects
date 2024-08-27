import numpy as np 
from scipy.optimize import minimize 

# WARNING: GPT code, danger close 

def quartic_bezier(t, params):
    p0, p1, p2, p3, p4 = params 

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    uuuu = uuu * u
    tttt = ttt * t

    p = (uuuu * p0) + (4 * uuu * t * p1) + (6 * uu * tt * p2) + (4 * u * ttt * p3) + (tttt * p4)

    return p

def quartic_bezier_dot(t, params):
    p0, p1, p2, p3, p4 = params 

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u

    d = (4 * uuu * (p1 - p0)) + (12 * uu * t * (p2 - p1)) + (12 * u * tt * (p3 - p2)) + (4 * tt * t * (p4 - p3))

    return d 

def quartic_bezier_ddot(t, params):
    p0, p1, p2, p3, p4 = params 

    u = 1 - t
    tt = t * t
    uu = u * u

    dd = (12 * uu * (p2 - 2 * p1 + p0)) + (24 * u * t * (p3 - 2 * p2 + p1)) + (12 * tt * (p4 - 2 * p3 + p2))
    
    return dd


def do_fit_quartic(posns):
    fit_posn = posns
    fit_times = np.linspace(0, 1, len(posns))

    def bz_quart_err_func(params):
        total_err = 0

        params = [0, params[0], params[1], params[2], 1.0]

        for t in range(len(fit_times)):
            bz_pt = quartic_bezier(fit_times[t], params)
            total_err += (bz_pt - fit_posn[t]) ** 2

        return total_err

    res = minimize(bz_quart_err_func, [0.25, 0.5, 0.75])
    
    opt_params = [0, res.x[0], res.x[1], res.x[2], 1.0]
    
    return opt_params