# -*- coding: utf-8 -*-

"""The user interface for our app"""


import os
import sys
# PyQt4, PySide stuff
from qtimport import *

# Import the compiled UI module
from file_carving_ui import Ui_filecarvingWidget
from mainwindow import Ui_MainWindow
from mm_context import CContext
from gui_options import CGuiOptions


# Create a class for our main window
class Gui_Qt(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Gui_Qt, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.centralwidget = QtGui.QWidget()
        self.customwidget = Ui_filecarvingWidget()
        self.customwidget.setupUi(self.centralwidget)

        self.setCentralWidget(self.centralwidget)

        # adjust widget elements
        self.customwidget.preprocessing.addItem("none")
        self.customwidget.preprocessing.addItem("sleuthkit")

        self.customwidget.resultTable.setColumnCount(3)
        self.customwidget.resultTable.setHorizontalHeaderLabels(("Fragment", "Offset", "Size"))
        self.customwidget.resultTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.customwidget.resultTable.verticalHeader().setVisible(False)
        self.numRowsResult = 0

        self.customwidget.progressBar.setMaximum(100)
        self.customwidget.progressBar.setMinimum(0)

        # actions
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered(bool)"),
                self.on_actionExit_triggered)
        self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered(bool)"),
                self.on_actionAbout_triggered)
        self.connect(self.customwidget.processButton, QtCore.SIGNAL("clicked(bool)"),
                self.on_processButton_clicked)
        self.connect(self.customwidget.inputFileButton, QtCore.SIGNAL("clicked(bool)"),
                self.on_inputFileButton_clicked)
        self.connect(self.customwidget.outputDirButton, QtCore.SIGNAL("clicked(bool)"),
                self.on_outputDirButton_clicked)

    def on_actionExit_triggered(self, pChecked=None):
        if pChecked is None:
            return
        self.close()

    def on_actionAbout_triggered(self, pChecked=None):
        QtGui.QMessageBox.about(self, "FREDI",
            "Forensics Recommendation Engine for Digital Investigators")

    def on_inputFileButton_clicked(self, pChecked=None):
        lFilename = QtGui.QFileDialog.getOpenFileName(self, "Open Image", "~", "All Files (*)")
        self.customwidget.inputFile.setText(lFilename[0])

    def on_outputDirButton_clicked(self, pChecked=None):
        lDialog = QtGui.QFileDialog()
        lDialog.setFileMode(QtGui.QFileDialog.Directory)
        lFilename = lDialog.getExistingDirectory(self, "Open Output Directory", "", QtGui.QFileDialog.ShowDirsOnly)
        self.customwidget.outputDir.setText(lFilename)

    def on_processButton_clicked(self, pChecked=None):
        # start processing
        lOptions = CGuiOptions()
        if self.customwidget.preprocessing.currentText() == "sleuthkit":
            lOptions.preprocess = True
        else:
            lOptions.preprocess = False
        lOptions.imagefile = self.customwidget.inputFile.text()
        lOptions.output = self.customwidget.outputDir.text()
        lOptions.offset = int(self.customwidget.offset.text())
        lOptions.fragmentsize = int(self.customwidget.fragmentSize.text())
        lOptions.incrementsize = int(self.customwidget.incrementSize.text())
        lOptions.blockgap = int(self.customwidget.blockGap.text())
        lOptions.verbose = False
        lContext = CContext(self)
        lContext.run(lOptions)

    def on_result_callback(self, pOffset, pSize):
        self.customwidget.resultTable.insertRow(self.numRowsResult)

        lItem = QtGui.QTableWidgetItem("Fragment " + str(self.numRowsResult + 1))
        lItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.customwidget.resultTable.setItem(self.numRowsResult, 0, lItem)

        lItem = QtGui.QTableWidgetItem(str(pOffset))
        lItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.customwidget.resultTable.setItem(self.numRowsResult, 1, lItem)

        lItem = QtGui.QTableWidgetItem(str(pSize))
        lItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.customwidget.resultTable.setItem(self.numRowsResult, 2, lItem)

        self.numRowsResult += 1

    def on_progress_callback(self, pValue):
        if 0 <= pValue <= 100:
            self.customwidget.progressBar.setValue(pValue)


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
