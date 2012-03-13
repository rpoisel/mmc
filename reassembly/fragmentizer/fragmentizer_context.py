from lib.frags import CFragment

class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pVideoBlocks, pBlockSize, pBlockGap, 
            pMinFragSize):
        lFragments = []
        lVideoBlocks = sorted(pVideoBlocks.getBlocks().keys())
        lVideoHeaders = pVideoBlocks.getHeaders()

        # only do this if we found some video fragments
        if len(lVideoBlocks) == 0:
            return lFragments

        # first do the block building
        lFragmentCur = CFragment(pBlockSize)
        for lIdx in xrange(len(lVideoBlocks)):
            if lVideoBlocks[lIdx] in lVideoHeaders: # header fragment
                lFragmentCur = CFragment(pBlockSize)
                # start new header-fragment
                lFragmentCur.mIsHeader = True
                lFragmentCur.mOffset = lVideoBlocks[lIdx]
                lFragments.append(lFragmentCur)
            elif lFragmentCur.mOffset == -1: # new no-header fragment
                lFragmentCur.mOffset = lVideoBlocks[lIdx]
                lFragments.append(lFragmentCur)
            elif (lVideoBlocks[lIdx] - \
                    (lFragmentCur.mOffset + lFragmentCur.mSize)) > pBlockGap: 
                # fragment after header or new no-header with big gap
                lFragmentCur = CFragment(pBlockSize)
                lFragmentCur.mOffset = lVideoBlocks[lIdx]
                lFragments.append(lFragmentCur)
            else: #fragment after header or new no-header with small gap
                lFragmentCur.mSize = lVideoBlocks[lIdx] - \
                        lFragmentCur.mOffset + pBlockSize

        return self.__reduce(lFragments, pBlockSize, pMinFragSize)

    def __reduce(self, pFragments, pBlockSize, pMultiplicator):
        return [lFrag for lFrag in pFragments \
                if lFrag.mIsHeader is True or \
                (lFrag.mIsHeader is False and lFrag.mSize > (pBlockSize * pMultiplicator))]
