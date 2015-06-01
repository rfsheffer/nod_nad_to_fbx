__author__ = 'rfsheffer'

import os
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

        for i in range(0, 4):  # column
            for j in range(0, 3):  # row
                self.rest_matrix_inverse[j][i] = read_float(fp)

        self.sibling_id = read_short(fp)
        self.child_id = read_short(fp)
        self.parent_id = read_short(fp)
        '''print('bone {0}, {1}, {2}            sib:{3}    child:{4}    parent:{5}'.format(self.rest_translate[0],
                                                                                self.rest_translate[1],
                                                                                self.rest_translate[2],
                                                                                self.sibling_id,
                                                                                self.child_id,
                                                                                self.parent_id))'''


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

        scene_info = fbx.FbxDocumentInfo.Create(fbx_manager, "SceneInfo")
        scene_info.mTitle = os.path.basename(out_name)
        scene_info.mSubject = "Nihilistic NOD model output to FBX"
        scene_info.mAuthor = "Nihilistic"
        scene_info.mRevision = "rev. 1.0"
        scene_info.mKeywords = os.path.basename(out_name)
        scene_info.mComment = "n/a"
        fbx_scene.SetSceneInfo(scene_info)

        root_node = fbx_scene.GetRootNode()

        vamp_node = fbx.FbxNode.Create(fbx_scene, os.path.basename(out_name))
        root_node.AddChild(vamp_node)

        # Now create the skeleton
        skel_bones = []
        for i in range(0, len(self.bones)):
            bone = self.bones[i]

            is_root = bone.sibling_id == -1 and bone.parent_id == -1

            bone_name = 'root' if is_root else 'bone{0}'.format(i - 1)
            skeleton_root_attridute = fbx.FbxSkeleton.Create(fbx_manager, bone_name)
            skeleton_root_attridute.SetSkeletonType(fbx.FbxSkeleton.eRoot if is_root else fbx.FbxSkeleton.eLimbNode)
            if not is_root:
                skeleton_root_attridute.Size.Set(1.0)
            skeleton_bone = fbx.FbxNode.Create(fbx_manager, bone_name)
            skeleton_bone.SetNodeAttribute(skeleton_root_attridute)
            skeleton_bone.LclTranslation.Set(fbx.FbxDouble3(bone.rest_translate[0],
                                                            bone.rest_translate[1],
                                                            bone.rest_translate[2]))
            skel_bones.append(skeleton_bone)
            if not is_root:
                skel_bones[bone.parent_id].AddChild(skeleton_bone)

        # Add the root bone to the scene hierarchy
        vamp_node.AddChild(skel_bones[0])

        material_list = {}  # Gets populated as textures are needed. Contains a (material, texture) tupple per key
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
            new_node.SetShadingMode(fbx.FbxNode.eTextureShading)

            # Init the required number of control points (verticies)
            new_mesh.InitControlPoints(group.num_verticies)

            # Clusters are verticies which are influenced by a bone.
            group_clusters = {}

            # Add all the verticies for this group
            for i in range(0, group.num_verticies):
                vertex = self.verticies[cur_vertex + i]
                new_mesh.SetControlPointAt(fbx.FbxVector4(vertex.pos[0], vertex.pos[1], vertex.pos[2]), i)
                # Create a cluster for each bone (verticies influenced by the bone)
                if vertex.bone_num not in group_clusters:
                    cluster = fbx.FbxCluster.Create(fbx_manager, '')
                    cluster.SetLink(skel_bones[vertex.bone_num])
                    cluster.SetLinkMode(fbx.FbxCluster.eTotalOne) # weights should add up to 1
                    group_clusters[vertex.bone_num] = cluster
                group_clusters[vertex.bone_num].AddControlPointIndex(i, vertex.weight)


            # Get the global node transform to apply to the clusters
            lScene = new_node.GetScene()
            lXMatrix = lScene.GetAnimationEvaluator().GetNodeGlobalTransform(new_node)

            # Create a skin deformer and assign all of the clusters
            skin_mod = fbx.FbxSkin.Create(fbx_manager, '')
            for bone_index, cluster in group_clusters.iteritems():
                cluster.SetTransformMatrix(lXMatrix)

                # Apply the skeleton bone global transform as the clusters link matrix
                skel_bone_matrix = lScene.GetAnimationEvaluator().GetNodeGlobalTransform(skel_bones[bone_index])
                cluster.SetTransformLinkMatrix(skel_bone_matrix)

                skin_mod.AddCluster(cluster)

            # Add the skin deformer to the mesh
            new_mesh.AddDeformer(skin_mod)

            # Create the layer to store UV and normal data
            layer = new_mesh.GetLayer(0)
            if not layer:
                new_mesh.CreateLayer()
                layer = new_mesh.GetLayer(0)

            # Create the materials.
            # Each polygon face will be assigned a unique material.
            matLayer = fbx.FbxLayerElementMaterial.Create(new_mesh, "")
            matLayer.SetMappingMode(fbx.FbxLayerElement.eByPolygon)
            matLayer.SetReferenceMode(fbx.FbxLayerElement.eIndexToDirect)
            layer.SetMaterials(matLayer)

            # Setup the indicies (the connections between verticies) per polygon
            cur_poly = 0
            for i in range(0, group.num_faces):

                new_mesh.BeginPolygon(cur_poly)

                face = self.faces[cur_face + i]
                for j in range(0, 3):
                    new_mesh.AddPolygon(face.indicies[j])

                cur_poly += 1
                new_mesh.EndPolygon()

            # specify normals per control point.
            # For compatibility, we follow the rules stated in the
            # layer class documentation: normals are defined on layer 0 and
            # are assigned by control point.
            normLayer = fbx.FbxLayerElementNormal.Create(new_mesh, '')
            normLayer.SetMappingMode(fbx.FbxLayerElement.eByControlPoint)
            normLayer.SetReferenceMode(fbx.FbxLayerElement.eDirect)

            for i in range(0, group.num_verticies):
                vertex = self.verticies[cur_vertex + i]
                normLayer.GetDirectArray().Add(fbx.FbxVector4(vertex.norm[0], vertex.norm[1], vertex.norm[2], 1.0))

            layer.SetNormals(normLayer)

            # Create color vertices
            '''vtxcLayer = fbx.FbxLayerElementVertexColor.Create(new_mesh, '')
            vtxcLayer.SetMappingMode(fbx.FbxLayerElement.eByControlPoint)
            vtxcLayer.SetReferenceMode(fbx.FbxLayerElement.eDirect)

            for i in range(0, group.num_verticies):
                vtxcLayer.GetDirectArray().Add(fbx.FbxColor(1.0, 1.0, 1.0, 1.0))

            layer.SetVertexColors(vtxcLayer)'''

            # create polygroups.
            # We are going to make a first group with the 4 sides.
            # And a second group with the top and bottom sides.
            # NOTE that the only reference mode allowed is eINDEX
            '''pgrpLayer = fbx.FbxLayerElementPolygonGroup.Create(new_mesh, '')
            pgrpLayer.SetMappingMode(fbx.FbxLayerElement.eByPolygon)
            pgrpLayer.SetReferenceMode(fbx.FbxLayerElement.eIndex)
            for i in range(0, group.num_faces):
                pgrpLayer.GetIndexArray().Add(0)

            layer.SetPolygonGroups(pgrpLayer)'''


            # create the UV textures mapping.
            # On layer 0 all the faces have the same texture
            uvLayer = fbx.FbxLayerElementUV.Create(new_mesh, '')
            uvLayer.SetMappingMode(fbx.FbxLayerElement.eByControlPoint)
            uvLayer.SetReferenceMode(fbx.FbxLayerElement.eDirect)

            # For all the verticies, set the UVs
            for i in range(0, group.num_verticies):
                vertex = self.verticies[cur_vertex + i]
                uvLayer.GetDirectArray().Add(fbx.FbxVector2(vertex.uv[0], vertex.uv[1]))

            layer.SetUVs(uvLayer)

            # Set textures
            if group.material_id != -1:
                texture_name = self.materials[group.material_id]

                # Create texture if nessesary
                if texture_name not in material_list:
                    texture = create_texture(fbx_manager, texture_name, texture_name + '.tga')

                    # We also need a material, create that now
                    material_name = fbx.FbxString(texture_name)

                    material = fbx.FbxSurfacePhong.Create(fbx_manager, material_name.Buffer())

                    # Generate primary and secondary colors.
                    material.Emissive.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
                    material.Ambient.Set(fbx.FbxDouble3(1.0, 1.0, 1.0))
                    material.Diffuse.Set(fbx.FbxDouble3(1.0, 1.0, 1.0))
                    material.Specular.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
                    material.TransparencyFactor.Set(0.0)
                    material.Shininess.Set(0.5)
                    material.ShadingModel.Set(fbx.FbxString("phong"))

                    material_info = (material, texture)
                    material_list[texture_name] = material_info

                else:
                    material_info = material_list[texture_name]

                texLayer = fbx.FbxLayerElementTexture.Create(new_mesh, '')
                texLayer.SetBlendMode(fbx.FbxLayerElementTexture.eModulate)
                texLayer.SetMappingMode(fbx.FbxLayerElement.eByPolygon)
                texLayer.SetReferenceMode(fbx.FbxLayerElement.eIndexToDirect)
                texLayer.GetDirectArray().Add(material_info[1])

                # set all faces to that texture
                for i in range(0, group.num_faces):
                    texLayer.GetIndexArray().Add(0)

                layer.SetTextures(fbx.FbxLayerElement.eTextureDiffuse, texLayer)

                lMeshNode = new_mesh.GetNode()
                if lMeshNode:
                    lMeshNode.AddMaterial(material_info[0])

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