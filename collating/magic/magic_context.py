import platform
import os

if platform.system().lower() == "windows":
    import magic_win32 as magic
else:
    import magic


class MagicDb:
    NONE = 0x0
    BASE_PATH = os.path.join("data", "magic")
    VIDEO = os.path.join(BASE_PATH, "animation.mgc")
    IMAGE_JPEG = os.path.join(BASE_PATH, "jpeg.mgc")
    IMAGE_PNG = os.path.join(BASE_PATH, "png.mgc")


class CMagic:
    def __init__(self, pType):
        self.mMagic = magic.open(magic.NONE)
        if pType != MagicDb.NONE:
            self.mMagic.load(pType)
        else:
            self.mMagic.load()

    def determineMagic(self, pBuffer):
        lMagic = self.mMagic.buffer(pBuffer)
        # exclude text based and unkown formats
        if lMagic == None or \
                lMagic.lower().find("text") != -1 or \
                lMagic == "data":
            return False
        return True
