__author__ = 'rfsheffer'

from vector import *

def hermite_spline(p1, p2, d1, d2, t):
    """
    Basic hermite spine
    :param p1: Vec3 of first point
    :param p2: Vec3 of second point
    :param d1: Vec3 of tangent 1
    :param d2: Vec3 of tangent 2
    :param t: time between 0.0 and 1.0 where t = 0.0 = p1 and t = 1.0 = p2
    :return: The output vector of the point between p1 and p2 at time t
    """
    sqr = t * t
    cube = t * sqr

    b1 = 2.0 * cube - 3.0 * sqr + 1.0
    b2 = 1.0 - b1
    b3 = cube - 2 * sqr + t
    b4 = cube - sqr

    output = Vec3()
    VectorScale(p1, b1, output)

    VectorMA(output, b2, p2, output)
    VectorMA(output, b3, d1, output)
    VectorMA(output, b4, d2, output)

    return output
