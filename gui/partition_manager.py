from preprocessing import mmls


class CPartitionManager(object):
    def __init__(self, pLoader):
        super(CPartitionManager, self).__init__()
        self.mDialog = pLoader.load(":/forms/dialog_partitions.ui")
        self.mMmls = mmls.CMmls()

        self.mDialog.buttonSelect.clicked.connect(
                self.on_buttonSelect_clicked)

    def on_buttonSelect_clicked(self):
        self.mDialog.close()

    def run(self, pSource):
        # show as modal dialog
        self.mDialog.fsInfo.setPlainText(self.mMmls.getPartitions(
            pSource))
        self.mDialog.exec_()
