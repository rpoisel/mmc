import os
import sys
import math
import logging
import multiprocessing
import datetime
import threading
import time
import Queue

from preprocessing.tsk import tsk_context
from preprocessing.plain import plain_context
from preprocessing import fsstat_context
try:
    from collating.fragment import fragment_context
except ImportError, pExc:
    logging.error("Problem with importing a library: " + str(pExc))
    logging.error("Try making it with 'make' first.")
    sys.exit(-1)
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
            self.__mCaller.progressCallback(lResults / len(self.__mResultArray))
            time.sleep(1)
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
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier(
                pOptions.reffragsdir,
                pOptions.fragmentsize)
        self.__mLock = multiprocessing.Lock()
        self.__mResultArray = None

    def classify(self, pOptions, pCaller):
        lNumCPUs = pOptions.maxcpus
        
        # TODO load dynamically
        if pOptions.preprocess == "sleuthkit":
            if pOptions.fstype != "":
                self.__mPreprocessor = tsk_context.CTskImgProcessor(pOptions)
            else:
                self.__mPreprocessor = plain_context.CPlainImgProcessor(pOptions)
        else:
            self.__mPreprocessor = plain_context.CPlainImgProcessor(pOptions)

        lLast = datetime.datetime.now()
        logging.info(str(lLast) + " Start classifying.")
        lManager = multiprocessing.Manager()
        lHeadersList = lManager.list()
        lBlocksList = lManager.list()
        lProcesses = []

        lQueue = Queue.Queue()
        lResultArray = multiprocessing.Array('i', [0 for i in range(self.__mPreprocessor.getNumParallel())])
        lResultThread = CResultThread(pCaller, lResultArray, lQueue)
        lResultThread.start()
        for lCnt in range(self.__mPreprocessor.getNumParallel()):
            lProcess = multiprocessing.Process(target=self.__classifyCore, args=(lCnt, lHeadersList, lBlocksList, lResultArray))
            lProcesses.append(lProcess)
            lProcess.start()

        for lProcess in lProcesses:
            lProcess.join(10000000000L)
        lQueue.put(True)
        lResultThread.join()

        logging.info("Start gathering results ...")
        lVideoBlocks = frags.CFrags(lHeadersList, lBlocksList)
        lNow = datetime.datetime.now()
        logging.info("Finished gathering results.")
        logging.info("Finished classifying. Duration: " + str(lNow - lLast))
        return lVideoBlocks

    def __classifyCore(self, pPid, pHeadersList, pBlocksList, pResultArray):
        # data structure for temporary storage of results
        lBlocks = frags.CFrags()

        # lBlock[0] ... offset
        # lBlock[1] ... bytes/data
        for lBlock in self.__mPreprocessor.getGenerator(pPid):
            pResultArray[pPid] = 100 * self.__mPreprocessor.getFragsRead(pPid) / self.__mPreprocessor.getFragsTotal(pPid)
            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBlock[1]) == True:
                lBlocks.addHeader(lBlock[0])

            # TODO ignore header fragments from other identifiable file types

            # generate a map of filetypes of fragments
            elif self.__mH264FC.classify(lBlock[1]) > 0:
                lBlocks.addBlock(lBlock[0])

        logging.info("Process " + str(pPid) + " finished classifying")
        self.__mLock.acquire()
        # gather results (append to shared memory list)
        for lHeader in lBlocks.getHeaders():
            pHeadersList.append(lHeader)
        for lBlock in lBlocks.getBlocks():
            pBlocksList.append(lBlock)
        self.__mLock.release()
        logging.info("Process " + str(pPid) + " finished returning results")
