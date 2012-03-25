import os
import sys
import logging
import multiprocessing
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
from reassembly.fragmentizer import fragmentizer_context
from collating.magic import magic_context
from lib import frags


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
            self.__mCaller.progressCallback( \
                    lResults / len(self.__mResultArray) \
                    )
            time.sleep(.1)
            lStop = False
            try:
                lStop = self.__mQueue.get_nowait()
            except Queue.Empty:
                pass
            if lStop == True:
                break


class CPreprocessing:

    # TODO implement read list of available plugins
    @staticmethod
    def getPreprocessors():
        return [{'name':'plain'}, {'name':'sleuthkit'}]

    def __init__(self, pOptions):
        self.__mLock = multiprocessing.Lock()
        self.__mResultArray = None

    def classify(self, pOptions, pCaller):

        lLast = datetime.datetime.now()
        logging.info(str(lLast) + " Start classifying.")

        lTypes = []
        if pOptions.recoverfiletype == "video":
            lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_H264,
                'mStrength': pOptions.strength})
        elif pOptions.recoverfiletype == "jpeg":
            lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_JPG,
                'mStrength': pOptions.strength})
        elif pOptions.recoverfiletype == "png":
            lTypes.append({'mType': fragment_context.FileType.FT_HIGH_ENTROPY,
                'mStrength': pOptions.strength})
            lTypes.append({'mType': fragment_context.FileType.FT_PNG,
                'mStrength': pOptions.strength})

        if pOptions.multiprocessing == True:

            # TODO load dynamically
            if pOptions.preprocess == "sleuthkit":
                if pOptions.fstype != "":
                    lPreprocessor = tsk_context.CTskImgProcessor(pOptions)
                else:
                    lPreprocessor = plain_context.CPlainImgProcessor(pOptions)
            else:
                lPreprocessor = plain_context.CPlainImgProcessor(pOptions)

            lManager = multiprocessing.Manager()
            lHeadersList = lManager.list()
            lBlocksList = lManager.list()
            lProcesses = []
            lResultArray = multiprocessing.Array('i', \
                    [0 for i in \
                    range(lPreprocessor.getNumParallel(pOptions.maxcpus)) \
                    ])
        else:
            lHeadersList = []
            lBlocksList = []
            lResultArray = [0]

        lQueue = Queue.Queue()
        lResultThread = CResultThread(pCaller, lResultArray, lQueue)
        lResultThread.start()

        lFragments = None
        if pOptions.multiprocessing == True:
            for lCnt in range(lPreprocessor.getNumParallel(pOptions.maxcpus)):
                lProcess = multiprocessing.Process(target=self.classifyCore, \
                        args=(\
                   lCnt,
                   lPreprocessor,
                   lHeadersList,
                   lBlocksList,
                   lResultArray,
                   lTypes,
                   pOptions \
                           ))
                lProcesses.append(lProcess)
                lProcess.start()

            for lProcess in lProcesses:
                lProcess.join(1000000L)
            logging.info("Start gathering results ...")
            lBlocks = frags.CFrags(lHeadersList, lBlocksList)
            logging.info("Finished gathering results.")
            # initialize fragmentizer with parameters that describe
            # the most important properties for blocks => fragments
            # conversions
            logging.info("Starting fragmentizing.")
            lFragmentizer = fragmentizer_context.CFragmentizer()
            lFragments = lFragmentizer.defrag(lBlocks,
                    pOptions.fragmentsize, pOptions.blockgap,
                    pOptions.minfragsize, pOptions.recoverfiletype)
            logging.info("Finished fragmentizing.")
        else:
            lClassifier = fragment_context.CFragmentClassifier()
            #lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
            lSize = os.path.getsize(pOptions.imagefile)
            lFragsTotal = lSize / pOptions.fragmentsize
            lFragments = lClassifier.classify(pOptions.fragmentsize,
                    lFragsTotal, pOptions.imagefile, lTypes,
                    pOptions.maxcpus)

        lNow = datetime.datetime.now()
        logging.info("Finished classifying. Duration: " + \
                str(lNow - lLast))

        lQueue.put(True)
        lResultThread.join()

        return lFragments

    def classifyCore(self, pPid, pPreprocessor, pHeadersList,
            pBlocksList, pResultArray, pTypes, pOptions):
        # data structure for temporary storage of results
        lMagic = magic_context.CMagic(pOptions.recoverfiletype)
        # do not change this: the fragment classifier cannot be pickled on
        # windows; so it has to be instantiated separately in each
        # process/thread
        try:
            lFC = fragment_context.CBlockClassifier()
        except OSError, pExc:
            logging.error("")
            logging.error("Problem with importing a library: " + str(pExc))
            logging.error("Try making it with 'make' first.")
            logging.error("")
            return
        lFC.open(pOptions,
                pTypes)

        logging.info("PID " + str(pPid) + \
                " | Initializing fragment classifier: fragmentsize " + \
                str(pOptions.fragmentsize))
        lBlocks = frags.CFrags()

        for lBlock in pPreprocessor.getGenerator(pPid):
            # lBlock[0] ... offset
            # lBlock[1] ... bytes/data
            pResultArray[pPid] = 100 * pPreprocessor.getFragsRead(pPid) / \
                    pPreprocessor.getFragsTotal(pPid)
            # check for beginning of files using libmagic(3)
            # TODO create more abstract method that allows to pass searched
            #      filetype as a parameter
            lMagicResult = lMagic.determineMagic(lBlock[1])
            if lMagicResult == magic_context.CMagic.HEADER:
                lBlocks.addHeader(lBlock[0])

            # TODO ignore header fragments from other identifiable file types

            # generate a map of filetypes of fragments
            # TODO add block dependent on its filetype
            #      (instead of an int-value)
            elif lMagicResult == magic_context.CMagic.UNKNOWN and \
                    lFC.classify(lBlock[1]) > 0:
                lBlocks.addBlock(lBlock[0])

        lFC.free()
        logging.info("Process " + str(pPid) + " finished classifying")
        self.__mLock.acquire()
        # gather results (append to shared memory list)
        for lHeader in lBlocks.getHeaders():
            pHeadersList.append(lHeader)
        for lBlock in lBlocks.getBlocks():
            pBlocksList.append(lBlock)
        self.__mLock.release()
        logging.info("Process " + str(pPid) + " finished returning results")
