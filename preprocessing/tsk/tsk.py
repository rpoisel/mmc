

class CTSKblkls(object):
    def __init__(self):
        self.imageoffset = 0
        self.filename = ''
        self.fstype = ''
        self.imagetype = ''
        self.sectorsize = -1
        self.list = True
        self.start = -1
        self.stop = -1
        
    def getAll(self):
        pass
    
    def getUnallocated(self):
        command = []
        command.append('blkls') # Name of the blkls command
        command.append('-A')
        
#        if self.fstype:
#            command.append('-f')
#            command.append(str(self.fstype))
        
        if self.imagetype:
            command.append('-i')
            command.append(str(self.imagetype))
        
        if self.imageoffset > 0:
            command.append('-o')
            command.append(str(self.imageoffset))
        
        if self.sectorsize > 0:
            command.append('-b')
            command.append(str(self.sectorsize))
        
        if self.list:
            command.append('-l')
        
        command.append(self.filename)
        
        if self.start > 0 and self.stop > 0:
            command.append(str(self.start) + "-" + str(self.stop))
        
        return command
    
    def getAllocated(self):
        command = []
        command.append('blkls') # Name of the blkls command
        command.append('-a')
        
#        if self.fstype:
#            command.append('-f')
#            command.append(str(self.fstype))
        
        if self.imagetype:
            command.append('-i')
            command.append(str(self.imagetype))
        
        if self.imageoffset >= 0:
            command.append('-o')
            command.append(str(self.imageoffset))
        
        if self.sectorsize >= 0:
            command.append('-b')
            command.append(str(self.sectorsize))
        
        if self.list:
            command.append('-l')
        
        command.append(self.filename)
        
        if self.start >= 0 and self.stop >= 0:
            command.append(str(self.start) + '-' + str(self.stop))
        
        return command
