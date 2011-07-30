import os
import sys
from PySide import QtGui, QtCore, QtUiTools
import gui_resources


class Gui_Qt(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Gui_Qt, self).__init__(parent)

        lLoader = QtUiTools.QUiLoader()
        lFile = QtCore.QFile(":/forms/file_carving_ui.ui")
        lFile.open(QtCore.QFile.ReadOnly)
        self.customwidget = lLoader.load(lFile, self)
        lFile.close()
        self.setCentralWidget(self.customwidget)


class CMain:
    def __init__(self):
        self.__mApp = QtGui.QApplication(sys.argv)
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
