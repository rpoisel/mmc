import multiprocessing

# TODO implement thread-unsafe version of this class
class CFrags:
    def __init__(self, pHeaders = [], pBlocks = []):
        self.__mHeaders = {}
        self.__mBlocks = {}
        for lHeader in pHeaders:
            self.addHeader(lHeader)
        for lBlock in pBlocks:
            self.addBlock(lBlock)

    def getHeaders(self):
        return self.__mHeaders

    def getBlocks(self):
        return self.__mBlocks

    def addHeader(self, pHeaderOffset):
        self.__mHeaders[pHeaderOffset] = True
        self.addBlock(pHeaderOffset)

    def addBlock(self, pBlockOffset):
        self.__mBlocks[pBlockOffset] = True
