import numpy as np 

# s/o to https://www.johndcook.com/blog/2023/08/27/intersect-circles/ 

def intersect_circles(x0, y0, r0, x1, y1, r1):
    c0 = np.array([x0, y0])
    c1 = np.array([x1, y1])
    v = c1 - c0
    d = np.linalg.norm(v)

    if d > r0 + r1 or d == 0:
        return None, None
    
    u = v/np.linalg.norm(v)
    xvec = c0 + (d**2 - r1**2 + r0**2)*u/(2*d)

    uperp = np.array([u[1], -u[0]])
    a = ((-d+r1-r0)*(-d-r1+r0)*(-d+r1+r0)*(d+r1+r0))**0.5/d
    return (xvec + a*uperp/2, xvec - a*uperp/2)
