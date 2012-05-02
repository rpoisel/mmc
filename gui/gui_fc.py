# -*- coding: utf-8 -*-

"""The user interface for our app"""


import os
import sys
import platform
import multiprocessing
import datetime
import logging
# PyQt4, PySide stuff
from PySide import QtCore
from PySide import QtGui
from PySide import QtXml
from PySide import QtUiTools

# Import the compiled UI module
import gui_resources
import gui_options
import gui_imgvisualizer
from mm_context import CContext
from preprocessing import preprocessing_context
from preprocessing import fsstat_context
from reassembly.reassembly import reassembly_context


class Jobs(object):
    NONE = 0x0
    CLASSIFY = 0x1
    REASSEMBLE = 0x2


class CThreadWorker(QtCore.QThread):
    sBegin = QtCore.Signal(int, int, int, str)
    sProgress = QtCore.Signal(int)
    sFinished = QtCore.Signal(int, int)
    sError = QtCore.Signal(str)

    def __init__(self, pOptions, pContext, pJobs):
        super(CThreadWorker, self).__init__()
        self.mOptions = pOptions
        self.mContext = pContext
        self.mJobs = pJobs
        self.mRunningJob = Jobs.NONE
        self.mLastTs = datetime.datetime.now()

    def beginCallback(self, pSize, pOffset, pFsType):
        self.sBegin.emit(self.mRunningJob, pSize, pOffset, pFsType)

    def progressCallback(self, pProgress):
        if self.mJobs & Jobs.CLASSIFY == Jobs.CLASSIFY \
                and \
                self.mJobs & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
                    if self.mRunningJob & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
                        self.sProgress.emit(85 + pProgress * 0.15)
                    else:
                        self.sProgress.emit(pProgress * 0.85)
        else:
            self.sProgress.emit(pProgress)

    def finishedCallback(self):
        self.sFinished.emit(self.mRunningJob, self.mJobs)

    def run(self):
        if self.mJobs & Jobs.CLASSIFY == Jobs.CLASSIFY:
            self.mRunningJob = Jobs.CLASSIFY
            try:
                self.mContext.runClassify(self.mOptions, self)
            except OSError, pExc:
                logging.error(str(pExc) + ". Please make sure the "\
                        "classifier binaries are compiled. ")
                self.sError.emit(str(pExc) + ". Please make sure the "\
                        "classifier binaries are compiled. ")
                self.sFinished.emit(self.mRunningJob, self.mJobs)
            except Exception, pExc:
                logging.error(str(pExc))
                self.sError.emit(str(pExc))

        if self.mJobs & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
            self.mRunningJob = Jobs.REASSEMBLE
            self.mContext.runReassembly(self.mOptions, self)


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
        self.mContext = None

        # adjust widget elements
        self.customwidget.imageView.setMouseTracking(True)

        for lPreprocessor in \
                preprocessing_context.CPreprocessing.getPreprocessors():
            self.customwidget.preprocessing.addItem(lPreprocessor['name'])

        self.mRecoverFiletypes = {"Video": ["MKV", "Copy", "JPEG", "PNG"],
                    "JPEG": ["JPEG", "PNG"],
                "PNG (not implemented)": ["PNG"]}

        for lFiletype in sorted(self.mRecoverFiletypes.keys()):
            self.customwidget.recoverfiletypes.addItem(lFiletype)
        self.customwidget.recoverfiletypes.setCurrentIndex(2)
        self.on_recoverFT_changed(\
                self.customwidget.recoverfiletypes.itemText(2))

        for lCPU in reversed(range(CContext.getCPUs())):
            self.customwidget.maxCPUs.addItem(str(lCPU + 1))
        self.on_multiprocessing_changed(False)

        self.customwidget.blockStatus.addItem("allocated")
        self.customwidget.blockStatus.addItem("unallocated")

        self.customwidget.resultTable.setColumnCount(7)
        self.customwidget.resultTable.setHorizontalHeaderLabels((\
                "Header", "Fragment", "Start [B]",
                "End [B]", "Start [Sector]",
                "End [Sector]", "Size [B]"))
        self.customwidget.resultTable.horizontalHeader().\
                setResizeMode(QtGui.QHeaderView.Stretch)
        self.customwidget.resultTable.verticalHeader().setVisible(False)

        self.customwidget.fileTable.setColumnCount(4)
        self.customwidget.fileTable.setHorizontalHeaderLabels(("File",\
                "Filetype", "Size", "Path"))
        self.customwidget.fileTable.horizontalHeader().setResizeMode(\
                QtGui.QHeaderView.Stretch)
        self.customwidget.fileTable.verticalHeader().setVisible(False)

        self.customwidget.progressBar.setMaximum(100)
        self.customwidget.progressBar.setMinimum(0)

        #self.on_recoverFT_changed(0)

        # actions
        self.ui.actionExit.triggered.connect(self.on_actionExit_triggered)
        self.ui.actionAbout.triggered.connect(self.on_actionAbout_triggered)
        self.ui.actionChooseOutputDir.triggered.connect(\
                self.on_outputDirButton_clicked)
        self.ui.actionOpenImage.triggered.connect(\
                self.on_inputFileButton_clicked)
        self.customwidget.classifyButton.clicked.connect(\
                self.on_classifyButton_clicked)
        self.customwidget.reassembleButton.clicked.connect(\
                self.on_reassembleButton_clicked)
        self.customwidget.processButton.clicked.connect(\
                self.on_processButton_clicked)
        self.customwidget.inputFileButton.clicked.connect(\
                self.on_inputFileButton_clicked)
        self.customwidget.outputDirButton.clicked.connect(\
                self.on_outputDirButton_clicked)
        self.customwidget.inputFile.textChanged.connect(\
                self.on_inputFile_changed)
        self.customwidget.outputDir.textChanged.connect(\
                self.on_outputDir_changed)
        self.customwidget.recoverfiletypes.\
                currentIndexChanged[unicode].connect(\
                self.on_recoverFT_changed)
        self.customwidget.multiprocessing.stateChanged.connect(\
                self.on_multiprocessing_changed)
        self.customwidget.fileTable.cellDoubleClicked.connect(\
                self.on_fileTable_cellDoubleClicked)

        # init values
        self.customwidget.inputFile.setText(\
                os.path.join(os.getcwd(), "data",
                    "image_ref_h264_ntfs_formatted.img"))
        self.customwidget.outputDir.setText(r"c:\temp" \
                if platform.system().lower() == "windows" else "/tmp/temp")

    def on_fileTable_cellDoubleClicked(self, pRow, pColumn):
        lFile = self.customwidget.fileTable.item(pRow, 3).text()
        if lFile != None:
            webbrowser.open_new_tab(self.customwidget.fileTable.item(pRow, \
                    3).text())

    def on_multiprocessing_changed(self, pState):
        self.customwidget.maxCPUs.setEnabled(pState)
        #self.customwidget.maxCPUs.setCurrentIndex(0)
