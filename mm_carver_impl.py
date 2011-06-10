#!/usr/bin/python

# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import optparse
import traceback

# import only if necessary
#from contexts.media import frag_mm_meta_context
from preprocessing.tsk import tsk_context
from preprocessing.plain import plain_context
from collating.magic import magic_context
from reassembly.reassembly import reassembly_context
from reassembly.fragmentizer import fragmentizer_context
from reassembly.ffmpeg import ffmpeg_context
from lib import datatypes
from lib import frags


class CContext():
    sDefaultImagefile = 'image.img'
    sDefaultFragmentsize = 512
    sDefaultIncrementsize = 512
    sDefaultOffset = 0
    sDefaultPreprocessing = False
    sDefaultOutput = '/tmp/clever-output'

    def __init__(self):
        pass

    def parseOptions(self):
        lParser = optparse.OptionParser(add_help_option=False)
        lParser.add_option("-h", "--help", action="help")
        lParser.add_option("-v", action="store_true", dest="verbose",
                help="Be moderately verbose")
        lParser.add_option("-f", "--file", dest="imagefile",
                help="The imagefile (default:" +
                CContext.sDefaultImagefile + ")",
                default=CContext.sDefaultImagefile)
        lParser.add_option("-s", "--fragmentsize", dest="fragmentsize",
                help="Size of fragments to investigate (default:" +
                str(CContext.sDefaultFragmentsize) + ")",
                default=CContext.sDefaultFragmentsize,
                type="int")
        lParser.add_option("-i", "--incrementsize", dest="incrementsize",
                help="Number of bytes from possible start of fragments" +
                "(default:" + str(CContext.sDefaultIncrementsize) + ")",
                default=CContext.sDefaultIncrementsize,
                type="int")
        lParser.add_option("-e", "--offset", dest="offset",
                help="Number of bytes to skip at the beginning" +
                " (default:" + str(CContext.sDefaultOffset) + ")",
                default=CContext.sDefaultOffset,
                type="int")
        lParser.add_option("-p", "--preprocess", action="store_true",
                dest="preprocess",
                help="Turn preprocessing on or off" +
                " (default:" + str(CContext.sDefaultPreprocessing) + ")",
                default=CContext.sDefaultPreprocessing)
        lParser.add_option("-o", "--output", dest="output",
                help="The output directory for extracted information" +
                " (default:" + str(CContext.sDefaultOutput) + ")",
                default=CContext.sDefaultOutput)
        (lOptions, lArgs) = lParser.parse_args()

        return lOptions

    def run(self):
        lOptions = self.parseOptions()

        try:
            lVideoFrags = frags.CFrags()
            lH264Fragments = []

            # initialize preprocessor
            if lOptions.preprocess == True:
                lProcessor = tsk_context.CTSK(lOptions.imagefile,
                    lOptions.offset, lOptions.incrementsize,
                    lOptions.fragmentsize)
            else:
                lProcessor = plain_context.CPlain(lOptions.imagefile,
                    lOptions.offset, lOptions.incrementsize,
                    lOptions.fragmentsize)

            # determine H.264 headers and fragments
            lProcessor.parseH264(lVideoFrags)

            if lOptions.verbose is True:
                lFragments = lVideoFrags.getBlocks()
                print("Number of H.264 headers: %d" % len(lFragments))
                for lH264Header in lFragments:
                    print("Header offset: " + str(lH264Header))

            # TODO reassembly (process map of fragments)
            lFFMpeg = ffmpeg_context.CFFMpegContext()
            # initialize fragmentizer with parameters that describe
            # the most important properties for blocks => fragments
            # conversions
            lFragmentizer = fragmentizer_context.CFragmentizer()
            lFragmentizer.defrag(lVideoFrags, lH264Fragments)
            lReassembly = reassembly_context.CReassembly(lOptions.output)
            lReassembly.assemble(lH264Fragments, lFFMpeg, lOptions.output)

        except LookupError, pExc:
            print("LookupError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-1)
        except NameError, pExc:
            print("NameError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-2)
        except EOFError, pExc:
            print("EOFError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-3)
        except Exception, pExc:
            print("Error: " + str(pExc))
            traceback.print_exc()
            sys.exit(-4)

if __name__ == "__main__":
    lContext = CContext()
    lContext.run()
