# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_carving_ui.ui'
#
# Created: Mon Aug  1 15:12:49 2011
#      by: pyside-uic 0.2.11 running on PySide 1.0.5
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_filecarvingWidget(object):
    def setupUi(self, filecarvingWidget):
        filecarvingWidget.setObjectName("filecarvingWidget")
        filecarvingWidget.resize(568, 468)
        self.verticalLayout = QtGui.QVBoxLayout(filecarvingWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.inputFile = QtGui.QLineEdit(filecarvingWidget)
        self.inputFile.setText("")
        self.inputFile.setObjectName("inputFile")
        self.gridLayout_2.addWidget(self.inputFile, 0, 0, 1, 1)
        self.inputFileButton = QtGui.QPushButton(filecarvingWidget)
        self.inputFileButton.setObjectName("inputFileButton")
        self.gridLayout_2.addWidget(self.inputFileButton, 0, 1, 1, 1)
        self.outputDirButton = QtGui.QPushButton(filecarvingWidget)
        self.outputDirButton.setObjectName("outputDirButton")
        self.gridLayout_2.addWidget(self.outputDirButton, 2, 1, 1, 1)
        self.outputDir = QtGui.QLineEdit(filecarvingWidget)
        self.outputDir.setText("")
        self.outputDir.setObjectName("outputDir")
        self.gridLayout_2.addWidget(self.outputDir, 2, 0, 1, 1)
        self.fsInfo = QtGui.QLabel(filecarvingWidget)
        self.fsInfo.setObjectName("fsInfo")
        self.gridLayout_2.addWidget(self.fsInfo, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtGui.QLabel(filecarvingWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.preprocessing = QtGui.QComboBox(filecarvingWidget)
        self.preprocessing.setObjectName("preprocessing")
        self.horizontalLayout.addWidget(self.preprocessing)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.fragmentSize = QtGui.QLineEdit(filecarvingWidget)
        self.fragmentSize.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fragmentSize.setObjectName("fragmentSize")
        self.gridLayout.addWidget(self.fragmentSize, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(filecarvingWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.incrementSize = QtGui.QLineEdit(filecarvingWidget)
        self.incrementSize.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.incrementSize.setObjectName("incrementSize")
        self.gridLayout.addWidget(self.incrementSize, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(filecarvingWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.offset = QtGui.QLineEdit(filecarvingWidget)
        self.offset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.offset.setObjectName("offset")
        self.gridLayout.addWidget(self.offset, 1, 2, 1, 1)
        self.label = QtGui.QLabel(filecarvingWidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.blockGap = QtGui.QLineEdit(filecarvingWidget)
        self.blockGap.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.blockGap.setObjectName("blockGap")
        self.gridLayout_3.addWidget(self.blockGap, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(filecarvingWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.resultTable = QtGui.QTableWidget(filecarvingWidget)
        self.resultTable.setObjectName("resultTable")
        self.resultTable.setColumnCount(0)
        self.resultTable.setRowCount(0)
        self.verticalLayout.addWidget(self.resultTable)
        self.progressBar = QtGui.QProgressBar(filecarvingWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_7 = QtGui.QLabel(filecarvingWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.outputformat = QtGui.QComboBox(filecarvingWidget)
        self.outputformat.setObjectName("outputformat")
        self.horizontalLayout_2.addWidget(self.outputformat)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.classifyButton = QtGui.QPushButton(filecarvingWidget)
        self.classifyButton.setObjectName("classifyButton")
        self.horizontalLayout_3.addWidget(self.classifyButton)
        self.reassembleButton = QtGui.QPushButton(filecarvingWidget)
        self.reassembleButton.setEnabled(False)
        self.reassembleButton.setObjectName("reassembleButton")
        self.horizontalLayout_3.addWidget(self.reassembleButton)
        self.processButton = QtGui.QPushButton(filecarvingWidget)
        self.processButton.setObjectName("processButton")
        self.horizontalLayout_3.addWidget(self.processButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(filecarvingWidget)
        QtCore.QMetaObject.connectSlotsByName(filecarvingWidget)

    def retranslateUi(self, filecarvingWidget):
        filecarvingWidget.setWindowTitle(QtGui.QApplication.translate("filecarvingWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.inputFileButton.setText(QtGui.QApplication.translate("filecarvingWidget", "&Input File", None, QtGui.QApplication.UnicodeUTF8))
        self.outputDirButton.setText(QtGui.QApplication.translate("filecarvingWidget", "&Output Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.fsInfo.setText(QtGui.QApplication.translate("filecarvingWidget", "FS Info: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("filecarvingWidget", "Preprocessing: ", None, QtGui.QApplication.UnicodeUTF8))
        self.fragmentSize.setText(QtGui.QApplication.translate("filecarvingWidget", "512", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("filecarvingWidget", "Increment Size", None, QtGui.QApplication.UnicodeUTF8))
        self.incrementSize.setText(QtGui.QApplication.translate("filecarvingWidget", "512", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("filecarvingWidget", "Offset", None, QtGui.QApplication.UnicodeUTF8))
        self.offset.setText(QtGui.QApplication.translate("filecarvingWidget", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("filecarvingWidget", "Block Size", None, QtGui.QApplication.UnicodeUTF8))
        self.blockGap.setText(QtGui.QApplication.translate("filecarvingWidget", "16384", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("filecarvingWidget", "Block Gap", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("filecarvingWidget", "Output Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.classifyButton.setText(QtGui.QApplication.translate("filecarvingWidget", "&Classify", None, QtGui.QApplication.UnicodeUTF8))
        self.reassembleButton.setText(QtGui.QApplication.translate("filecarvingWidget", "&Reassemble", None, QtGui.QApplication.UnicodeUTF8))
        self.processButton.setText(QtGui.QApplication.translate("filecarvingWidget", "&Process (do it all)", None, QtGui.QApplication.UnicodeUTF8))

