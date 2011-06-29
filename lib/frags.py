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
        if pHeaderOffset in self.__mBlocks:
            lIndex = self.__mBlocks.index(pHeaderOffset)
        else:
            self.__mBlocks.append(pHeaderOffset)
            lIndex = self.__mBlocks.index(pHeaderOffset)
        if lIndex not in self.__mHeaders:
            self.__mHeaders.append(lIndex)
            return True
        return False

    def addBlock(self, pBlockOffset):
        return pBlockOffset in self.__mBlocks
