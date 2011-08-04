import copy

class CFragment:
    def __init__(self, pBlockSize):
        self.mOffset = -1
        self.mSize = pBlockSize
        self.mIsHeader = False

    def __str__(self):
        lString = str(self.mOffset) + " / " + str(self.mSize)
        if self.mIsHeader:
            lString += " | Header"
        return lString

class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pVideoBlocks, pH264Fragments, pBlockSize, pBlockGap, 
            pMinFragSize):
        # only do this if we found some video fragments
        if len(pVideoBlocks.getBlocks()) == 0:
            return

        # first do the block building
        lFragmentCur = CFragment(pBlockSize)
        #pH264Fragments.append(lFragmentCur)
        for lIdx in xrange(len(pVideoBlocks.getBlocks())):
            if pVideoBlocks.getBlocks()[lIdx] in pVideoBlocks.getHeaders(): # header fragment
                lFragmentCur = CFragment(pBlockSize)
                # start new header-fragment
                lFragmentCur.mIsHeader = True
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                pH264Fragments.append(lFragmentCur)
            elif lFragmentCur.mOffset == -1: # new no-header fragment
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                pH264Fragments.append(lFragmentCur)
            elif (pVideoBlocks.getBlocks()[lIdx] - \
                    (lFragmentCur.mOffset + lFragmentCur.mSize)) > pBlockGap: 
                # fragment after header or new no-header with big gap
                lFragmentCur = CFragment(pBlockSize)
                lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                pH264Fragments.append(lFragmentCur)
            else: #fragment after header or new no-header with small gap
                lFragmentCur.mSize = pVideoBlocks.getBlocks()[lIdx] - \
                        lFragmentCur.mOffset + pBlockSize

        self.__reduce(pH264Fragments, pBlockSize, pMinFragSize)

    def __reduce(self, pH264Fragments, pBlockSize, pMultiplicator):
        for lFragment in pH264Fragments:
            if lFragment.mIsHeader is False and \
                    lFragment.mSize <= (pBlockSize * pMultiplicator):
                pH264Fragments.remove(lFragment)
