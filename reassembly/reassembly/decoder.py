import subprocess
import platform

class CDecoder:
    @staticmethod
    def getDecoder(pOutputFormat):
        if pOutputFormat.find('.dd') != -1:
            return CCopyDecoder()
        elif pOutputFormat.find('.mkv') != -1 or \
                pOutputFormat.find('.jpg') != -1 or \
                pOutputFormat.find('.png') != -1:
            return CFFMpegDecoder()
        else:
            return None

class CFFMpegDecoder(CDecoder):
    def __init__(self):
        self.__mFFMpeg = None
        self.__mFH = None

    def open(self, pPath):
        if platform.system().lower() == "linux":
            self.__mFH = open("/dev/null", "w")
            self.__mFFMpeg = subprocess.Popen(
                    ["ffmpeg", "-y", "-i", "-", pPath], 
                    bufsize = 512, stdin = subprocess.PIPE, stdout = self.__mFH.fileno(), 
                    stderr = self.__mFH.fileno())
        else:
            self.__mFFMpeg = subprocess.Popen(
                    ["ffmpeg", "-y", "-i", "-", pPath], 
                    bufsize = 512, stdin = subprocess.PIPE, stdout = None, stderr = None)

    def write(self, pData):
        try:
            self.__mFFMpeg.stdin.write(pData)
        except IOError, pExc:
            pass

    def close(self):
        self.__mFFMpeg.communicate()
        try:
            self.__mFFMpeg.kill()
        except OSError:
            pass
        if self.__mFH != None:
            self.__mFH.close()


class CCopyDecoder(CDecoder):
    def __init__(self):
        self.__mFH = None

    def open(self, pPath):
        self.__mFH = open(pPath, "wb")
    
    def write(self, pData):
        self.__mFH.write(pData)
    
    def close(self):
        self.__mFH.close()
