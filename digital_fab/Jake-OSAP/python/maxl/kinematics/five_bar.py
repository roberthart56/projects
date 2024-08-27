from typing import List 
from dataclasses import dataclass 
import numpy as np 
from .intersect_circles import intersect_circles

# makes the assumption that the mechanism is 'hanging'
# i.e the two a (left) b (right), 
# theta-zero is 'down' - i.e. zero axis is along the y... -1 
class FiveBar:
    def __init__(self, a_xy, b_xy, len_a1, len_a2, len_b1, len_b2):
        self.a_xy = np.array(a_xy)
        self.b_xy = np.array(b_xy)
        self.len_a1 = len_a1 
        self.len_a2 = len_a2
        self.len_b1 = len_b1 
        self.len_b2 = len_b2 

    def actu_to_cart(self, actu):
        # calculate position of ai
        # ... using right-hand rule, so i.e. theta_a 
        # is probably negative most of the time, 
        pos_ai = [
            self.a_xy[0] + self.len_a1 * np.sin(actu[0]),
            self.a_xy[1] + self.len_a1 * np.cos(actu[0])
        ]

        pos_bi = [
            self.b_xy[0] + self.len_b1 * np.sin(actu[1]),
            self.b_xy[1] + self.len_b1 * np.cos(actu[1])
        ]
  
        # for intersections of two circles, 
        inter_a, inter_b = intersect_circles(*pos_ai, self.len_a2, *pos_bi, self.len_b2)

        # it's possible that this is impossible, or at the intersecting singularity
        if inter_a is None:
            raise Exception("bonkers proposal")

        # otherwise we are... picking two points - in our case it will be the one
        # with the most negative y value... 
        intersection = inter_a if inter_a[1] < inter_b[1] else inter_b 

        return intersection 

    def cart_to_actu(self, cart):
        # so, yeah, we intersect... 
        inter_a, inter_b = intersect_circles(cart[0], cart[1], self.len_a2, *self.a_xy, self.len_a1)
        if inter_a is None:
            raise Exception(F"5B a: {cart} ... req'd cart posns are out of reach ?")

        # this will be the left-most of the two, 
        inter_left = inter_a if inter_a[0] < inter_b[0] else inter_b 

        # flipped on the right side, 
        inter_a, inter_b = intersect_circles(cart[0], cart[1], self.len_b2, *self.b_xy, self.len_b1)
        if inter_a is None:
            raise Exception(F"5B b: {cart} ... req'd cart posns are out of reach ?")

        inter_right = inter_a if inter_a[0] > inter_b[0] else inter_b 

        # then we can go posn's to angles, 
        theta_a = np.arcsin((inter_left[0] - self.a_xy[0]) / self.len_a1)
        theta_b = np.arcsin((inter_right[0] - self.b_xy[0]) / self.len_b1)

        # rads to degs babey 
        theta_a = np.rad2deg(theta_a)
        theta_b = np.rad2deg(theta_b)

        return [theta_a, theta_b]
