

class FTypes:
    UNKNOWN=0x0
    VIDEO=0x1
    TEXT=0x2


class CMagic:
    def __init__(self):
        pass

    def determineMagicType(self, pBuffer):
        if pBuffer[0:4] == '\x00\x00\x00\x01' and ord(pBuffer[4])&0x1F == 0x07:
            return FTypes.VIDEO
        return FTypes.UNKNOWN

    def determineMagicH264(self, pBuffer):
        lType = self.determineMagicType(pBuffer)
        if lType == FTypes.VIDEO:
            return True
        return False
