# -*- coding: utf-8 -*-

"""The user interface for our app"""


import os
import sys
# PyQt4, PySide stuff
from qtimport import *

# Import the compiled UI module
from file_carving_ui import Ui_filecarvingWidget
from mainwindow import Ui_MainWindow


# Create a class for our main window
class Gui_Qt(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Gui_Qt, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.widget = QtGui.QWidget()
        lUI = Ui_filecarvingWidget()
        lUI.setupUi(self.widget)

        self.setCentralWidget(self.widget)

        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered(bool)"),
                     self.on_actionExit_triggered)
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered(bool)"),
                     self.on_actionAbout_triggered)

    def on_actionExit_triggered(self, pChecked=None):
        if pChecked is None:
            return
        self.close()

    def on_actionAbout_triggered(self, pChecked=None):
        QtGui.QMessageBox.about(self, "FREDI",
            "Forensics Recommendation Engine for Digital Investigators")


class CMain:
    def __init__(self):
        if gUsePyQt:
            self.__mApp = QtGui.QApplication(sys.argv)
        else:
            # unicode issue work-around for PySide
            self.__mApp = QtGui.QApplication("nothing")

        self.__mWindow = Gui_Qt()

    def run(self):
        self.__mWindow.show()
        lReturn = self.__mApp.exec_()
        sys.exit(lReturn)


def main():
    lMain = CMain()
    lMain.run()

if __name__ == "__main__":
    main()
