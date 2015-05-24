__author__ = 'rsheffer'

from math3d.vector import *
from file_reader import *
import fbx
from fbx_helpers import *

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
        self.bone_num = read_unsigned_int(fp) #  NOTE: The standard says this is a byte, the standard lies


class NodFace:
    def __init__(self):
        self.indicies = [0, 0, 0]

    def read_face(self, fp):
        for i in range(0, 3):
            self.indicies[i] = read_unsigned_short(fp)


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
        self.num_faces = read_unsigned_short(fp)
        self.num_verticies = read_unsigned_short(fp)
        self.min_verticies = read_unsigned_short(fp)
        self.group_flags = read_unsigned_short(fp)
        self.bone_num = read_unsigned_short(fp)  # standard says 1 byte...
        self.mesh_num = read_unsigned_short(fp)  # standard says 1 byte...


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
        """
        Imports the NODs data into the structure
        :param file_name: The model file to import from
        """
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

        num_bones = read_unsigned_short(fp)
        num_meshes = read_unsigned_short(fp)
        num_verts = read_unsigned_int(fp)
        num_faces = read_unsigned_int(fp)
        num_groups = read_unsigned_short(fp)
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
                self.lod_vert_collapse.append(read_unsigned_short(fp))

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


    def export_fbx(self, out_name):
        """
        Output the model data to an fbx
        :param out_name: The fbx to output to, example ~/temp/mymodel.fbx
        """

        # Create the required FBX SDK data structures.
        fbx_manager = fbx.FbxManager.Create()
        fbx_scene = fbx.FbxScene.Create(fbx_manager, '')

        root_node = fbx_scene.GetRootNode()

        vamp_node = fbx.FbxNode.Create(fbx_scene, 'vampNode')
        root_node.AddChild(vamp_node)

        cur_face = 0
        cur_vertex = 0
        group_num = 0
        for group in self.mesh_groups:
            mesh_name = self.mesh_names[group.mesh_num]

            new_node = fbx.FbxNode.Create(fbx_scene, '{0}Node{1}'.format(mesh_name, group_num))
            vamp_node.AddChild(new_node)

            # Create a new mesh node attribute in the scene, and set it as the new node's attribute
            new_mesh = fbx.FbxMesh.Create(fbx_scene, '{0}Mesh{1}'.format(mesh_name, group_num))
            new_node.SetNodeAttribute(new_mesh)

            # Init the required number of control points (verticies)
            new_mesh.InitControlPoints(group.num_verticies)

            cur_poly = 0
            cur_point = 0
            for i in range(cur_face, cur_face + group.num_faces):

                new_mesh.BeginPolygon(cur_poly)

                # set all the face control points and triangle polygons
                face = self.faces[i]
                for j in range(0, 3):
                    vertex = self.verticies[cur_vertex + face.indicies[j]]
                    new_mesh.SetControlPointAt(fbx.FbxVector4(vertex.pos[0], vertex.pos[1], vertex.pos[2]), cur_point + j)
                    new_mesh.AddPolygon(cur_point + j)

                cur_point += 3
                cur_poly += 1
                new_mesh.EndPolygon()

            # move to next group and its faces
            group_num += 1
            cur_face += group.num_faces
            cur_vertex += group.num_verticies


        # Save the scene.
        save_scene(out_name, fbx_manager, fbx_scene, False)

        # Destroy the fbx manager explicitly, which recursively destroys
        # all the objects that have been created with it.
        fbx_manager.Destroy()
        del fbx_manager, fbx_scene