import magic


class CMagic:
    def __init__(self):
        self.__mMagic = magic.open(magic.MAGIC_NONE)
        self.__mMagic.load()

    def determineMagicType(self, pBuffer):
        return self.__mMagic.buffer(pBuffer)

    def determineMagicH264(self, pBuffer):
        lType = self.determineMagicType(pBuffer)
        if type(lType) == str:
            if lType.lower().find("video") >= 0:
                return True
            elif lType.find("MPEG v4 system") >= 0:
                return True
        return False
