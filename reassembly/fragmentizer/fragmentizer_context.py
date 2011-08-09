import copy

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

class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pVideoBlocks, pBlockSize, pBlockGap, 
            pMinFragSize):
        lH264Fragments = []
        # only do this if we found some video fragments
        if len(pVideoBlocks.getBlocks()) == 0:
            return lH264Fragments

        # first do the block building
        lFragmentCur = CFragment(pBlockSize)
        for lIdx in xrange(len(pVideoBlocks.getBlocks())):
            if pVideoBlocks.getBlocks()[lIdx] in pVideoBlocks.getHeaders(): # header fragment
                lFragmentCur = CFragment(pBlockSize)
                # start new header-fragment
                lFragmentCur.mIsHeader = True
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                lH264Fragments.append(lFragmentCur)
            elif lFragmentCur.mOffset == -1: # new no-header fragment
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                lH264Fragments.append(lFragmentCur)
            elif (pVideoBlocks.getBlocks()[lIdx] - \
                    (lFragmentCur.mOffset + lFragmentCur.mSize)) > pBlockGap: 
                # fragment after header or new no-header with big gap
                lFragmentCur = CFragment(pBlockSize)
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                lH264Fragments.append(lFragmentCur)
            else: #fragment after header or new no-header with small gap
                lFragmentCur.mSize = pVideoBlocks.getBlocks()[lIdx] - \
                        lFragmentCur.mOffset + pBlockSize

        return self.__reduce(lH264Fragments, pBlockSize, pMinFragSize)

    def __reduce(self, pH264Fragments, pBlockSize, pMultiplicator):
        return [lFrag for lFrag in pH264Fragments \
                if lFrag.mIsHeader is True or \
                (lFrag.mIsHeader is False and lFrag.mSize > (pBlockSize * pMultiplicator))]
