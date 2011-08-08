import os

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
        self.__mVideoBlocks = frags.CFrags()
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier(pOptions.imagefile,
                pOptions.fragmentsize)
        
        # TODO load dynamically
        if pOptions.preprocess == "sleuthkit":
            self.__mPreprocessor = tsk_context.CTSKImgProcessor(pOptions)
        else:
            self.__mPreprocessor = plain_context.CPlainImgProcessor(pOptions)

    def getVideoBlocks(self):
        return self.__mVideoBlocks

    def classify(self, pCaller = None):
        # lBlock[0] ... offset
        # lBlock[1] ... bytes/data
        for lBlock in self.__mPreprocessor.getGenerator():
            #QtCore.QCoreApplication.processEvents()
            if 100 * self.__mPreprocessor.getFragsRead() / self.__mPreprocessor.getFragsTotal() % 10 == 0:
                pCaller.progressCallback(100 * self.__mPreprocessor.getFragsRead() / self.__mPreprocessor.getFragsTotal())
            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBlock[1]) == True:
                print("Found H.264-Header fragment.")
                self.__mVideoBlocks.addHeader(lBlock[0])

            # TODO ignore header fragments from other identifiable file types

            # generate a map of filetypes of fragments
            elif self.__mH264FC.classify(lBlock[1]) > 0:
                self.__mVideoBlocks.addBlock(lBlock[0])
