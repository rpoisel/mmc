import multiprocessing

class CFrags:
    def __init__(self, pHeaders = [], pBlocks = []):
        # pointers to elements of relevant blocks
        self.__mHLock = multiprocessing.Lock()
        self.__mBLock = multiprocessing.Lock()
        self.__mHeaders = []
        self.__mBlocks = []
        for lHeader in pHeaders:
            self.addHeader(lHeader)
        # offsets to relevant blocks
        for lBlock in pBlocks:
            self.addBlock(lBlock)
        #self.__mHeaders = pHeaders
        #self.__mBlocks = pBlocks

    def getHeaders(self):
        lHeaders = []
        self.__mHLock.acquire()
        for lBlockIdx in self.__mHeaders:
            lHeaders.append(self.__mBlocks[lBlockIdx])
        self.__mHLock.release()
        return sorted(lHeaders)

    def getBlocks(self):
        self.__mBLock.acquire()
        lSorted = sorted(self.__mBlocks)
        self.__mBLock.release()
        return lSorted

    def addHeader(self, pHeaderOffset):
        # determine if block exists
        lIndex = 0
        self.__mBLock.acquire()
        if pHeaderOffset in self.__mBlocks:
            lIndex = self.__mBlocks.index(pHeaderOffset)
        else:
            self.__mBlocks.append(pHeaderOffset)
            lIndex = self.__mBlocks.index(pHeaderOffset)
        self.__mBLock.release()
        self.__mHLock.acquire()
        if lIndex not in self.__mHeaders:
            self.__mHeaders.append(lIndex)
            self.__mHLock.release()
            return True
        self.__mHLock.release()
        return False

    def addBlock(self, pBlockOffset):
        self.__mBLock.acquire()
        if pBlockOffset in self.__mBlocks:
            self.__mBLock.release()
            return True
        self.__mBlocks.append(pBlockOffset)
        self.__mBLock.release()
        return False
