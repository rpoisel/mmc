import sys
import os

from cx_Freeze import setup, Executable

lTarget = Executable(
    script = "gui/gui_fc.py",
    includes = ["PySide.QtCore","PySide.QtGui","PySide.QtXml", "magic"]
    ) 
include_files = [("collating/fragment/libfragment_classifier.so", "libfragment_classifier.so")]
setup(
    version = "0.9.5",
    description = "Multimedia File Carver",
    author = "Rainer Poisel",
    author_email = "rainer.poisel@fhstp.ac.at",
    name = "mmc",
    options = {"build_exe": {
                             "append_script_to_exe": True,
                             "create_shared_zip": False,
                             "include_files": include_files,
                            }
               },
    executables = [lTarget]
    )
