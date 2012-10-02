# -*- coding: utf-8 -*-

"""The user interface for our app"""


import os
import sys
import platform
import logging
import datetime
import webbrowser

# PyQt4, PySide stuff
from PySide import QtCore
from PySide import QtGui
from PySide import QtXml
from PySide import QtUiTools

# Import the compiled UI module
import gui_resources

from jobs import Jobs
from worker import CThreadWorker
from preprocessing import fsstat
from filecarver import CFileCarver
from gui_options import CGuiOptions
from model_frags import CModelFrags
from model_files import CModelFiles
from preprocessing import preprocessing
from gui_imgvisualizer import CImgVisualizer


# Create a class for our main window
class CMain(object):

    def __init__(self, parent=None):
        super(CMain, self).__init__()

        self.__mApp = QtGui.QApplication(sys.argv)

        self.__mImgVisualizer = None
        self.__mLock = QtCore.QMutex()

        lLoader = QtUiTools.QUiLoader()

        self.ui = lLoader.load(":/forms/mainwindow.ui")
        self.customwidget = lLoader.load(":/forms/file_carving_ui.ui")
        self.mIcon = QtGui.QIcon(":/images/icon_mm_carver.png")

        self.ui.setWindowIcon(self.mIcon)
        self.ui.setCentralWidget(self.customwidget)

        self.mLoadMovie = QtGui.QMovie(":/images/loadinfo.gif")
        self.customwidget.progressLabel.setMovie(self.mLoadMovie)
        self.mLoadMovie.jumpToNextFrame()

        self.__mGeometry = None
        self.mFileCarver = None

        # adjust widget elements
        self.customwidget.imageView.setMouseTracking(True)

        self.customwidget.preprocessing.addItem("Sleuthkit")
        self.customwidget.preprocessing.addItem("Plain")

        self.mRecoverFiletypes = {"Video": ["MKV", "Copy", "JPEG", "PNG"],
                    "JPEG": ["JPEG", "PNG"],
                "PNG (not implemented)": ["PNG"]}

        for lFiletype in sorted(self.mRecoverFiletypes.keys()):
            self.customwidget.recoverfiletypes.addItem(lFiletype)
        self.customwidget.recoverfiletypes.setCurrentIndex(2)
        self.on_recoverFT_changed(
                self.customwidget.recoverfiletypes.itemText(2))

        for lCPU in reversed(range(CFileCarver.getCPUs())):
            self.customwidget.maxCPUs.addItem(str(lCPU + 1))

        self.customwidget.blockStatus.addItem("allocated")
        self.customwidget.blockStatus.addItem("unallocated")

        self.customwidget.resultTable.setSelectionBehavior(
                QtGui.QAbstractItemView.SelectRows)
        self.customwidget.resultTable.setSelectionMode(
                QtGui.QAbstractItemView.SingleSelection)
        #self.customwidget.resultTable.setContextMenuPolicy(
        #        QtCore.Qt.CustomContextMenu)
        self.customwidget.resultTable.horizontalHeader().\
                setResizeMode(QtGui.QHeaderView.Stretch)
        self.customwidget.resultTable.verticalHeader().setVisible(False)
        self.__actionExtractFragment = QtGui.QAction("Extract fragment ...",
                self.customwidget.resultTable,
                statusTip="Extract this fragment",
                triggered=self.on_fragmentExtract)

        self.customwidget.fileTable.setSelectionBehavior(
                QtGui.QAbstractItemView.SelectRows)
        self.customwidget.fileTable.setSelectionMode(
                QtGui.QAbstractItemView.SingleSelection)
        self.customwidget.fileTable.horizontalHeader().setResizeMode(
                QtGui.QHeaderView.Stretch)
        self.customwidget.fileTable.verticalHeader().setVisible(False)

        self.customwidget.progressBar.setMaximum(100)
        self.customwidget.progressBar.setMinimum(0)

        # signals and slots
        self.ui.actionExit.triggered.connect(self.on_actionExit_triggered)
        self.ui.actionAbout.triggered.connect(self.on_actionAbout_triggered)
        self.ui.actionChooseOutputDir.triggered.connect(
                self.on_outputDirButton_clicked)
        self.ui.actionOpenImage.triggered.connect(
                self.on_inputFileButton_clicked)
        self.customwidget.classifyButton.clicked.connect(
                self.on_classifyButton_clicked)
        self.customwidget.reassembleButton.clicked.connect(
                self.on_reassembleButton_clicked)
        self.customwidget.processButton.clicked.connect(
                self.on_processButton_clicked)
        self.customwidget.inputFileButton.clicked.connect(
                self.on_inputFileButton_clicked)
        self.customwidget.outputDirButton.clicked.connect(
                self.on_outputDirButton_clicked)
        self.customwidget.inputFile.textChanged.connect(
                self.on_inputFile_changed)
        self.customwidget.outputDir.textChanged.connect(
                self.on_outputDir_changed)
        self.customwidget.recoverfiletypes.\
                currentIndexChanged[unicode].connect(
                self.on_recoverFT_changed)
        self.customwidget.fileTable.doubleClicked.connect(
                self.on_fileTable_doubleClicked)
        #self.customwidget.resultTable.customContextMenuRequested.connect(
        #        self.on_result_contextMenuRequested)
        self.customwidget.resultTable.doubleClicked.connect(
                self.on_resultTable_doubleClicked)

        # init values
        self.customwidget.inputFile.setText(
                os.path.join(os.getcwd(), "data",
                    "image_ref_h264_ntfs_formatted.img"))
        self.customwidget.outputDir.setText(r"c:\temp"
                if platform.system().lower() == "windows" else "/tmp/temp")

    def on_fileTable_doubleClicked(self, pIndex):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file://" +
            self.mFileCarver.files[pIndex.row()].mFilePath))

    def on_resultTable_doubleClicked(self, pIndex):
        if self.customwidget.resultTable.currentIndex().row() < 0:
            return
        lFragment = self.mFileCarver.fragments[
                self.customwidget.resultTable.currentIndex().row()
                ]

        self.on_fragmentExtract(lFragment)

