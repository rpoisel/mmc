class CFragment:
    def __init__(self):
        self.mOffset = -1
        self.mNumBlocks = 1

class CFragmentizer:
    def __init__(self):
        pass

    def defrag(self, pVideoBlocks, pH264Fragments):
        lFragmentCur = CFragment()
        pH264Fragments.append(lFragmentCur)
        for lIdx in xrange(len(pVideoBlocks.getBlocks()) - 1):
            if pVideoBlocks.getBlocks()[lIdx] - pVideoBlocks.getBlocks()[lIdx + 1] < 16384:
                if lFragmentCur.mOffset == -1:
                    lFragmentCur.mOffset = pVideoBlocks.getBlocks()[lIdx]
                lFragmentCur.mNumBlocks += 1
            else:
                lFragmentCur = CFragment()
                pH264Fragments.append(lFragmentCur)
                
        
