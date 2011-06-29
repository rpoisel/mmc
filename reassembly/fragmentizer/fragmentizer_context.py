class CFragment:
    def __init__(self):
        self.mOffset = -1
        self.mNumBlocks = 1
        self.mIsHeader = False

class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pVideoBlocks, pH264Fragments, pBlockSize, pBlockGap):
        # only do this if we found some video fragments
        if len(pVideoBlocks.getBlocks()) == 0:
            return

        # first do the block building
        lFragmentCur = CFragment()
        pH264Fragments.append(lFragmentCur)
        for lIdx in xrange(len(pVideoBlocks.getBlocks()) - 1):
            # TODO check if currently investigated fragments are headers
            # and start a new fragment if so
            if pVideoBlocks.getBlocks()[lIdx] - \
                    pVideoBlocks.getBlocks()[lIdx + 1] <= pBlockGap:
                if lFragmentCur.mOffset == -1:
                    lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                    if lFragmentCur.mOffset in pVideoBlocks.getHeaders():
                        lFragmentCur.mIsHeader = True
                lFragmentCur.mNumBlocks += 1
            else:
                lFragmentCur = CFragment()
                pH264Fragments.append(lFragmentCur)
                
        # divide fragments at headers
        # TODO integrate this step into the previous one
        for lHeader in pVideoBlocks.getHeaders():
            for lFragment in pH264Fragments:
                if lFragment.mOffset < lHeader < (lFragment.mOffset + lFragment.mNumBlocks * pBlockSize):
                    lNumBlocksOld = (lHeader - lFragment.mOffset) / pBlockSize
                    lFragmentNew = CFragment()
                    lFragmentNew.mNumBlocks = lFragment.mNumBlocks - lNumBlocksOld
                    lFragmentNew.mOffset = lHeader
                    lFragment.mNumBlocks = lNumBlocksOld
                    pH264Fragments.append(lFragmentNew)

        