#    def on_result_contextMenuRequested(self, pPoint):
#        lMenu = QtGui.QMenu()
#        lAction = lMenu.addAction(self.__actionExtractFragment)
#        lMenu.exec_(self.customwidget.resultTable.mapToGlobal(pPoint))

    def on_actionExit_triggered(self):
        self.ui.close()

    def on_recoverFT_changed(self, pSelectedValue):
        lOutputFileTypes = self.mRecoverFiletypes[pSelectedValue]

        if lOutputFileTypes is None:
            return

        self.customwidget.outputformat.clear()
        for lOutputFiletype in lOutputFileTypes:
            self.customwidget.outputformat.addItem(lOutputFiletype)

        #Enable and Disable the specific Preprocessing Tab
        for lTabCnt in range(self.customwidget.tabWidgetReassembly.count()):
            if self.customwidget.tabWidgetReassembly.tabText(lTabCnt).upper() \
                    == pSelectedValue.upper():
                self.customwidget.tabWidgetReassembly.setTabEnabled(
                        lTabCnt, True)
            else:
                self.customwidget.tabWidgetReassembly.setTabEnabled(
                        lTabCnt, False)

        #Some Filetype specific value customizations
        lAssemblyMethods = ["Parallel Unique Path (PUP)"]

        #Get the Filetype specific Reassembly Algorithms
        self.customwidget.assemblyMethod.clear()
        if lAssemblyMethods is not None:
            for lAssembly in lAssemblyMethods:
                self.customwidget.assemblyMethod.addItem(lAssembly)

    def on_inputFile_changed(self, pPath):
        # TODO clear data that has been determined so far
        if os.path.exists(pPath):
            lOptions = self.__getOptions()
            self.__mGeometry = \
                    fsstat.CFsStat.getFsGeometry(lOptions)
            logging.info("FS Info: " + str(self.__mGeometry))
            self.customwidget.offset.setText(str(self.__mGeometry.offset))
            self.customwidget.fragmentSize.setText(
                    str(self.__mGeometry.blocksize))
            self.customwidget.fsInfo.setText(
                    "FS Info: " + str(self.__mGeometry))
            pass
        else:
            self.customwidget.fsInfo.setText(
                    "<html><font color=\"#FF0000\">"
                    "Imagefile does not exist.</font></html>")

    def on_outputDir_changed(self, pPath):
        if os.path.isdir(pPath):
            self.customwidget.outputDirInfo.setText("Output directory exists.")
        else:
            self.customwidget.outputDirInfo.setText(
                    "<html><font color=\"#FF0000\">"
                    "Output directory does not exist.</font></html>")

    def on_actionAbout_triggered(self, pChecked=None):
        QtGui.QMessageBox.about(self.ui,
            "Multimedia File Carver",
            "<html>Key developers:  \
            <ul> \
                <li>Rainer Poisel</li> \
                <li>Bernhard Schildendorfer</li> \
                <li>Manfred Ruzicka</li> \
                <li>Markus Mannel</li> \
                <li>Vasileios Miskos</li> \
            </ul> \
            &copy; 2011, 2012 St. Poelten University of Applied "
            "Sciences</html> \
            <p> \
            This software is released under the terms of the LGPLv3:<br /> \
            <a href=\"http://www.gnu.org/licenses/lgpl.html\">"
            "http://www.gnu.org/licenses/lgpl.html</a> \
            </p> \
            Regarding software required for running our file carver we "
            "kindly refer to their respective licenses: \
            <ul> \
            <li><a href=\"http://ffmpeg.org/legal.html\">FFmpeg</a></li> \
            <li><a href=\"http://www.sleuthkit.org/sleuthkit/licenses.php\">"
            "The Sleuth Kit</a></li> \
            </ul> \
            "
            )

    def on_inputFileButton_clicked(self, pChecked=None):
        lFilename = QtGui.QFileDialog.getOpenFileName(self.ui,
                "Choose Image",
                os.path.dirname(self.customwidget.inputFile.text()),
                "All Files (*)")
        if lFilename[0] != "":
            self.customwidget.inputFile.setText(lFilename[0])
