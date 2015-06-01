__author__ = 'rfsheffer'


class Vec3:
    def __init__(self, x = 0, y = 0, z = 0):
        """
        :param x: X coordinate
        :param y: Y coordinate
        :param z: Z coordinate
        """
        self.x = x
        self.y = y
        self.z = z

    def __cmp__(self, other):
        return other.x == self.x and other.y == self.y and other.z == self.z

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise Exception('out of range!')

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise Exception('out of range!')

    def vecMA(self, scale, toward):
        """
        Adds a scaled normalized vector to self
        :param scale: The distance
        :param toward: The direction vector (normalized vector)
        """
        self.x += scale * toward.x
        self.y += scale * toward.y
        self.z += scale * toward.z

    def compare(self, other, equal_epsilon = 0.001):
        """
        A vector comparison within an epsilon
        :param other: The other vector to compare self against
        :param equal_epsilon: The variance
        :return: True if vectors are equal within an epsilon delta
        """
        for i in range(0, 3):
            if math.fabs(self[i] - other[i]) > equal_epsilon:
                return False

        return True

    def normalize(self):
        """
        Normalize self so length is equal to 1
        """
        length = 0.0
        for i in range(0, 3):
            length += self[i] * self[i]
        length = math.sqrt(length)
        if length == 0:
            return 0.0

        for i in range(0, 3):
            self[i] /= length

        return length

    def scale(self, scale):
        self.x *= scale
        self.y *= scale
        self.z *= scale


'''
Old School C style Vector manipulation functions
'''
def VectorMA(va, scale, vb, vc):
    vc[0] = va[0] + scale * vb[0]
    vc[1] = va[1] + scale * vb[1]
    vc[2] = va[2] + scale * vb[2]


def DotProduct(x, y):
    return (x[0] * y[0] + x[1] * y[1] + x[2] * y[2])


def CrossProduct(v1, v2, cross):
    cross[0] = v1[1] * v2[2] - v1[2] * v2[1]
    cross[1] = v1[2] * v2[0] - v1[0] * v2[2]
    cross[2] = v1[0] * v2[1] - v1[1] * v2[0]


def VectorCompare (v1, v2, equal_epsilon = 0.001):
    for i in range(0, 3):
        if math.fabs(v1[i] - v2[i]) > equal_epsilon:
            return False

    return True


def VectorNormalize(v):
    length = 0.0
    for i in range(0, 3):
        length += v[i] * v[i]
    length = math.sqrt(length)
    if length == 0:
        return 0.0

    for i in range(0, 3):
        v[i] /= length

    return length


def VectorScale(v, scale, out):
    out[0] = v[0] * scale
    out[1] = v[1] * scale
    out[2] = v[2] * scale


def VectorSubtract(a, b, c):
    c[0] = a[0] - b[0]
    c[1] = a[1] - b[1]
    c[2] = a[2] - b[2]


def VectorAdd(a, b, c):
    c[0] = a[0] + b[0]
    c[1] = a[1] + b[1]
    c[2] = a[2] + b[2]


def VectorCopy(a, b):
    b[0] = a[0]
    b[1] = a[1]
    b[2] = a[2]

def VectorLerp(v1, v2, t, out):
    out[0] = v1[0] + (v2[0] - v1[0]) * t
    out[1] = v1[1] + (v2[1] - v1[1]) * t
    out[2] = v1[2] + (v2[2] - v1[2]) * t
