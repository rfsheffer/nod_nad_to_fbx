__author__ = 'rsheffer'

import struct


def read_bytes_reversed(fp, num):
    _bytes = fp.read(num)
    return ''.join(reversed(_bytes))  # reverse for little endian (intel)


def read_int(fp):
    return struct.unpack('>i', read_bytes_reversed(fp, 4))[0]

def read_unsigned_int(fp):
    return struct.unpack('>I', read_bytes_reversed(fp, 4))[0]

def read_short(fp):
    return struct.unpack('>h', read_bytes_reversed(fp, 2))[0]

def read_unsigned_short(fp):
    return struct.unpack('>H', read_bytes_reversed(fp, 2))[0]

def read_byte(fp):
    return struct.unpack('>b', read_bytes_reversed(fp, 1))[0]

def read_unsigned_byte(fp):
    return struct.unpack('>B', read_bytes_reversed(fp, 1))[0]

def read_float(fp):
    return struct.unpack('>f', read_bytes_reversed(fp, 4))[0]


def read_string(fp, num):
    """
    Reads a string from the file up to a number of bytes, and strips the trailing zeros
    """
    str_bytes = ''.join(fp.read(num))

    for i in range(0, num):
        if str_bytes[i] == '\0':
            str_bytes = str_bytes[0:i]
            break

    return str_bytes
