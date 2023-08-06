#! /usr/bin/env python
#
# A script that runs a Pysos model
#
#   pysos <model.py>
#
#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import sys
import os
if sys.version_info[0:2] < (2,4):
    print ""
    print "ERROR: Pysos requires Python 2.4 or newer"
    sys.exit(1)
from os.path import abspath, dirname
if hasattr(sys,"frozen"):
    absolute_path=abspath(sys.executable)
else:
    absolute_path=abspath(__file__)
sys.path.insert(0, dirname(dirname(absolute_path))+os.sep+"coopr")
sys.path.insert(0, dirname(dirname(absolute_path)))
sys.path.append(".")
sys.path.append("..")

from optparse import OptionParser
#
# Finish imports
#
import pysos
import traceback

filter_excepthook=False
def pysos_excepthook(etype,value,tb):
    print ""
    if filter_excepthook:
        print "ERROR: Unexpected exception while loading Pysos model "+args[0]
    else:
        print "ERROR: Unexpected exception while running Pysos model "+args[0]
    print "  ",value
    print ""
    tb_list = traceback.extract_tb(tb,None)
    i=0
    if not pysos.debug and filter_excepthook:
        while i < len(tb_list):
            if args[0] in tb_list[i][0]:
                break
            i += 1
    print "Pysos Traceback (most recent call last):"
    for item in tb_list[i:]:
        print "  File \""+item[0]+"\", line "+str(item[1])+", in "+item[2]
        if item[3] is not None:
            print "    "+item[3]
    sys.exit(1)

def main():
        #
        #
        # Setup command-line options
        #
        #
    parser = OptionParser()
    parser.add_option("--path",
        help="Give a path that is used to find the Pysos python files",
        action="store",
        dest="solver",
        type="string",
        default=".")
    parser.add_option("--debug",
            help="Generate verbose debugging information",
            action="store_true",
            dest="debug",
            default=False)
    parser.usage="pysos [options] <model.py>"
    #
    #
    # Parse command-line options
    #
    #
    (options, args) = parser.parse_args()
    args=sys.argv[1:]
    sys.excepthook = pysos_excepthook
    #
    #
    # Setup solver and model
    #
    #
    if len(args) == 0 or len(args) > 1:
        parser.print_help()
        sys.exit(1)
    if not os.path.exists(args[0]):
        print "File "+args[0]+" does not exist!"
        sys.exit(1)

    if options.debug:
        pysos.debug=True
    #
    # Create Model
    #
    if "/" in args[0]:
        tmp= "/".join((args[0]).split("/")[:-1])
        sys.path.append(tmp)
        tmp_import = (args[0]).split("/")[-1]
    elif "\\" in args[0]:
        tmp= "\\".join((args[0]).split("\\")[:-1])
        sys.path.append(tmp)
        tmp_import = (args[0]).split("\\")[-1]
    else:
        tmp_import = args[0]

    namespace = ".".join((tmp_import).split(".")[:-1])
    exec "import "+namespace+" as user"
    filter_excepthook=False
