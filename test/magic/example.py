#! /usr/bin/python

import magic_win32 as magic

ms = magic.open(magic.NONE)
ms.load(r"..\..\data\magic\animation.mgc")

f = open(r"c:\temp\FVDO_Shore_qcif.h264", "rb")
buf = f.read(4096)
f.close()

tp = ms.buffer(buf)
print (tp)

ms.close()
