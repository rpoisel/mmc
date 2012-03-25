import platform
import os

if platform.system().lower() == "windows":
    import magic_win as magic
else:
    import magic


class MagicDb:

    BASE_PATH = os.path.join("data", "magic")

    sSignatures = {'video': os.path.join(BASE_PATH, "animation.mgc"), \
            'jpeg': os.path.join(BASE_PATH, "jpeg.mgc"), \
            'png': os.path.join(BASE_PATH, "png.mgc")}


class CMagic:

    HEADER = 0
    IRRELEVANT = 1
    UNKNOWN = 2

    def __init__(self, pType):
        self.mMagic = magic.open(magic.MAGIC_NONE)
        if pType in MagicDb.sSignatures:
            self.mMagic.load(MagicDb.sSignatures[pType])
        else:
            self.mMagic.load()

    def determineMagic(self, pBuffer):
        lMagic = self.mMagic.buffer(pBuffer)
        # exclude text based and unkown formats
        if lMagic.lower().find("text") != -1:
            return CMagic.IRRELEVANT
        elif lMagic == "data":
            return CMagic.UNKNOWN
        return CMagic.HEADER
