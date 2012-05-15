# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import multiprocessing
import traceback
import logging
import datetime

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
        self.__mFragments = None
        self.__mFiles = None

    @property
    def fragments(self):
        return self.__mFragments

    @property
    def files(self):
        return self.__mFiles

    @staticmethod
    def getCPUs():
        return multiprocessing.cpu_count()

    def runClassify(self, pOptions, pCaller):
        pCaller.beginCallback(os.path.getsize(pOptions.imagefile),
                pOptions.offset,
                "")
        # initialize preprocessor
        lProcessor = preprocessing_context.CPreprocessing(pOptions)
        self.__mFragments = lProcessor.classify(pOptions, pCaller)
        logging.info("Back to the main context.")

        logging.info("8<=============== FRAGMENTs ==============")
        lCnt = 0
        for lFragment in self.__mFragments:
            logging.info("FragmentIdx %04d" % lCnt + ": " + str(lFragment))
            lCnt += 1
        logging.info("8<=============== FRAGMENTs ==============")

        pCaller.progressCallback(100)
        pCaller.finishedCallback()

    def runReassembly(self, pOptions, pCaller):
        pCaller.beginCallback(os.path.getsize(pOptions.imagefile),
                pOptions.offset,
                "")

        lReassembly = None
        if pOptions.recoverfiletype == "video":
            lReassembly = \
                reassembly_context.CReassemblyFactory.getInstanceVideo(\
                pOptions.assemblymethod)
        elif pOptions.recoverfiletype == "jpeg":
            lReassembly = \
                reassembly_context.CReassemblyFactory.getInstanceJpeg(\
                pOptions.assemblymethod)
        elif pOptions.recoverfiletype == "png":
            lReassembly = \
                reassembly_context.CReassemblyFactory.getInstancePng(\
                pOptions.assemblymethod)
        if lReassembly != None:
            self.__mFiles = lReassembly.assemble(pOptions, self.__mFragments, \
                                                 pCaller)

        pCaller.finishedCallback()

    def cleanup(self):
        del(self.__mFragments)
