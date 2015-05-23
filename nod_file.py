__author__ = 'rsheffer'

from math3d.vector import *
from file_reader import *


class NodBone:
    def __init__(self):
        self.rest_translate = Vec3()
        self.rest_matrix_inverse = [[0 for x in range(4)] for x in range(3)]
        self.sibling_id = -1
        self.child_id = -1
        self.parent_id = -1

    def read_bone(self, fp):
        for i in range(0, 3):
            self.rest_translate[i] = read_float(fp)

        for i in range(0, 3):
            row = self.rest_matrix_inverse[i]
            for j in range(0, 4):
                row[j] = read_float(fp)

        self.sibling_id = read_short(fp)
        self.child_id = read_short(fp)
        self.parent_id = read_short(fp)


class NodVertex:
    def __init__(self):
        self.pos = Vec3()
        self.norm = Vec3()
        self.uv = Vec3()
        self.weight = 0.0
        self.bone_num = -1

    def read_vertex(self, fp):
        for i in range(0, 3):
            self.pos[i] = read_float(fp)

        for i in range(0, 3):
            self.norm[i] = read_float(fp)

        for i in range(0, 2):
            self.uv[i] = read_float(fp)

        self.weight = read_float(fp)
        self.bone_num = read_byte(fp)

        print self.bone_num


class NodFace:
    def __init__(self):
        self.indicies = [0, 0, 0]

    def read_face(self, fp):
        for i in range(0, 3):
            self.indicies[i] = read_short(fp)


class NodMeshGroup:
    GROUP_FLAGS = {
        'HAS_LOD'       : 1,
        'NO_WEIGHTS'    : 2,
        'NO_SKINNING'   : 4,
        'MULTI_TEXTURE' : 8
    }

    def __init__(self):
        self.material_id = -1
        self.num_faces = 0
        self.num_verticies = 0
        self.min_verticies = 0
        self.group_flags = 0
        self.bone_num = 0
        self.mesh_num = 0

    def read_mesh_group(self, fp):
        self.material_id = read_int(fp)
        fp.read(12)  # padding
        self.num_faces = read_short(fp)
        self.num_verticies = read_short(fp)
        self.min_verticies = read_short(fp)
        self.group_flags = read_short(fp)
        self.bone_num = read_byte(fp)
        self.mesh_num = read_byte(fp)


class NodFile:
    ACCEPTED_MDL_VERSIONS = [7]
    BAD_INPUT_ERROR_MSG = 'bad input file!'

    MODEL_FLAGS = {
        'HAS_LOD'   : 1,
        'INLINE'    : 2,
        'STATIC'    : 4,
        'RES1'      : 8,
        'RES2'      : 16
    }

    def __init__(self):
        self.version = -1
        self.materials = []
        self.model_flags = 0
        self.bounds = [Vec3(), Vec3()]
        self.bones = []
        self.mesh_names = []
        self.verticies = []
        self.lod_vert_collapse = []
        self.faces = []
        self.mesh_groups = []

    def open_nod(self, file_name):
        fp = open(file_name)
        if not fp:
            raise Exception(NodFile.BAD_INPUT_ERROR_MSG)

        # Read in the header data
        self.version = read_unsigned_int(fp)
        if self.version not in NodFile.ACCEPTED_MDL_VERSIONS:
            raise Exception(NodFile.BAD_INPUT_ERROR_MSG)

        num_materials = read_unsigned_int(fp)
        for i in range(0, num_materials):
            mat_name = read_string(fp, 32)
            self.materials.append(mat_name)

        num_bones = read_short(fp)
        num_meshes = read_short(fp)
        num_verts = read_unsigned_int(fp)
        num_faces = read_unsigned_int(fp)
        num_groups = read_short(fp)
        self.model_flags = read_unsigned_int(fp)
        for i in range(0, 2):
            bound = self.bounds[i]
            for j in range(0, 3):
                bound[j] = read_float(fp)

        # read in the bones
        for i in range(0, num_bones):
            bone = NodBone()
            bone.read_bone(fp)
            self.bones.append(bone)

        # read in the mesh names
        for i in range(0, num_meshes):
            mesh_name = read_string(fp, 32)
            self.mesh_names.append(mesh_name)

        # read in the vertex soup
        for i in range(0, num_verts):
            vertex = NodVertex()
            vertex.read_vertex(fp)
            self.verticies.append(vertex)

        # if there are LODs, load the collapse data
        if (self.model_flags & NodFile.MODEL_FLAGS['HAS_LOD']) != 0:
            for i in range(0, num_verts):
                self.lod_vert_collapse.append(read_short(fp))

        # face data is next. It is just a long list of three shorts per face.
        # this defines the indicies of the verticies of the face polygon.
        for i in range(0, num_faces):
            face = NodFace()
            face.read_face(fp)
            self.faces.append(face)

        # read in the groups. The groups define how the raw materials above are renderered.
        for i in range(0, num_groups):
            group = NodMeshGroup()
            group.read_mesh_group(fp)
            self.mesh_groups.append(group)

        fp.close()
