__author__ = 'rsheffer'

import fbx

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
