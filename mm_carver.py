#!/usr/bin/python

# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import optparse

# import only if necessary
from contexts.media import frag_mm_meta_context
from contexts.tsk import tsk_context
from contexts.plain import plain_context
from contexts.magic import magic_context
import lib.datatypes


class CContext():
    default_imagefile = 'image.img'
    default_fragmentsize = 4096
    default_incrementsize = 4096
    default_offset = 0
    default_preprocessing = False

    def __init__(self):
        pass

    def run(self):
        lParser = optparse.OptionParser(add_help_option=False)
        lParser.add_option("-h", "--help", action="help")
        lParser.add_option("-v", action="store_true", dest="verbose",
                help="Be moderately verbose")
        lParser.add_option("-f", "--file", dest="imagefile",
                help="The imagefile (default:" +
                CContext.default_imagefile + ")",
                default=CContext.default_imagefile)
        lParser.add_option("-s", "--fragmentsize", dest="fragmentsize",
                help="Size of fragments to investigate (default:" +
                str(CContext.default_fragmentsize) + ")",
                default=CContext.default_fragmentsize,
                type="int")
        lParser.add_option("-i", "--incrementsize", dest="incrementsize",
                help="Number of bytes from possible start of fragments" +
                "(default:" + str(CContext.default_incrementsize) + ")",
                default=CContext.default_incrementsize,
                type="int")
        lParser.add_option("-o", "--offset", dest="offset",
                help="Number of bytes to skip at the beginning" +
                " (default:" + str(CContext.default_offset) + ")",
                default=CContext.default_offset,
                type="int")
        lParser.add_option("-p", "--preprocess", action="store_true",
                dest="preprocess",
                help="Turn preprocessing on or off" +
                " (default:" + str(CContext.default_preprocessing) + ")",
                default=CContext.default_preprocessing)
        (lOptions, lArgs) = lParser.parse_args()

        try:
            lH264Headers = []
            lH264Fragments = []

            # open imagefile
            lImage = open(lOptions.imagefile, "rb")

            # initialize preprocessor
            if lOptions.preprocess == True:
                lProcessor = tsk_context.CTSK(lImage)
            else:
                lProcessor = plain_context.CPlain(lImage)

            # determine H.264 headers and fragments
            lProcessor.parseH264(lH264Headers, lH264Fragments,
                    lOptions.offset, lOptions.incrementsize,
                    lOptions.fragmentsize)

            print(lH264Headers)

            # close imagefile
            lImage.close()

            # TODO reassembly:

        except LookupError, pExc:
            print("Error: " + str(pExc))
            sys.exit(-1)
        except NameError, pExc:
            print("Error: " + str(pExc))
            sys.exit(-2)
        except EOFError, pExc:
            sys.exit(-3)
        except Exception, pExc:
            print("Error: " + str(pExc))
            sys.exit(-4)

if __name__ == "__main__":
    lContext = CContext()
    lContext.run()
