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
from reassembly.reassembly import reassembly_context
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
        self.mFragments = []

    @property
    def fragments(self):
        return self.mFragments

    @staticmethod
    def getCPUs():
        return multiprocessing.cpu_count()

    def runClassify(self, pOptions, pCaller):
        try:
            pCaller.beginCallback(os.path.getsize(pOptions.imagefile),
                    pOptions.offset,
                    "")
            # initialize preprocessor
            lProcessor = preprocessing_context.CPreprocessing(pOptions)
            self.mFragments = lProcessor.classify(pOptions, pCaller)
            logging.info("Back to the main context.")

            logging.info("8<=============== FRAGMENTs ==============")
            for lIdx in xrange(len(self.mFragments)):
                lFragment = self.mFragments[lIdx]
                logging.info("FragmentIdx %04d" % lIdx + ": " + str(lFragment))
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
            pCaller.beginCallback(os.path.getsize(pOptions.imagefile),
                    pOptions.offset,
                    "")

            lReassembly = None
            if pOptions.recoverfiletype == "video":
                lReassembly = \
                    reassembly_context.CReassemblyFactory.getInstanceVideo(\
                    pOptions.assemblymethod)
            elif pOptions.recoverfiletype == "video":
                lReassembly = \
                    reassembly_context.CReassemblyFactory.getInstanceJpeg(\
                    pOptions.assemblymethod)
            elif pOptions.recoverfiletype == "video":
                lReassembly = \
                    reassembly_context.CReassemblyFactory.getInstancePng(\
                    pOptions.assemblymethod)
            if lReassembly != None:
                lReassembly.assemble(pOptions, self.mFragments, pCaller)
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