#        if pState == False:
#            self.customwidget.maxCPUs.setCurrentIndex(\
#                    self.customwidget.maxCPUs.count() - 1)
#        else:
#            self.customwidget.maxCPUs.setCurrentIndex(0)

    def on_actionExit_triggered(self):
        self.ui.close()

    def on_recoverFT_changed(self, pSelectedValue):
        lOutputFileTypes = self.mRecoverFiletypes[pSelectedValue]

        if lOutputFileTypes == None:
            return

        self.customwidget.outputformat.clear()
        for lOutputFiletype in lOutputFileTypes:
            self.customwidget.outputformat.addItem(lOutputFiletype)

        #Enable and Disable the specific Preprocessing Tab
        for lTabCnt in range(self.customwidget.tabWidgetReassembly.count()):
            if self.customwidget.tabWidgetReassembly.tabText(lTabCnt).upper() \
                    == pSelectedValue.upper():
                self.customwidget.tabWidgetReassembly.setTabEnabled(\
                        lTabCnt, True)
            else:
                self.customwidget.tabWidgetReassembly.setTabEnabled(\
                        lTabCnt, False)

        #Some Filetype specific value customizations
        lAssemblyMethods = None
        if pSelectedValue == "Video":
            self.customwidget.minimumFragmentSize.setText("4")
            lAssemblyMethods = reassembly_context.CReassemblyFactory.\
                    getAssemblyMethodsVideo()
        elif pSelectedValue == "JPEG":
            self.customwidget.minimumFragmentSize.setText("0")
            lAssemblyMethods = reassembly_context.CReassemblyFactory.\
                    getAssemblyMethodsJpeg()
        elif pSelectedValue == "PNG":
            lAssemblyMethods = reassembly_context.CReassemblyFactory.\
                    getAssemblyMethodsPng()

        #Get the Filetype specific Reassembly Algorithms
        self.customwidget.assemblyMethod.clear()
        if lAssemblyMethods != None:
            for lAssembly in lAssemblyMethods:
                self.customwidget.assemblyMethod.addItem(lAssembly)
