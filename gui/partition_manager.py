from preprocessing import mmls
from PySide import QtCore
from PySide import QtGui


class CPartitionManager(object):
    def __init__(self, pLoader, pSource):
        super(CPartitionManager, self).__init__()
        self.mDialog = pLoader.load(":/forms/dialog_partitions.ui")
        self.mMmls = mmls.CMmls(pSource)

        # set up GUI elements
        self.mDialog.partInfo.setColumnCount(4)
        self.mDialog.partInfo.setSelectionBehavior(
                QtGui.QAbstractItemView.SelectRows)
        self.mDialog.partInfo.setSelectionMode(
                QtGui.QAbstractItemView.SingleSelection)
        self.mDialog.partInfo.setHorizontalHeaderLabels(
                ["start", "end", "len", "type"]
                )
        self.mDialog.partInfo.horizontalHeader().setResizeMode(
                QtGui.QHeaderView.Stretch)
        self.mDialog.partInfo.horizontalHeader().setResizeMode(
                3, QtGui.QHeaderView.ResizeToContents)

        # set interactivity
        self.mDialog.buttonSelect.clicked.connect(
                self.on_buttonSelect_clicked)
        self.mDialog.partInfo.cellClicked.connect(
                self.on_cell_clicked)

    def on_buttonSelect_clicked(self):
        # set offset parameters in gui

        # then close dialog
        self.mDialog.close()

    def on_cell_clicked(self, pRow, pCol):
        print "Offset: " + self.mDialog.partInfo.item(pRow, 0).text()

    def run(self):
        # check if partition table could be interpreted
        if self.mMmls.getUnitsize() < 0:
            # error
            self.mDialog.fsInfo.setPlainText(self.mMmls.getOutput())
        else:
            # partitions exist
            lPartitions = self.mMmls.getPartitions()
            self.mDialog.partInfo.setRowCount(len(lPartitions))
            for lCnt in range(len(lPartitions)):
                for lCntElem in range(len(lPartitions[lCnt])):
                    lItem = QtGui.QTableWidgetItem(
                            lPartitions[lCnt][lCntElem])
                    lItem.setFlags(QtCore.Qt.ItemIsEnabled |
                            QtCore.Qt.ItemIsSelectable)
                    if lCntElem < 3:
                        lItem.setTextAlignment(QtCore.Qt.AlignRight |
                                QtCore.Qt.AlignVCenter)
                    self.mDialog.partInfo.setItem(lCnt, lCntElem,
                            lItem)

        # show as modal dialog
        self.mDialog.exec_()
