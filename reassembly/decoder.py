import subprocess
import os
import platform


class CDecoder(object):
    @staticmethod
    def getDecoder(pInputFormat):
        if pInputFormat.find('.dd') != -1:
            return CCopyDecoder()
        elif pInputFormat.find("video") != -1 or \
                pInputFormat.find(".mkv") != -1:
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
        self.__mJpegPath = pPath.replace(".png", ".jpg")
        #self.__mJpeg = open(self.__mJpegPath, 'w')

        if platform.system().lower() == "linux":
            lConvertPath = "convert"
            self.__mFH = open("/dev/null", "w")
        else:
            lConvertPath = os.path.join("bin", "convert")
            self.__mFH = open("NUL", "w")

        self.__mJpegProc = subprocess.Popen(
                [lConvertPath,
                    #self.__mJpegPath,
                    "-",
                    self.__mPngPath],
                bufsize=512,
                stdin=subprocess.PIPE,
                stdout=self.__mFH.fileno(),
                stderr=self.__mFH.fileno())

    def write(self, pData):
        try:
            self.__mJpegProc.stdin.write(pData)
        except IOError, pExc:
            pass
        #self.__mJpeg.write(pData)

    def close(self):
        #self.__mJpeg.close()

        try:
            self.__mJpegProc.communicate()
        except IOError:
            pass
        try:
            self.__mJpegProc.kill()
        except OSError:
            pass
        if self.__mFH is not None:
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
            lFFMpegPath = "ffmpeg"
            self.__mFH = open("/dev/null", "w")
        else:
            lFFMpegPath = os.path.join("bin", "ffmpeg")
            self.__mFH = open("NUL", "w")

        self.__mFFMpeg = subprocess.Popen(
                [lFFMpegPath, "-y", "-i", "-", pPath],
                bufsize=512,
                stdin=subprocess.PIPE,
                stdout=self.__mFH.fileno(),
                stderr=self.__mFH.fileno())

        if pPathDump is not None:
            self.__mFhDump = open(pPathDump, "wb")

    def write(self, pData):
        try:
            self.__mFFMpeg.stdin.write(pData)
        except IOError, pExc:
            pass
        if self.__mFhDump is not None:
            self.__mFhDump.write(pData)

    def close(self):
        try:
            self.__mFFMpeg.communicate()
        except IOError:
            pass
        try:
            self.__mFFMpeg.kill()
        except OSError:
            pass
        if self.__mFH is not None:
            self.__mFH.close()
        if self.__mFhDump is not None:
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
