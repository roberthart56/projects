import numpy as np 
from scipy.optimize import minimize 

def cubic_bezier(t, params):
    p0, p1, p2, p3 = params 

    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t

    p = (uuu * p0) + (3 * uu * t * p1) + (3 * u * tt * p2) + (ttt * p3)

    return p

def cubic_bezier_dot(t, params):
    p0, p1, p2, p3 = params 

    u = 1 - t
    tt = t * t
    uu = u * u

    d = 3 * uu * (p1 - p0) + 6 * u * t * (p2 - p1) + 3 * tt * (p3 - p2) 

    return d 

def cubic_bezier_ddot(t, params):
    p0, p1, p2, p3 = params 

    u = 1 - t

    dd = 6 * u * (p2 - 2 * p1 - p0) + 6 * t * (p3 - 2 * p2 - p1)
    
    return dd 

def do_fit_cubic(posns):
    fit_posn = posns
    fit_times = np.linspace(0, 1, len(posns))

    def bz_err_func(params):
        total_err = 0

        params = [0, params[0], params[1], 1.0]
        # params = [params[0], params[1], params[2], params[3]]

        for t in range(len(fit_times)):
            bz_pt = cubic_bezier(fit_times[t], params)
            total_err += (bz_pt - fit_posn[t]) ** 2

        return total_err

    res = minimize(bz_err_func, [0.25, 0.75])
    # res = minimize(bz_err_func, [0, 0.25, 0.75, 1])
    # print(res.x)
    
    opt_params = [0, res.x[0], res.x[1], 1.0]
    
    return opt_params


