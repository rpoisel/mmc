from PySide.QtCore import Qt
from PySide.QtCore import QAbstractTableModel
from PySide.QtCore import QModelIndex


class CModelFiles(QAbstractTableModel):

    def __init__(self, pFiles, parent=None):
        super(CModelFiles, self).__init__(parent)

        self.__mFiles = pFiles

    def rowCount(self, index=QModelIndex()):
        if self.__mFiles is None:
            return 0
        return len(self.__mFiles)

    def columnCount(self, pIndex=QModelIndex()):
        return 4

    def data(self, pIndex, pRole=Qt.DisplayRole):
        if not pIndex.isValid():
            return None

        if not 0 <= pIndex.row() < len(self.__mFiles):
            return None

        if pRole == Qt.DisplayRole:
            lFile = self.__mFiles[pIndex.row()]

            if pIndex.column() == 0:
                return "File " + str(pIndex.row())
            elif pIndex.column() == 1:
                return lFile.mFileType
            elif pIndex.column() == 2:
                # len of file
                return str(0)
            elif pIndex.column() == 3:
                # path to file
                return lFile.mFilePath
            return None

        elif pRole == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def headerData(self, pSection, pOrientation, pRole=Qt.DisplayRole):
        """ Set the headers to be displayed. """

        if pRole != Qt.DisplayRole:
            return None

        if pOrientation == Qt.Horizontal:
            if pSection == 0:
                return "File"
            elif pSection == 1:
                return "Filetype"
            elif pSection == 2:
                return "Size"
            elif pSection == 3:
                return "Path"
        return None

    def flags(self, pIndex):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not pIndex.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, pIndex) |
                            Qt.ItemIsSelectable)

