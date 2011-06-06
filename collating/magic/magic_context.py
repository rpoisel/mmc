import magic


class CMagic:
    def __init__(self):
        self.__mMagic = magic.open(magic.MAGIC_NONE)
        self.__mMagic.load()

    def determineMagicType(self, pBuffer):
        return self.__mMagic.buffer(pBuffer)

    def determineMagicH264(self, pBuffer):
        lType = self.determineMagicType(pBuffer)
        if lType.find("H.264") >= 0 and lType.find("video") >= 0:
            return True
        return False
