

class CFrags:
    def __init__(self, pHeaders=[], pBlocks=[]):
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


class CFragmentFactory:

    def __init__(self):
        pass

    @staticmethod
    def getFragment(pType, pBlockSize):
        if pType == "video":
            return CFragmentVideo(pBlockSize)
        elif pType == "jpeg":
            return CFragmentJpeg(pBlockSize)
        elif pType == "png":
            return CFragmentPng(pBlockSize)


# TODO work with properties: 
# http://adam.gomaa.us/blog/2008/aug/11/the-python-property-builtin/
class CFragment(object):
    def __init__(self, pBlockSize):
        self.mOffset = -1
        self.mSize = pBlockSize
        self.mNextIdx = -1
        self.mIsHeader = False

    def __str__(self):
        lString = str(self.mOffset) + " / " + str(self.mSize)
        if self.mIsHeader:
            lString += " | Header"
        if self.mNextIdx >= 0:
            lString += " | NextIdx " + str(self.mNextIdx)
        return lString


class CFragmentVideo(CFragment):

    def __init__(self, pBlockSize):
        super(CFragmentVideo, self).__init__(pBlockSize)
        self.mPicBegin = ""
        self.mPicEnd = ""
        self.mIsSmall = False

    def __str__(self):
        lString = super(CFragmentVideo, self).__str__()
        if self.mPicBegin != "":
            lString += " | PicBegin " + self.mPicBegin
        if self.mPicEnd != "":
            lString += " | PicEnd " + self.mPicEnd
        return lString


class CFragmentJpeg(CFragment):

    def __init__(self, pBlockSize):
        super(CFragmentJpeg, self).__init__(pBlockSize)
        # Bernhard: your properties here :-)

    def __str__(self):
        lString = super(CFragmentJpeg, self).__str__()
        return lString


class CFragmentPng(CFragment):

    def __init__(self, pBlockSize):
        super(CFragmentPng, self).__init__(pBlockSize)

    def __str__(self):
        lString = super(CFragmentPng, self).__str__()
        return lString
