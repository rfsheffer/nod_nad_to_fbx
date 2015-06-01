__author__ = 'rfsheffer'

import os
import optparse
from nod_file import *
from nad_file import *


def main():
    # Get the necessary arguments
    argParser = optparse.OptionParser(usage='usage: %prog -i [input dir] -o [output dir] [options]', version="%prog 0.1")
    argParser.add_option('-o', '--output', action='store', type='string', dest='output', default=False,
                         help='FBX output file name')
    argParser.add_option('-i', '--input', action='store', type='string', dest='input', default=False,
                         help='The NOD (Nihilistic Object Data) to convert')
    argParser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
                         help='Spews information about the process (takes more time)')

    (options, args) = argParser.parse_args()

    if options.input == False or options.output == False:
        print('Input and Output directories required to run this software!')
        argParser.print_version()
        argParser.print_help()
        quit()

    fbx_name = os.path.basename(options.input)
    fbx_name = fbx_name.split('.')[0] + '.fbx'

    if '.nod' in options.input:
        nod = NodFile()
        nod.open_nod(options.input)
        nod.export_fbx(os.path.join(options.output, fbx_name))
    elif '.nad' in options.input:
        print('NAD not supported yet!')
    else:
        raise Exception('bad input file!')


if __name__ == '__main__':
    main()
