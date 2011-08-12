from lib import frags

if __name__ == "__main__":
    lFrags = frags.CFrags()
    #lFrags = {}
    lHeaders = []
    lHeadersFH = open('headers.txt', 'r')
    lBlocksFH = open('blocks.txt', 'r')

    while True:
        lLine = lHeadersFH.readline()
        if lLine == '':
            break
        #if int(lLine.strip()) in lFrags:
            #lHeaders.append(int(lLine.strip()))
        lFrags.addHeader(int(lLine.strip()))
    while True:
        lLine = lBlocksFH.readline()
        if lLine == '':
            break
        #lFrags[int(lLine.strip())] = True
        lFrags.addBlock(int(lLine.strip()))
    
    lBlocks = sorted(lFrags.getBlocks())
    print("Number of blocks: " + str(len(lFrags.getBlocks())))
    print("Headers: ")
    for lHeader in lFrags.getHeaders():
        print(lHeader)

    lHeadersFH.close()
    lBlocksFH.close()
