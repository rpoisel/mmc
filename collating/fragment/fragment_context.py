import platform
from ctypes import *


class FileType:
    FT_UNKNOWN = 0
    FT_HIGH_ENTROPY = 1
    FT_LOW_ENTROPY = 2
    FT_TXT = 3
    FT_HTML = 4
    FT_XML = 5
    FT_JPG = 6
    FT_PNG = 7
    FT_DOC = 8
    FT_PDF = 9
    FT_H264 = 10
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
        self.__mClassify.restype = c_int
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


class CFragmentClassifier:

    def __init__(self):

        # load library
        lLibname = r"libblock_reader"
        if platform.system().lower() == "windows":
            lLibname += ".dll"
        elif platform.system().lower() == "linux":
            lLibname += ".so"
        self.__mLH = cdll.LoadLibrary(lLibname)

        self.__mClassify = self.__mLH.classify
        self.__mClassify.restype = c_int
        self.__mClassify.argtypes = \
            [c_int, c_int, c_char_p, ClassifyTArray, \
            c_int, c_int]

    def classify(self, pBlockSize, pNumBlocks, pImage,
            pTypes, pNumThreads):
        lCnt = 0
        lTypes = ClassifyTArray()
        for lType in pTypes:
            lTypes[lCnt].mType = lType['mType']
            lTypes[lCnt].mStrength = lType['mStrength']
            lCnt += 1
        return self.__mClassify(pBlockSize, pNumBlocks,
                pImage, lTypes, lCnt, pNumThreads)
