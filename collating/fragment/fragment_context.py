import platform
from ctypes import *


class FileType:
    FT_JPG = 0
    FT_PNG = 1
    FT_DOC = 2
    FT_PDF = 3
    FT_H264 = 4
    FT_TXT = 5
    FT_HTML = 6
    FT_XML = 7
    FT_UNKNOWN = 8
    FT_HIGH_ENTROPY = 9
    FT_LOW_ENTROPY = 10
    FT_VIDEO = 11
    FT_IMAGE = 12


class ClassifyT(Structure):
    _fields_ = [ \
            ("mType", c_uint), \
            ("mStrength", c_int), \
            ("mIsHeader", c_int), \
            ]

ClassifyTArray = ClassifyT * 24


class CBlockOptions(Structure):
    pass


class CBlockOptions(Structure):
    _fields_ = [ \
            ("mOption1", c_char_p), \
            ("mOption2", c_char_p), \
            ("mOption3", c_char_p), \
            ("mOption4", c_char_p), \
            ("mOption5", c_char_p), \
            ("mSubOptions", POINTER(CBlockOptions)), \
            ]


CBlockOptionsPointer = POINTER(CBlockOptions)


class CClassifyHandler(Structure):
    _fields_ = []


CClassifyHandlerPointer = POINTER(CClassifyHandler)


class CFragmentStruct(Structure):
    _fields_ = [("mOffset", c_ulonglong),
            ("mSize", c_ulonglong),
            ("mNextIdx", c_longlong),
            ("mIsHeader", c_int),
            ("mPicBegin", c_char_p),
            ("mPicEnd", c_char_p),
            ("mIsSmall", c_int)]

    def __str__(self):
        lString = str(self.mOffset) + " / " + str(self.mSize)
        if self.mIsHeader:
            lString += " | Header"
        if self.mNextIdx >= 0:
            lString += " | NextIdx " + str(self.mNextIdx)
        return lString


CFragmentStructPointer = POINTER(CFragmentStruct)


class CFragmentCollection(Structure):
    _fields_ = [("mNumFrags", c_ulonglong),
            ("mMaxFrags", c_ulonglong),
            ("mFrags", CFragmentStructPointer)]


CFragmentCollectionPointer = POINTER(CFragmentCollection)


class CFragments(object):

    def __init__(self, pCollection, pDestructor):
        super(CFragments, self).__init__()
        self.__mCollection = pCollection
        self.__mDestructor = pDestructor

    def __getitem__(self, pKey):
        return self.__mCollection.contents.mFrags[pKey]

    def __len__(self):
        return self.__mCollection.contents.mNumFrags

    def __iter__(self):
        for lCnt in xrange(self.__mCollection.contents.mNumFrags):
            yield self.__mCollection.contents.mFrags[lCnt]

    def __del__(self):
        if self.__mCollection != None:
            self.__mDestructor(self.__mCollection)
        self.__mCollection = None


class CBlockClassifier:

    def __init__(self):
        # open library handle
        lLibname = r"libfragment_classifier"
        if platform.system().lower() == "windows":
            lLibname += ".dll"
        elif platform.system().lower() == "linux":
            lLibname += ".so"
        self.__mLH = cdll.LoadLibrary(lLibname)

        self.__mOpen = self.__mLH.fragment_classifier_new_ct
        self.__mOpen.restype = CClassifyHandlerPointer
        self.__mOpen.argtypes = \
            [CBlockOptionsPointer, c_uint, c_uint, ClassifyTArray, c_uint]

        self.__mFree = self.__mLH.fragment_classifier_free
        self.__mFree.restype = None
        self.__mFree.argtypes = \
            [CClassifyHandlerPointer]

        self.__mClassify = self.__mLH.fragment_classifier_classify
        self.__mClassify.restype = CFragmentCollectionPointer
        self.__mClassify.argtypes = \
            [CClassifyHandlerPointer, c_char_p, c_int]

    def open(self, pOptions, pTypes):
        lCnt = 0
        lTypes = ClassifyTArray()
        for lType in pTypes:
            lTypes[lCnt].mType = lType['mType']
            lTypes[lCnt].mStrength = lType['mStrength']
            lCnt += 1
        self.__mCH = self.__mOpen(None, 0, pOptions.fragmentsize, lTypes, lCnt)

    def free(self):
        self.__mFree(self.__mCH)

    def classify(self, pBuffer):
        return self.__mClassify(self.__mCH, pBuffer, len(pBuffer))


class CFragmentClassifier(object):

    def __init__(self):
        super(CFragmentClassifier, self).__init__()

        # load library
        lLibname = r"libblock_reader"
        if platform.system().lower() == "windows":
            lLibname += ".dll"
        elif platform.system().lower() == "linux":
            lLibname += ".so"
        self._mLH = cdll.LoadLibrary(lLibname)

        self._mClassify = self._mLH.classify
        self._mClassify.restype = CFragmentCollectionPointer
        self._mClassify.argtypes = \
            [c_int, c_int, c_char_p, c_ulonglong, \
            ClassifyTArray, c_int, c_ulonglong, c_ulonglong, c_int]

        self._mClassifyFree = self._mLH.classify_free
        self._mClassifyFree.restype = None
        self._mClassifyFree.argtypes = \
            [CFragmentCollectionPointer]

    def classify(self, pBlockSize, pNumBlocks, pImage,
            pOffset, pTypes, pBlockGap, pMinFragSize,
            pNumThreads):
        lCnt = 0
        lTypes = ClassifyTArray()
        for lType in pTypes:
            lTypes[lCnt].mType = lType['mType']
            lTypes[lCnt].mStrength = lType['mStrength']
            lCnt += 1
        return CFragments(self._mClassify(pBlockSize, pNumBlocks,
                pImage, pOffset, lTypes, lCnt, pBlockGap,
                pMinFragSize, pNumThreads), self._mClassifyFree)