#        for lCnt in xrange(self.customwidget.tabWidget.count() - 2):
#            self.customwidget.tabWidget.setTabEnabled(lCnt + 2, False)
#        if pIdx == 0:
#            self.customwidget.tabWidget.setTabEnabled(2, True)
#        elif 0 < pIdx < 3:
#            self.customwidget.tabWidget.setTabEnabled(3, True)

    def on_inputFile_changed(self, pPath):
        if os.path.exists(pPath):
            lOptions = self.__getOptions()
            self.__mGeometry = \
                    fsstat_context.CFsStatContext.getFsGeometry(lOptions)
            logging.info("FS Info: " + str(self.__mGeometry))
            self.customwidget.offset.setText(str(self.__mGeometry.offset))
            self.customwidget.fragmentSize.setText(\
                    str(self.__mGeometry.blocksize))
            self.customwidget.fsInfo.setText(\
                    "FS Info: " + str(self.__mGeometry))
            pass
        else:
            self.customwidget.fsInfo.setText(\
                    "<html><font color=\"#FF0000\">"\
                    "Imagefile does not exist.</font></html>")

    def on_outputDir_changed(self, pPath):
        if os.path.isdir(pPath):
            self.customwidget.outputDirInfo.setText("Output directory exists.")
        else:
            self.customwidget.outputDirInfo.setText(\
                    "<html><font color=\"#FF0000\">"\
                    "Output directory does not exist.</font></html>")

    def on_actionAbout_triggered(self, pChecked=None):
        QtGui.QMessageBox.about(self.ui,
            "Multimedia File Carver",
            "<html>Key developers:  \
            <ul> \
                <li>Rainer Poisel</li> \
                <li>Vasileios Miskos</li> \
                <li>Manfred Ruzicka</li> \
                <li>Markus Mannel</li> \
            </ul> \
            &copy; 2011, 2012 St. Poelten University of Applied "\
            "Sciences</html> \
            <p> \
            This software is released under the terms of the LGPLv3:<br /> \
            <a href=\"http://www.gnu.org/licenses/lgpl.html\">"\
            "http://www.gnu.org/licenses/lgpl.html</a> \
            </p> \
            Regarding software required for running our file carver we "\
            "kindly refer to their respective licenses: \
            <ul> \
            <li><a href=\"http://ffmpeg.org/legal.html\">FFmpeg</a></li> \
            <li><a href=\"http://www.gzip.org/zlib/zlib_license.html\">"\
            "zlib</a></li> \
            <li><a href=\"http://www.sleuthkit.org/sleuthkit/licenses.php\">"\
            "The Sleuth Kit</a></li> \
            </ul> \
            "
            )

    def on_inputFileButton_clicked(self, pChecked=None):
        lFilename = QtGui.QFileDialog.getOpenFileName(self.ui, \
                "Choose Image", \
                os.path.dirname(self.customwidget.inputFile.text()), \
                "All Files (*)")
        if lFilename[0] != "":
            self.customwidget.inputFile.setText(lFilename[0])

    def on_outputDirButton_clicked(self):
        lDialog = QtGui.QFileDialog()
        lDialog.setFileMode(QtGui.QFileDialog.Directory)
        lFilename = lDialog.getExistingDirectory(self.ui, \
                "Choose output directory", \
                os.path.dirname(self.customwidget.outputDir.text()), \
                QtGui.QFileDialog.ShowDirsOnly)
        if lFilename != "":
            self.customwidget.outputDir.setText(lFilename)

    def on_processButton_clicked(self, pChecked=None):
        if not os.path.exists(self.customwidget.inputFile.text()):
            QtGui.QMessageBox.about(self.ui, "Error",
                "Please make sure that your input file exists.")
            return
        elif not os.path.isdir(self.customwidget.outputDir.text()):
            if self.__outputDirProblem() == False:
                return
        if self.__mLock.tryLock() == True:
            self.mLastTs = datetime.datetime.now()
            if self.mContext != None:
                self.mContext.cleanup()
            self.mContext = CContext()
            self.__clearFragments()
            self.__clearFiles()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.CLASSIFY | Jobs.REASSEMBLE)

    def __outputDirProblem(self):
        lMsgBox = QtGui.QMessageBox()
        lMsgBox.setText("The specified output directory does not exist. ")
        lMsgBox.setInformativeText("Do you want to create it?")
        lCreateButton = lMsgBox.addButton(self.ui.tr("Create directory"),\
                QtGui.QMessageBox.ActionRole)
        lCancelButton = lMsgBox.addButton(QtGui.QMessageBox.Abort)
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
        if len(self.mContext.fragments) is 0:
            QtGui.QMessageBox.about(self.ui, "Error",
                "What would you like to reassemble? "\
                        "No fragments have been classified yet!")
            return
        elif not os.path.isdir(self.customwidget.outputDir.text()):
            if self.__outputDirProblem() == False:
                return
        if self.__mLock.tryLock() == True:
            self.mLastTs = datetime.datetime.now()
            self.__clearFiles()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.REASSEMBLE)

    def on_classifyButton_clicked(self, pChecked=None):
        if not os.path.exists(self.customwidget.inputFile.text()):
            QtGui.QMessageBox.about(self.ui, "Error",
                "Please make sure that your input file exists.")
            return
        if self.__mLock.tryLock() == True:
            self.mLastTs = datetime.datetime.now()
            if self.mContext != None:
                self.mContext.cleanup()
            self.mContext = CContext()
            self.__clearFragments()
            self.customwidget.progressBar.setValue(0)
            self.__startWorker(Jobs.CLASSIFY)

    def __clearFragments(self):
        lCnt = self.customwidget.resultTable.rowCount() - 1
        while (lCnt >= 0):
            self.customwidget.resultTable.removeRow(lCnt)
            lCnt -= 1
        #self.numRowsResult = 0
        self.customwidget.resultTable.update()

    def __clearFiles(self):
        lCnt = self.customwidget.fileTable.rowCount() - 1
        while (lCnt >= 0):
            self.customwidget.fileTable.removeRow(lCnt)
            lCnt -= 1
        self.customwidget.fileTable.update()

    def __enableElements(self, pEnabled):
        self.customwidget.classifyButton.setEnabled(pEnabled)
        self.customwidget.reassembleButton.setEnabled(pEnabled)
        self.customwidget.processButton.setEnabled(pEnabled)
        # TODO add all elements that should be deactivated
        if pEnabled == True:
            self.mLoadMovie.stop()
            self.mLoadMovie.jumpToFrame(0)
        else:
            self.mLoadMovie.start()

    def __startWorker(self, pJobs):
        lOptions = self.__getOptions()
        self.__mWorker = CThreadWorker(lOptions, self.mContext, pJobs)
        self.__mWorker.sBegin.connect(self.on_begin_callback, \
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sProgress.connect(self.on_progress_callback, \
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sFinished.connect(self.on_finished_callback, \
                QtCore.Qt.QueuedConnection)
        self.__mWorker.sError.connect(self.on_error_callback, \
                QtCore.Qt.QueuedConnection)
        self.__enableElements(False)
        self.__mWorker.start(QtCore.QThread.IdlePriority)

    def __getOptions(self):
        # TODO rename fragmentsize to blocksize
        lOptions = gui_options.CGuiOptions()
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
        lOptions.minfragsize = int(\
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
        lOptions.multiprocessing = \
                self.customwidget.multiprocessing.isChecked()
        if self.__mGeometry != None:
            lOptions.fstype = self.__mGeometry.fstype
            lOptions.tskProperties = self.__mGeometry.tskProperties
        else:
            lOptions.fstype = ''
        lOptions.verbose = False
        return lOptions

    def on_begin_callback(self, pJob, pSize, pOffset, pFsType):
        if pJob == Jobs.CLASSIFY:
            logging.info("Beginning classifying. Imagesize is " +\
                    str(pSize) + " bytes.")
            self.__mImgVisualizer = gui_imgvisualizer.CImgVisualizer(\
                    self.mContext, pSize, pOffset, pFsType,\
                    self.customwidget.imageView)
            self.customwidget.imageView.setScene(self.__mImgVisualizer)
        elif pJob == Jobs.REASSEMBLE:
            logging.info("Beginning reassembling.")

    def on_progress_callback(self, pValue):
        lDelta = datetime.datetime.now() - self.mLastTs
        self.customwidget.duration.setText(str(lDelta))
        if 0 <= pValue <= 100:
            self.customwidget.progressBar.setValue(pValue)

    def on_finished_callback(self, pFinishedJob, pJobs):
        lOptions = self.__getOptions()
        lDelta = datetime.datetime.now() - self.mLastTs
        self.customwidget.duration.setText(str(lDelta))
        if pFinishedJob == Jobs.CLASSIFY:
            lNumRowsResult = 0
            if self.mContext.fragments != None:
                for lFrag in self.mContext.fragments:
                    self.customwidget.resultTable.insertRow(lNumRowsResult)
                    if lFrag.mIsHeader == True:
                        lItem = QtGui.QTableWidgetItem("H")
                    else:
                        lItem = QtGui.QTableWidgetItem("")
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, 0,
                            lItem)

                    lItem = QtGui.QTableWidgetItem("Fragment " +\
                            str(lNumRowsResult + 1))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, 1,
                            lItem)
                    self.customwidget.resultTable.horizontalHeader().\
                            resizeSection(1, 10)

                    lItem = QtGui.QTableWidgetItem(str(lFrag.mOffset))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(\
                            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, 2,
                            lItem)

                    #End Address in Bytes
                    lItem = QtGui.QTableWidgetItem(str(lFrag.mOffset + \
                            lFrag.mSize))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(\
                            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, 3,
                            lItem)

                    #Start Address in Sectors
                    lSector = lFrag.mOffset / int(self.__mGeometry.sectorsize)
                    # TODO this assumes that one cluster contains four sectors
                    lItem = QtGui.QTableWidgetItem(str(lSector) + \
                            "/" + str(lSector / 4))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(QtCore.Qt.AlignRight | \
                            QtCore.Qt.AlignVCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult,
                            4, lItem)

                    #End Address in Sectors
                    lSector = (lFrag.mOffset + lFrag.mSize) / \
                            int(self.__mGeometry.sectorsize) - 1
                    # TODO this assumes that one cluster contains four sectors
                    lItem = QtGui.QTableWidgetItem(str(lSector) + \
                            "/" + str(lSector / 4))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(QtCore.Qt.AlignRight | \
                            QtCore.Qt.AlignVCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, \
                            5, lItem)

                    #Size in Bytes
                    lItem = QtGui.QTableWidgetItem(str(lFrag.mSize))
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    lItem.setTextAlignment(QtCore.Qt.AlignRight | \
                            QtCore.Qt.AlignVCenter)
                    self.customwidget.resultTable.setItem(lNumRowsResult, \
                            6, lItem)

                    lNumRowsResult += 1
            self.__mImgVisualizer.update()
        if (pJobs & Jobs.REASSEMBLE == 0 and pFinishedJob == Jobs.CLASSIFY) \
                or (pFinishedJob == Jobs.REASSEMBLE):
            self.__mLock.unlock()
            self.__enableElements(True)

        if pFinishedJob == Jobs.REASSEMBLE and \
            lOptions.showResults == True:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(\
                        "file://" + lOptions.output))
        if pFinishedJob == Jobs.CLASSIFY:
            logging.info("Classification finished. ")
        elif pFinishedJob == Jobs.REASSEMBLE:
            logging.info("Reassembling finished. ")

