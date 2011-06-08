class CVideoFrags:
    def __init__(self):
        # pointers to elements of relevant fragments
        self.__mHeaders = []
        # offsets to relevant fragments
        self.__mFragments = []

    def getHeaderIterator(self):
        return CHeaderIterator(self.__mHeaders)

    def getFragmentIterator(self):
        return self.__mFragments

    def addHeader(self, pHeaderOffset):
        try:
            lIndex = self.__mFragments.index(pHeaderOffset)
            self.__mHeaders.append(lIndex)
        except ValueError:
            self.__mFragments.add(pHeaderOffset)
            lIndex = self.__mFragments.index(pHeaderOffset)
            self.__mHeaders.append(lIndex)

    def addFragment(self, pFragmentOffset):
        # TODO check if fragment has already been added
        try:
            lIndex = self.__mFragments.index(pFragmentOffset)
            return
        except ValueError:
            self.__mFragments.add(pFragmentOffset)

    class CHeaderIterator:
        # iterate through offsets that contain video headers
        # resolve indeces in headers to offsets in fragments
        def __init__(self, pHeaders):
           pass

       def next(self):
           pass
