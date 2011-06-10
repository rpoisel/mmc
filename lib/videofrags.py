class CVideoFrags:
    def __init__(self):
        # pointers to elements of relevant fragments
        self.__mHeaders = []
        # offsets to relevant fragments
        self.__mFragments = []

    def getHeaders(self):
        lHeaders = []
        for lFragmentIdx in self.__mHeaders:
            lHeaders.append(self.__mFragments[lFragmentIdx])
        return lHeaders

    def getFragments(self):
        return self.__mFragments

    def addHeader(self, pHeaderOffset):
        # determine if fragment exists
        lIndex = 0
        try:
            lIndex = self.__mFragments.index(pHeaderOffset)
        except ValueError:
            self.__mFragments.append(pHeaderOffset)
            lIndex = self.__mFragments.index(pHeaderOffset)
            self.__mHeaders.append(lIndex)
            return True
        # determine if index in headers exists
        try:
            lHdrIdx = self.__mHeaders.index(lIndex)
        except ValueError:
            self.__mHeaders.append(lIndex)
            return True
        return False

    def addFragment(self, pFragmentOffset):
        try:
            lIndex = self.__mFragments.index(pFragmentOffset)
            return False
        except ValueError:
            self.__mFragments.append(pFragmentOffset)
            return True
