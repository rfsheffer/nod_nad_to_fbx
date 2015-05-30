__author__ = 'rfsheffer'

from math3d.vector import *
from math3d.spline import *
from file_reader import *
import fbx
from fbx_helpers import *


class KeyFrame:
    def __init__(self):
        self.frame = 0          # Time line position of the keyframe,(0.0 ... numFrames, floating point values are valid)
        self.frame_scale = 0    # Scaling factor used to interpolate to next keyframe, computed as (1/nextFrame-thisFrame)
        self.value = Vec3()     # absolute 3D position of euler angle at this keyframe
        self.c_factor = Vec3()  # The constant curve fitting factor for the Hermite curve interpolation
        self.b_fractor = Vec3() # The linear curve fitting factor
        self.a_factor = Vec3()  # The square curve fitting factor

    def read_keyframe(self, fp):
        self.frame = read_float(fp)
        self.frame_scale = read_float(fp)
        for i in range(0, 3):
            self.value[i] = read_float(fp)

        for i in range(0, 3):
            self.c_factor[i] = read_float(fp)

        for i in range(0, 3):
            self.b_fractor[i] = read_float(fp)

        for i in range(0, 3):
            self.a_factor[i] = read_float(fp)

class BoneTrack:
    TRACK_TYPES = {
        'rotation': 0,
        'translation': 1,
        'scale': 2
    }

    def __init__(self):
        self.num_keys = 0
        self.bone_num = 0
        self.track_type = 0
        self.keys = []      # keyframes

    def read_bone_track(self, fp):
        self.num_keys = read_unsigned_int(fp)
        self.bone_num = read_unsigned_int(fp)
        self.track_type = read_unsigned_int(fp)
        for i in range(0, self.num_keys):
            key = KeyFrame()
            key.read_keyframe(fp)
            self.keys.append(key)

class KeyframeTag:
    def __init__(self):
        self.frame_num = 0.0
        self.tag_type = 0

    def read_keytag(self, fp):
        self.frame_num = read_float(fp)
        self.tag_type = read_unsigned_int(fp)

class NadFile:
    ACCEPTED_MDL_VERSIONS = [3]
    BAD_INPUT_ERROR_MSG = 'bad input file!'

    def __init__(self):
        self.version = 0
        self.num_bone_tracks = 0
        self.flags = 0
        self.duration = 0.0
        self.bone_tracks = []
        self.num_tags = 0
        self.tags = []

    def open_nad(self, file_name):
        """
        Imports the NODs data into the structure
        :param file_name: The model file to import from
        """
        fp = open(file_name)
        if not fp:
            raise Exception(NadFile.BAD_INPUT_ERROR_MSG)

        # Read in the header data
        self.version = read_unsigned_int(fp)
        if self.version not in NadFile.ACCEPTED_MDL_VERSIONS:
            raise Exception(NadFile.BAD_INPUT_ERROR_MSG)

        self.num_bone_tracks = read_unsigned_int(fp)
        self.flags = read_unsigned_int(fp)
        self.duration = read_float(fp)

        for i in range(0, self.num_bone_tracks):
            bone_track = BoneTrack()
            bone_track.read_bone_track(fp)
            self.bone_tracks.append(bone_track)

        self.num_tags = read_unsigned_int(fp)

        for i in range(0, self.num_tags):
            key_tag = KeyframeTag()
            key_tag.read_keytag(fp)
            self.tags.append(key_tag)

    def export_fbx(self):
        pass
