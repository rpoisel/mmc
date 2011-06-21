# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import traceback
import logging

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

    def run(self, pOptions):
        try:
            lVideoFrags = frags.CFrags()
            lH264Fragments = []

            # initialize preprocessor
            if pOptions.preprocess == True:
                lProcessor = tsk_context.CTSK(pOptions.imagefile,
                    pOptions.offset, pOptions.incrementsize,
                    pOptions.fragmentsize)
            else:
                lProcessor = plain_context.CPlain(pOptions.imagefile,
                    pOptions.offset, pOptions.incrementsize,
                    pOptions.fragmentsize)

            # determine H.264 headers and fragments
            lFragsTested = lProcessor.parseH264(lVideoFrags)

            if pOptions.verbose is True:
                lFragments = lVideoFrags.getBlocks()
                print("Number of frags tested %d / Number of H.264 fragments %d" % 
                        (lFragsTested, (len(lFragments) + \
                                len(lVideoFrags.getHeaders()))))
                for lH264Header in lFragments:
                    print("Fragment offset: " + str(lH264Header))

            # TODO reassembly (process map of fragments)
            lFFMpeg = ffmpeg_context.CFFMpegContext()
            # initialize fragmentizer with parameters that describe
            # the most important properties for blocks => fragments
            # conversions
            lFragmentizer = fragmentizer_context.CFragmentizer()
            lFragmentizer.defrag(lVideoFrags, lH264Fragments)
            lReassembly = reassembly_context.CReassembly(pOptions.output)
            lReassembly.assemble(lH264Fragments, lFFMpeg, pOptions.output)

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
