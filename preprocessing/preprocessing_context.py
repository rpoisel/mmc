import os
import math
import logging
import multiprocessing
import datetime

from preprocessing.tsk import tsk_context
from preprocessing.plain import plain_context
from preprocessing import fsstat_context
from collating.fragment import fragment_context
from collating.magic import magic_context
from lib import frags

#from PySide import QtCore


class CPreprocessing:

    # TODO implement read list of available plugins
    @staticmethod
    def getPreprocessors():
        return [{'name':'plain'}, {'name':'sleuthkit'}]

    def __init__(self, pOptions):
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier(pOptions.imagefile,
                pOptions.fragmentsize)
        self.__mLock = multiprocessing.Lock()

    #def getVideoBlocks(self):
        #return self.__mVideoBlocks

    def classify(self, pOptions, pCaller = None):
        lVideoBlocks = None #frags.CFrags()
        lNumCPUs = pOptions.maxcpus
        
        # TODO load dynamically
        if pOptions.preprocess == "sleuthkit":
            self.__mPreprocessor = tsk_context.CTSKImgProcessor(pOptions)
        else:
            self.__mPreprocessor = plain_context.CPlainImgProcessor(pOptions)


        lLast = datetime.datetime.now()
        logging.info(str(lLast) + " Start classifying.")
        lManager = multiprocessing.Manager()
        lHeadersList = lManager.list()
        lBlocksList = lManager.list()
        lProcesses = []

        lProgress = 0

        for lCnt in range(self.__mPreprocessor.getNumParallel()):
            lProcess = multiprocessing.Process(target=self.__classifyCore, args=(lCnt, lHeadersList, lBlocksList, pCaller))
            lProcesses.append(lProcess)
            lProcess.start()

        for lProcess in lProcesses:
            lProcess.join(10000000000L)
            lProgress += (90 / len(lProcesses))
            pCaller.progressCallback(lProgress)

        logging.info("Start gathering results ...")
        lVideoBlocks = frags.CFrags(lHeadersList, lBlocksList)
        #lVideoBlocks = frags.CFrags()
        lNow = datetime.datetime.now()
        logging.info("Finished gathering results.")
        logging.info("Finished classifying. Duration: " + str(lNow - lLast))
        return lVideoBlocks

    def __classifyCore(self, pPid, pHeadersList, pBlocksList, pCaller):
        # data structure for temporary storage of results
        lBlocks = frags.CFrags()
        lDebug = []

        # lBlock[0] ... offset
        # lBlock[1] ... bytes/data
        for lBlock in self.__mPreprocessor.getGenerator(pPid):
            #if pPid == 0:
                #if 100 * self.__mPreprocessor.getFragsRead(pPid) / self.__mPreprocessor.getFragsTotal(pPid) % 10 == 0:
                    #pCaller.progressCallback(100 * self.__mPreprocessor.getFragsRead(pPid) / self.__mPreprocessor.getFragsTotal(pPid))
            lDebug.append(lBlock)
            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBlock[1]) == True:
                #print("Found H.264-Header fragment.")
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