#        Popen(["mmls", "/home/rpoisel/git/mmc/data/usbkey.dd"],
#                stdout=PIPE).communicate()[0].split('\n')

    def on_outputDirButton_clicked(self):
        lDialog = QtGui.QFileDialog()
        lDialog.setFileMode(QtGui.QFileDialog.Directory)
        lFilename = lDialog.getExistingDirectory(self.ui,
                "Choose output directory",
                os.path.dirname(self.customwidget.outputDir.text()),
                QtGui.QFileDialog.ShowDirsOnly)
        if lFilename != "":
            self.customwidget.outputDir.setText(lFilename)

    def on_processButton_clicked(self, pChecked=None):
        if not os.path.exists(self.customwidget.inputFile.text()):
            QtGui.QMessageBox.about(self.ui, "Error",
                "Please make sure that your input file exists.")
            return
        elif not os.path.isdir(self.customwidget.outputDir.text()):
            if self.__outputDirProblem() is False:
                return
        if self.__mLock.tryLock() is True:
            self.mLastTs = datetime.datetime.now()
            if self.mFileCarver is not None:
                self.mFileCarver.cleanup()
            self.mFileCarver = CFileCarver()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.CLASSIFY | Jobs.REASSEMBLE)

    def on_fragmentExtract(self, pFragment):
        # determine filename for extracted fragment
        lFilename = QtGui.QFileDialog.getOpenFileName(self.ui,
                "Choose File",
                os.path.dirname(self.customwidget.outputDir.text()),
                "All Files (*)")
        if lFilename[0] != "":
            if os.path.exists(lFilename[0]) is True:
                lMsgBox = QtGui.QMessageBox()
                lMsgBox.setText(
                        "<b>The file you want to write already exists!</b>")
                lMsgBox.setInformativeText("Do you want to overwrite it?")
                lButtonCancel = lMsgBox.addButton(
                        self.ui.tr("Cancel"),
                        QtGui.QMessageBox.ActionRole)
                lButtonOverwrite = lMsgBox.addButton(
                        self.ui.tr("Overwrite"),
                        QtGui.QMessageBox.ActionRole)
                lMsgBox.exec_()
                if lMsgBox.clickedButton() != lButtonOverwrite:
                    return
            try:
                self.mFileCarver.extractFragment(self.__getOptions(),
                        pFragment,
                        lFilename[0])
            except OSError, pExc:
                QtGui.QMessageBox.about(self.ui, "Error",
                        "Could not write to file. \n" + str(pExc))

    def __outputDirProblem(self):
        lMsgBox = QtGui.QMessageBox()
        lMsgBox.setText(
                "<b>The specified output directory does not exist. </b>")
        lMsgBox.setInformativeText("Do you want to create it?")
        lCreateButton = lMsgBox.addButton(self.ui.tr("Create directory"),
                QtGui.QMessageBox.ActionRole)
        lButtonCancel = lMsgBox.addButton(
                self.ui.tr("Cancel"),
                QtGui.QMessageBox.ActionRole)
        lMsgBox.exec_()
        if lMsgBox.clickedButton() == lCreateButton:
            try:
                os.makedirs(self.customwidget.outputDir.text())
                self.on_outputDir_changed(self.customwidget.outputDir.text())
            except OSError, pExc:
                QtGui.QMessageBox.about(self.ui, "Error",
                        "Could not create directory: \n" + str(pExc))
                return False
            return True
        return False

    def on_reassembleButton_clicked(self, pChecked=None):
        if len(self.mFileCarver.fragments) is 0:
            QtGui.QMessageBox.about(self.ui, "Error",
                "What would you like to reassemble? "
                        "No fragments have been classified yet!")
            return
        elif not os.path.isdir(self.customwidget.outputDir.text()):
            if self.__outputDirProblem() is False:
                return
        if self.__mLock.tryLock() is True:
            self.mLastTs = datetime.datetime.now()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.REASSEMBLE)

    def on_classifyButton_clicked(self, pChecked=None):
        if not os.path.exists(self.customwidget.inputFile.text()):
            QtGui.QMessageBox.about(self.ui, "Error",
                "Please make sure that your input file exists.")
            return
        if self.__mLock.tryLock() is True:
            self.mLastTs = datetime.datetime.now()
            if self.mFileCarver is not None:
                self.mFileCarver.cleanup()
            self.mFileCarver = CFileCarver()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.CLASSIFY)

    def __enableElements(self, pEnabled):
        self.customwidget.classifyButton.setEnabled(pEnabled)
        self.customwidget.reassembleButton.setEnabled(pEnabled)
        self.customwidget.processButton.setEnabled(pEnabled)
        # TODO add all elements that should be deactivated
        if pEnabled is True:
            self.mLoadMovie.stop()
            self.mLoadMovie.jumpToFrame(0)
        else:
            self.mLoadMovie.start()

    def __startWorker(self, pJobs):
        lOptions = self.__getOptions()
        self.__mWorker = CThreadWorker(lOptions, self.mFileCarver, pJobs)
        self.__mWorker.sBegin.connect(self.on_begin_callback,
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sProgress.connect(self.on_progress_callback,
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sFinished.connect(self.on_finished_callback,
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sError.connect(self.on_error_callback,
                QtCore.Qt.QueuedConnection)
        self.__enableElements(False)
        self.__mWorker.start(QtCore.QThread.IdlePriority)

    def __getOptions(self):
        # TODO rename fragmentsize to blocksize
        lOptions = CGuiOptions()
        lOptions.preprocess = self.customwidget.preprocessing.currentText()
        if self.customwidget.outputformat.currentText() == "PNG":
            if self.customwidget.recoverfiletypes.currentText().upper() == \
                    "VIDEO":
                lOptions.outputformat = "%08d.png"
            else:
                lOptions.outputformat = "picture.png"
        elif self.customwidget.outputformat.currentText() == "MKV":
            lOptions.outputformat = "movie.mkv"
        elif self.customwidget.outputformat.currentText() == "Copy":
            lOptions.outputformat = "movie.dd"
        else:
            if self.customwidget.recoverfiletypes.currentText().upper() == \
                    "VIDEO":
                lOptions.outputformat = "%08d.jpg"
            else:
                lOptions.outputformat = "picture.jpg"

        if self.customwidget.recoverfiletypes.currentText().upper() == "VIDEO":
            lOptions.recoverfiletype = "video"
            lOptions.similarity = int(self.customwidget.similarityVideo.text())
        elif self.customwidget.recoverfiletypes.currentText().upper() == \
                "JPEG":
            lOptions.recoverfiletype = "jpeg"
            lOptions.similarity = int(self.customwidget.similarityJpeg.text())
        elif self.customwidget.recoverfiletypes.currentText().upper() == "PNG":
            lOptions.recoverfiletype = "png"

        lOptions.strength = self.customwidget.strength.value()
        lOptions.showResults = self.customwidget.showResults.isChecked()
        lOptions.imagefile = self.customwidget.inputFile.text()
        lOptions.output = self.customwidget.outputDir.text()
        lOptions.offset = int(self.customwidget.offset.text())
        lOptions.imageoffset = int(self.customwidget.partitionOffset.text())
        lOptions.fragmentsize = int(self.customwidget.fragmentSize.text())
        lOptions.incrementsize = lOptions.fragmentsize
        lOptions.blockgap = int(self.customwidget.blockGap.text())
        lOptions.minfragsize = int(
                self.customwidget.minimumFragmentSize.text())
        lOptions.hdrsize = int(self.customwidget.headerSize.text())
        lOptions.extractsize = int(self.customwidget.extractSize.text()) * 1024
        lOptions.assemblymethod = \
                self.customwidget.assemblyMethod.currentText()
        lOptions.minpicsize = int(self.customwidget.minPicSize.text())
        #lOptions.similarity = int(self.customwidget.similarity.text())
        if self.customwidget.recoverfiletypes.currentText().upper() == "VIDEO":
            lOptions.recoverfiletype = "video"
            lOptions.similarity = int(self.customwidget.similarityVideo.text())
        elif self.customwidget.recoverfiletypes.currentText().upper() == \
                "JPEG":
            lOptions.recoverfiletype = "jpeg"
            lOptions.similarity = int(self.customwidget.similarityJpeg.text())
        elif self.customwidget.recoverfiletypes.currentText().upper() == "PNG":
            lOptions.recoverfiletype = "png"
        lOptions.blockstatus = self.customwidget.blockStatus.currentText()
        lOptions.maxcpus = int(self.customwidget.maxCPUs.currentText())
        if self.__mGeometry is not None:
            lOptions.fstype = self.__mGeometry.fstype
            lOptions.tskProps = self.__mGeometry.tskProperties
        else:
            lOptions.fstype = ''
        lOptions.verbose = False
        return lOptions

    def on_begin_callback(self, pJob, pSize, pOffset, pFsType):
        if pJob == Jobs.CLASSIFY:
            logging.info("Beginning classifying. Imagesize is " +
                    str(pSize) + " bytes.")
            self.__mImgVisualizer = CImgVisualizer(
                    self.mFileCarver, pSize, pOffset, pFsType,
                    self.customwidget.imageView)
            self.customwidget.imageView.setScene(self.__mImgVisualizer)
        elif pJob == Jobs.REASSEMBLE:
            logging.info("Beginning reassembling.")

    def on_progress_callback(self, pValue):
        lDelta = datetime.datetime.now() - self.mLastTs
        self.customwidget.duration.setText(str(lDelta))
        if 0 <= pValue <= 100:
            self.customwidget.progressBar.setValue(pValue)

    def on_finished_callback(self, pFinishedJob, pJobs, pError):
        lOptions = self.__getOptions()
        lDelta = datetime.datetime.now() - self.mLastTs
        self.customwidget.duration.setText(str(lDelta))

        # set model for fragments view
        lModelFrags = CModelFrags(self.mFileCarver.fragments)
        self.customwidget.resultTable.setModel(lModelFrags)

        if (pJobs & Jobs.REASSEMBLE == 0 and pFinishedJob == Jobs.CLASSIFY) \
                or (pFinishedJob == Jobs.REASSEMBLE):
            self.__enableElements(True)
            if pError is True:
                self.customwidget.reassembleButton.setEnabled(False)
            self.__mLock.unlock()

        if pFinishedJob == Jobs.REASSEMBLE and \
            lOptions.showResults is True:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(
                        "file://" + lOptions.output))
        if pFinishedJob == Jobs.CLASSIFY:
            logging.info("Classification finished. ")
        elif pFinishedJob == Jobs.REASSEMBLE:
            logging.info("Reassembling finished. ")

            # set model for files view
            lModelFiles = CModelFiles(self.mFileCarver.files)
            self.customwidget.fileTable.setModel(lModelFiles)

        self.__mImgVisualizer.update()

    def on_error_callback(self, pError):
        QtGui.QMessageBox.about(self.ui, "Error",
                "An error occured: " + pError)

    def run(self):
        self.ui.show()
        lReturn = self.__mApp.exec_()
        sys.exit(lReturn)
