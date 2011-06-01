import os
import ctypes


class CFragmentClassifier:

    sFragClassLib = "contexts/fragment/libfragment_context.so"

    def __init__(self):
        self.__mFragClassLib = ctypes.cdll.LoadLibrary(
                CFragmentClassifier.sFragClassLib)

    def determineH264(self, pBuffer):
        lStringBuf = ctypes.create_string_buffer(pBuffer)
        return self.__mFragClassLib.classify(lStringBuf, 
                len(pBuffer));
