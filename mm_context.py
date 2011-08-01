# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import traceback
import logging
import threading

# import only if necessary
#from contexts.media import frag_mm_meta_context
from preprocessing import preprocessing_context
from collating.magic import magic_context
from reassembly.reassembly import reassembly_context
from reassembly.fragmentizer import fragmentizer_context
from reassembly.ffmpeg import ffmpeg_context
from lib import datatypes


class CContext:
    sDefaultImagefile = 'image.img'
    sDefaultFragmentsize = 512
    sDefaultIncrementsize = 512
    sDefaultBlockGap = 16384
    sDefaultOffset = 0
    sDefaultPreprocessing = False
    sDefaultOutput = '/tmp/temp'
    sDefaultOutputFormat = 'jpg'

    def __init__(self):
        self.mH264Fragments = []

    def getH264Fragments(self):
        return self.mH264Fragments

    def runClassify(self, pOptions, pCaller):
        try:

            # initialize preprocessor
            lProcessor = preprocessing_context.CPreprocessing(pOptions)
            lProcessor.classify(pCaller)

            if pOptions.verbose is True:
                lFragments = lProcessor.getVideoBlocks().getBlocks()
                print("Number of frags tested %d / Number of H.264 fragments %d" % 
                        len(lProcessor.getVideoBlocks()), (len(lFragments)))
                for lH264Header in lFragments:
                    print("Fragment offset: " + str(lH264Header))

            # initialize fragmentizer with parameters that describe
            # the most important properties for blocks => fragments
            # conversions
            lFragmentizer = fragmentizer_context.CFragmentizer()
            lFragmentizer.defrag(lProcessor.getVideoBlocks(), self.mH264Fragments, 
                    pOptions.fragmentsize, pOptions.blockgap)
            for lH264Fragment in self.mH264Fragments:
                print(lH264Fragment)
                #if pCaller != None:
                pCaller.resultCallback(lH264Fragment.mIsHeader, \
                        lH264Fragment.mOffset,
                        lH264Fragment.mSize)

            #if pCaller != None:
            pCaller.finishedCallback()

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

    def runReassembly(self, pOptions, pCaller):
        try:
            lFFMpeg = ffmpeg_context.CFFMpegContext()
            lReassembly = reassembly_context.CReassembly()
            lReassembly.assemble(pOptions, self.mH264Fragments, lFFMpeg, pCaller)
            pCaller.finishedCallback()
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
