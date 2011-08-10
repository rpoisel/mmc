import os
import multiprocessing

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
        self.__mVideoBlocks = None #frags.CFrags()
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier(pOptions.imagefile,
                pOptions.fragmentsize)
        self.__mNumCPUs = pOptions.maxcpus
        self.__mLock = multiprocessing.Lock()
        
        # TODO load dynamically
        if pOptions.preprocess == "sleuthkit":
            self.__mPreprocessor = tsk_context.CTSKImgProcessor(pOptions)
        else:
            self.__mPreprocessor = plain_context.CPlainImgProcessor(pOptions)

    def getVideoBlocks(self):
        return self.__mVideoBlocks

    def classify(self, pCaller = None):
        # TODO convert to multiprocessing
        #      move usage of generators back into the specific contexts {tsk,plain}_context
        #      only start the classification process here
        lManager = multiprocessing.Manager()
        lHeadersList = lManager.list()
        lBlocksList = lManager.list()
        lProcesses = []

        for lCnt in range(self.__mNumCPUs):
            lProcess = multiprocessing.Process(target=self.__classifyCore, args=(lCnt, lHeadersList, lBlocksList, pCaller))
            lProcesses.append(lProcess)
            lProcess.start()

        for lProcess in lProcesses:
            lProcess.join(10000000000L)

        self.__mVideoBlocks = frags.CFrags(lHeadersList, lBlocksList)

    def __classifyCore(self, pPid, pHeadersList, pBlocksList, pCaller):
        print("Classifying Process (%02d): PID " % pPid + str(os.getpid()))
        
        # data structure for temporary storage of results
        lBlocks = frags.CFrags()

        # lBlock[0] ... offset
        # lBlock[1] ... bytes/data
        for lBlock in self.__mPreprocessor.getGenerator(pPid):
            #if pPid == 0:
                #if 100 * self.__mPreprocessor.getFragsRead(pPid) / self.__mPreprocessor.getFragsTotal(pPid) % 10 == 0:
                    #pCaller.progressCallback(100 * self.__mPreprocessor.getFragsRead(pPid) / self.__mPreprocessor.getFragsTotal(pPid))
            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBlock[1]) == True:
                print("Found H.264-Header fragment.")
                lBlocks.addHeader(lBlock[0])

            # TODO ignore header fragments from other identifiable file types

            # generate a map of filetypes of fragments
            elif self.__mH264FC.classify(lBlock[1]) > 0:
                lBlocks.addBlock(lBlock[0])

        self.__mLock.acquire()
        # gather results (append to shared memory list)
        for lHeader in lBlocks.getHeaders():
            pHeadersList.append(lHeader)
        for lBlock in lBlocks.getBlocks():
            pBlocksList.append(lBlock)
        self.__mLock.release()
