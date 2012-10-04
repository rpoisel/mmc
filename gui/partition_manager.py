from PySide import QtCore
from PySide import QtGui

from preprocessing import mmls
from model_partitions import CModelPartitions


class CPartitionManager(object):
    def __init__(self, pLoader, pSource):
        super(CPartitionManager, self).__init__()
        self.mDialog = pLoader.load(":/forms/dialog_partitions.ui")
        self.mMmls = mmls.CMmls(pSource)
        self.mPartitions = self.mMmls.getPartitions()

        # check if partition table could be interpreted
        if self.mMmls.getUnitsize() < 0:
            # error
            self.mDialog.fsInfo.setPlainText(self.mMmls.getOutput())
        else:
            # partitions exist
            lModel = CModelPartitions(self.mPartitions)
            self.mDialog.partInfo.setModel(lModel)

        # set up GUI elements
        self.mDialog.partInfo.setSelectionBehavior(
                QtGui.QAbstractItemView.SelectRows)
        self.mDialog.partInfo.setSelectionMode(
                QtGui.QAbstractItemView.SingleSelection)

        self.mDialog.partInfo.horizontalHeader().setResizeMode(
                QtGui.QHeaderView.Stretch)
        self.mDialog.partInfo.horizontalHeader().setResizeMode(
                0, QtGui.QHeaderView.ResizeToContents)

        # set interactivity
        self.mDialog.buttonSelect.clicked.connect(
                self.on_buttonSelect_clicked)
        self.mDialog.partInfo.clicked.connect(
                self.on_partition_clicked)

    def on_buttonSelect_clicked(self):
        # set offset parameters in gui

        # then close dialog
        self.mDialog.close()

    def on_partition_clicked(self, pIndex):
        self.mDialog.fsInfo.setPlainText("Offset: " +
                self.mPartitions[pIndex.row()][0])

    def run(self):
        # show as modal dialog
        self.mDialog.exec_()
