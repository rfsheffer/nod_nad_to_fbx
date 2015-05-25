__author__ = 'rsheffer'

import fbx

def create_texture(sdk_manager, name, filename):
    l_texture = fbx.FbxFileTexture.Create(sdk_manager, name)
    l_texture.SetFileName(filename)
    l_texture.SetTextureUse(fbx.FbxTexture.eStandard)
    l_texture.SetMappingType(fbx.FbxTexture.eUV)
    l_texture.SetMaterialUse(fbx.FbxFileTexture.eModelMaterial)
    l_texture.SetSwapUV(False)
    l_texture.SetTranslation(0.0, 0.0)
    l_texture.SetScale(1.0, 1.0)
    l_texture.SetRotation(0.0, 0.0)
    return l_texture

def create_material(sdk_manager):
    lMaterialName = "material"
    lShadingName = "Phong"
    fbx.FbxDouble3(0.0, 0.0, 0.0)
    lBlack = fbx.FbxDouble3(0.0, 0.0, 0.0)
    lRed = fbx.FbxDouble3(1.0, 0.0, 0.0)
    lDiffuseColor = fbx.FbxDouble3(0.75, 0.75, 0.0)
    gMaterial = fbx.FbxSurfacePhong.Create(sdk_manager, lMaterialName)

    # Generate primary and secondary colors.
    '''gMaterial.Emissive
    gMaterial.GetEmissiveColor()      .Set(lBlack)
    gMaterial.GetAmbientColor()       .Set(lRed)
    gMaterial.GetDiffuseColor()       .Set(lDiffuseColor)
    gMaterial.GetTransparencyFactor() .Set(40.5)
    gMaterial.GetShadingModel()       .Set(lShadingName)
    gMaterial.GetShininess()          .Set(0.5)'''
    return gMaterial

def save_scene(filename, fbx_manager, fbx_scene, as_ascii=False):
    """ Save the scene using the Python FBX API """
    exporter = fbx.FbxExporter.Create(fbx_manager, '')

    if as_ascii:
        # DEBUG: Initialize the FbxExporter object to export in ASCII.
        ascii_format_index = get_ascii_format_index(fbx_manager)
        is_initialized = exporter.Initialize(filename, ascii_format_index)
    else:
        is_initialized = exporter.Initialize(filename)

    if not is_initialized:
        raise Exception('Exporter failed to initialize. Error returned: ' + str(exporter.GetStatus().GetErrorString()))

    exporter.Export(fbx_scene)

    exporter.Destroy()


def get_ascii_format_index(fbx_manager):
    """ Obtain the index of the ASCII export format. """
    # Count the number of formats we can write to.
    num_formats = fbx_manager.GetIOPluginRegistry().GetWriterFormatCount()

    # Set the default format to the native binary format.
    format_index = fbx_manager.GetIOPluginRegistry().GetNativeWriterFormat()

    # Get the FBX format index whose corresponding description contains "ascii".
    for i in range(0, num_formats):

        # First check if the writer is an FBX writer.
        if fbx_manager.GetIOPluginRegistry().WriterIsFBX(i):

            # Obtain the description of the FBX writer.
            description = fbx_manager.GetIOPluginRegistry().GetWriterFormatDescription(i)

            # Check if the description contains 'ascii'.
            if 'ascii' in description:
                format_index = i
                break

    # Return the file format.
    return format_index
