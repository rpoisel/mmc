import subprocess
import os
import platform


class CDecoder(object):
    @staticmethod
    def getDecoder(pInputFormat, pOutputFormat=None):
        if pOutputFormat != None and pOutputFormat.find('.dd') != -1:
            return CCopyDecoder()
        elif pInputFormat.find("video") != -1:
            return CFFMpegDecoder()
        elif pInputFormat.find("jpg") != -1:
            return CJpegDecoder()
        elif pInputFormat.find("jpeg") != -1:
            return CJpegDecoder()
        else:
            return None

    def open(self, pPath):
        pass

    def write(self, pData):
        pass

    def close(self):
        pass


class CJpegDecoder(CDecoder):
    def __init__(self):
        self.__mJpeg = None
        self.__mFH = None
        self.__mJpegProc = None
        self.__mPngPath = None

    def open(self, pPath):
        self.__mPngPath = pPath
        self.__mJpeg = open(pPath.replace(".png", ".jpg"), 'w')

    def write(self, pData):
        self.__mJpeg.write(pData)

    def close(self):
        self.__mJpeg.close()
        if platform.system().lower() == "linux":
            self.__mFH = open("/dev/null", "w")
            self.__mJpegProc = subprocess.Popen(
                    ["convert", self.__mPngPath.replace(".png", ".jpg"),\
                     self.__mPngPath],
                    bufsize = 512, stdin = subprocess.PIPE,\
                    stdout = self.__mFH.fileno(),
                    stderr = self.__mFH.fileno())

        self.__mJpegProc.communicate()
        try:
            self.__mJpegProc.kill()
        except OSError:
            pass
        if self.__mFH != None:
            self.__mFH.close()


class CFFMpegDecoder(CDecoder):
    def __init__(self):
        self.__mPath = ""
        self.__mFFMpeg = None
        self.__mFH = None
        self.__mFhDump = None

    def open(self, pPath, pPathDump=None):
        self.__mPath = pPath
        if platform.system().lower() == "linux":
            self.__mFH = open("/dev/null", "w")
            self.__mFFMpeg = subprocess.Popen(
                    ["ffmpeg", "-y", "-i", "-", pPath],
                    bufsize=512,
                    stdin=subprocess.PIPE,
                    stdout=self.__mFH.fileno(),
                    stderr=self.__mFH.fileno())
        else:
            self.__mFH = open("NUL", "w")
            self.__mFFMpeg = subprocess.Popen(
                    ["bin" + os.sep + "ffmpeg.exe",
                        "-y", "-i", "-", pPath],
                    bufsize=512,
                    stdin=subprocess.PIPE,
                    stdout=self.__mFH.fileno(),
                    stderr=self.__mFH.fileno())
        if pPathDump != None:
            self.__mFhDump = open(pPathDump, "wb")

    def write(self, pData):
        try:
            self.__mFFMpeg.stdin.write(pData)
        except IOError, pExc:
            pass
        if self.__mFhDump != None:
            self.__mFhDump.write(pData)

    def close(self):
        self.__mFFMpeg.communicate()
        try:
            self.__mFFMpeg.kill()
        except OSError:
            pass
        if self.__mFH != None:
            self.__mFH.close()
        if self.__mFhDump != None:
            self.__mFhDump.close()


class CCopyDecoder(CDecoder):
    def __init__(self):
        self.__mFH = None

    def open(self, pPath):
        self.__mFH = open(pPath, "wb")

    def write(self, pData):
        self.__mFH.write(pData)

    def close(self):
        self.__mFH.close()
