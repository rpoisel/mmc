from lib.frags import CFragmentFactory


class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pBlocks, pBlockSize, pBlockGap,
            pMinFragSize, pType):
        lFragments = []
        lBlocks = sorted(pBlocks.getBlocks().keys())
        lHeaders = pBlocks.getHeaders()

        # only do this if we found some video fragments
        if len(lBlocks) == 0:
            return lFragments

        # first do the block building
        lFragmentCur = CFragmentFactory.getFragment(pType, pBlockSize)
        for lIdx in xrange(len(lBlocks)):
            if lBlocks[lIdx] in lHeaders:  # header fragment
                lFragmentCur = CFragmentFactory.getFragment(pType, pBlockSize)
                # start new header-fragment
                lFragmentCur.mIsHeader = True
                lFragmentCur.mOffset = lBlocks[lIdx]
                lFragments.append(lFragmentCur)
            elif lFragmentCur.mOffset == -1:  # new no-header fragment
                lFragmentCur.mOffset = lBlocks[lIdx]
                lFragments.append(lFragmentCur)
            elif (lBlocks[lIdx] - \
                    (lFragmentCur.mOffset + lFragmentCur.mSize)) > pBlockGap:
                # fragment after header or new no-header with big gap
                lFragmentCur = CFragmentFactory.getFragment(pType, pBlockSize)
                lFragmentCur.mOffset = lBlocks[lIdx]
                lFragments.append(lFragmentCur)
            else:  # fragment after header or new no-header with small gap
                lFragmentCur.mSize = lBlocks[lIdx] - \
                        lFragmentCur.mOffset + pBlockSize

        return self.__reduce(lFragments, pBlockSize, pMinFragSize)

    def __reduce(self, pFragments, pBlockSize, pMultiplicator):
        return [lFrag for lFrag in pFragments \
                if lFrag.mIsHeader is True or \
                (lFrag.mIsHeader is False and \
                lFrag.mSize > (pBlockSize * pMultiplicator))]
