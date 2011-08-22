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

class CFragment:
    def __init__(self, pBlockSize):
        self.mOffset = -1
        self.mSize = pBlockSize
        self.mIsHeader = False
        self.mPicBegin = ""
        self.mPicEnd = ""
        self.mNextIdx = -1
        self.mIsSmall = False


    def __str__(self):
        lString = str(self.mOffset) + " / " + str(self.mSize)
        if self.mIsHeader:
            lString += " | Header"
        if self.mNextIdx >= 0:
            lString += " | NextIdx " + str(self.mNextIdx)
        if self.mPicBegin != "":
            lString += " | PicBegin " + self.mPicBegin
        if self.mPicEnd != "":
            lString += " | PicEnd " + self.mPicEnd
        return lString

