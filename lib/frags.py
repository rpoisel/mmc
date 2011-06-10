class CFrags:
    def __init__(self):
        # pointers to elements of relevant blocks
        self.__mHeaders = []
        # offsets to relevant blocks
        self.__mBlocks = []

    def getHeaders(self):
        lHeaders = []
        for lBlockIdx in self.__mHeaders:
            lHeaders.append(self.__mBlocks[lBlockIdx])
        return lHeaders

    def getBlocks(self):
        return self.__mBlocks

    def addHeader(self, pHeaderOffset):
        # determine if block exists
        lIndex = 0
        try:
            lIndex = self.__mBlocks.index(pHeaderOffset)
        except ValueError:
            self.__mBlocks.append(pHeaderOffset)
            lIndex = self.__mBlocks.index(pHeaderOffset)
        # determine if index in headers exists
        try:
            lHdrIdx = self.__mHeaders.index(lIndex)
        except ValueError:
            self.__mHeaders.append(lIndex)
            return True
        return False

    def addBlock(self, pBlockOffset):
        try:
            lIndex = self.__mBlocks.index(pBlockOffset)
            return False
        except ValueError:
            self.__mBlocks.append(pBlockOffset)
            return True
