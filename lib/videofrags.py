class CVideoFrags:
    def __init__(self):
        # pointers to elements of relevant fragments
        self.__mHeaders = []
        # offsets to relevant fragments
        self.__mFragments = []

    def getHeaderIterator(self):
        return CVideoFrags.CHeaderIterator(self.__mHeaders, self.__mFragments)

    def getFragmentIterator(self):
        return self.__mFragments

    def addHeader(self, pHeaderOffset):
        try:
            lIndex = self.__mFragments.index(pHeaderOffset)
            self.__mHeaders.append(lIndex)
        except ValueError:
            self.__mFragments.append(pHeaderOffset)
            lIndex = self.__mFragments.index(pHeaderOffset)
            try:
                lHeaderIdx = self.__mHeaders.index(lIndex)
                return False
            except ValueError:
                self.__mHeaders.append(lIndex)
                return True

    def addFragment(self, pFragmentOffset):
        # TODO check if fragment has already been added
        try:
            lIndex = self.__mFragments.index(pFragmentOffset)
            return False
        except ValueError:
            self.__mFragments.append(pFragmentOffset)
            return True

    class CHeaderIterator:
        # iterate through offsets that contain video headers
        # resolve indeces in headers to offsets in fragments
        def __init__(self, pHeaders, pFragments):
            self.__mHeaders = pHeaders
            self.__mFrags = pFragments
            self.__mIdx = 0

        def __iter__(self):
            return self

        def next(self):
            if self.__mIdx >= len(self.__mHeaders):
                raise StopIteration
            lOffset = self.__mFrags[self.__mHeaders[self.__mIdx]]
            self.__mIdx += 1
            return lOffset
