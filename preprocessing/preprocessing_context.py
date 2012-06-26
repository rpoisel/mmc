import os
import sys
import logging
import datetime
import threading
import time
import Queue
from ctypes import *

from preprocessing.tsk import tsk_context
from preprocessing.plain import plain_context
try:
    #from collating.fragment import fragment_context
    from collating.fragment import fragment_context
except ImportError, pExc:
    logging.error("Problem with importing a library: " + str(pExc))
    logging.error("Try making it with 'make' first.")
    sys.exit(-1)
#from collating.magic import magic_context


class CResultThread(threading.Thread):

    def __init__(self, pCaller, pResultArray, pQueue):
        super(CResultThread, self).__init__()
        self.__mCaller = pCaller
        self.__mResultArray = pResultArray
        self.__mQueue = pQueue

    def run(self):
        while True:
            lResults = 0
            for lResult in self.__mResultArray:
                lResults += lResult
            self.__mCaller.progressCallback(
                    lResults / len(self.__mResultArray)
                    )
            time.sleep(.1)
            lStop = False
            try:
                lStop = self.__mQueue.get_nowait()
            except Queue.Empty:
                pass
            if lStop is True:
                break


class CPreprocessing:

    # TODO implement read list of available plugins
    @staticmethod
    def getPreprocessors():
        return [{'name':'plain'}, {'name':'sleuthkit'}]

    def __init__(self, pOptions):
        self.__mResultArray = None

    def classify(self, pOptions, pCaller):

        lLast = datetime.datetime.now()
        logging.info(str(lLast) + " Start classifying.")

        lTypes = []
        if pOptions.recoverfiletype == "video":
            lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_VIDEO,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_H264,
                'mStrength': pOptions.strength})
        elif pOptions.recoverfiletype == "jpeg":
            #lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
            #    'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_JPG,
                'mStrength': pOptions.strength})
        elif pOptions.recoverfiletype == "png":
            lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_PNG,
                'mStrength': pOptions.strength})

        lResultArray = [0]

        lQueue = Queue.Queue()
        lResultThread = CResultThread(pCaller, lResultArray, lQueue)
        lResultThread.start()

        lFragments = None
        try:
            lClassifier = fragment_context.CFragmentClassifier()
            #lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
            lSize = os.path.getsize(pOptions.imagefile)
            lFragsTotal = lSize / pOptions.fragmentsize
            lFragments = lClassifier.classify(pOptions.fragmentsize,
                    lFragsTotal, pOptions.imagefile, pOptions.offset,
                            lTypes,
                    pOptions.blockgap, pOptions.minfragsize,
                            pOptions.maxcpus)
        except OSError, pExc:
            lQueue.put(True)
            lResultThread.join()
            raise pExc

        lNow = datetime.datetime.now()
        logging.info("Finished classifying. Duration: " +
                str(lNow - lLast))

        lQueue.put(True)
        lResultThread.join()

        return lFragments