#            lRowCount = 0
#
#            for lFrag in self.mContext.fragments:
#                if lFrag.mIsHeader == True:
#                    self.customwidget.fileTable.insertRow(lRowCount)
#                    #Header Number
#                    lItem = QtGui.QTableWidgetItem("File " + str(lRowCount))
#                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
#                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
#                    self.customwidget.fileTable.setItem(lRowCount, 0, lItem)
#                    #Filetype
#                    lItem = QtGui.QTableWidgetItem(lFrag.mFileType)
#                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
#                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
#                    self.customwidget.fileTable.setItem(lRowCount, 1, lItem)
#                    #Size
#                    lItem = QtGui.QTableWidgetItem(str(lFrag.mSize))
#                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
#                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
#                    self.customwidget.fileTable.setItem(lRowCount, 2, lItem)
#                    #Path
#                    lItem = QtGui.QTableWidgetItem(lFrag.mFilePath)
#                    lItem.setFlags(QtCore.Qt.ItemIsEnabled)
#                    lItem.setTextAlignment(QtCore.Qt.AlignCenter)
#                    self.customwidget.fileTable.setItem(lRowCount, 3, lItem)
#
#                    lRowCount += 1

    def on_error_callback(self, pError):
        QtGui.QMessageBox.about(self.ui, "Error",\
                "An error occured: " + pError)

    def run(self):
        #self.__mWindow.show()
        self.ui.show()
        lReturn = self.__mApp.exec_()
        sys.exit(lReturn)
