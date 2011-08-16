# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import traceback
import logging
import datetime
import multiprocessing

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

    @staticmethod
    def getCPUs():
        return multiprocessing.cpu_count()

    def runClassify(self, pOptions, pCaller):
        try:

            # initialize preprocessor
            #lProcessor = preprocessing_context.CPreprocessing(pOptions)
            #lProcessor.classify(pCaller)
            lProcessor = preprocessing_context.CPreprocessing(pOptions)
            lVideoBlocks = lProcessor.classify(pOptions, pCaller)
            logging.info("Back to the main context.")

            if pOptions.verbose is True:
                lBlocks = lVideoBlocks.getBlocks()
                lHeaders = lVideoBlocks.getHeaders()
                logging.info("Number of H.264 fragments %d" % 
                        len(lVideoBlocks.getBlocks()))
                logging.info("8<============ Headers ==============")
                for lH264Header in lHeaders:
                    logging.info(str(lH264Header))
                logging.info("8<============ Blocks ==============")
                for lH264Block in lBlocks:
                    logging.info(str(lH264Block))

            # initialize fragmentizer with parameters that describe
            # the most important properties for blocks => fragments
            # conversions
            logging.info("Starting fragmentizing.")
            lFragmentizer = fragmentizer_context.CFragmentizer()
            self.mH264Fragments = lFragmentizer.defrag(lVideoBlocks, 
                    pOptions.fragmentsize, pOptions.blockgap,
                    pOptions.minfragsize)
            logging.info("Finished fragmentizing.")
            logging.info("8<=============== FRAGMENTs ==============")
            for lIdx in xrange(len(self.mH264Fragments)):
                lH264Fragment = self.mH264Fragments[lIdx]
                logging.info("FragmentIdx %04d" % lIdx + ": " + str(lH264Fragment))
                pCaller.resultCallback(lH264Fragment.mIsHeader, \
                        lH264Fragment.mOffset,
                        lH264Fragment.mSize)
            logging.info("8<=============== FRAGMENTs ==============")

            pCaller.progressCallback(100)
            pCaller.finishedCallback()

        except LookupError, pExc:
            logging.error("LookupError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-1)
        except NameError, pExc:
            logging.error("NameError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-2)
        except EOFError, pExc:
            logging.error("EOFError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-3)
        except Exception, pExc:
            logging.error(str(pExc))
            traceback.print_exc()
            sys.exit(-4)

    def runReassembly(self, pOptions, pCaller):
        try:
            lFFMpeg = ffmpeg_context.CFFMpegContext()
            lReassembly = reassembly_context.CReassembly()
            lReassembly.assemble(pOptions, self.mH264Fragments, lFFMpeg, pCaller)
            pCaller.finishedCallback()
        except LookupError, pExc:
            logging.error("LookupError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-1)
        except NameError, pExc:
            logging.error("NameError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-2)
        except EOFError, pExc:
            logging.error("EOFError: " + str(pExc))
            traceback.print_exc()
            sys.exit(-3)
        except Exception, pExc:
            logging.error(str(pExc))
            traceback.print_exc()
            sys.exit(-4)
