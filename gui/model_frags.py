from PySide.QtCore import Qt
from PySide.QtCore import QAbstractTableModel
from PySide.QtCore import QModelIndex


class CModelFrags(QAbstractTableModel):

    def __init__(self, pFrags, parent=None):
        super(CModelFrags, self).__init__(parent)

        self.__mFrags = pFrags

    def rowCount(self, index=QModelIndex()):
        if self.__mFrags is None:
            return 0
        return len(self.__mFrags)

    def columnCount(self, pIndex=QModelIndex()):
        return 7

    def data(self, pIndex, pRole=Qt.DisplayRole):
        if not pIndex.isValid():
            return None

        if not 0 <= pIndex.row() < len(self.__mFrags):
            return None

        if pRole == Qt.DisplayRole:
            lFrag = self.__mFrags[pIndex.row()]

            if pIndex.column() == 0:
                return "H" if lFrag.mIsHeader else ""
            if pIndex.column() == 1:
                return "Fragment " + str(pIndex.row())
            if pIndex.column() == 2:
                # start address in bytes
                return str(lFrag.mOffset)
            if pIndex.column() == 3:
                # end address in bytes
                return str(lFrag.mOffset + lFrag.mSize)
            if pIndex.column() == 4:
                # start address in sectors
                return ""
            if pIndex.column() == 5:
                # end address in sectors
                return ""
            if pIndex.column() == 6:
                # size in bytes and sectors
                return str(lFrag.mSize)
            return None

        if pRole == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def headerData(self, pSection, pOrientation, pRole=Qt.DisplayRole):
        """ Set the headers to be displayed. """

        if pRole != Qt.DisplayRole:
            return None

        if pOrientation == Qt.Horizontal:
            if pSection == 0:
                return "Header"
            elif pSection == 1:
                return "Fragment"
            elif pSection == 2:
                return "Start [Bytes]"
            elif pSection == 3:
                return "End [Bytes]"
            elif pSection == 4:
                return "Start [Sector]"
            elif pSection == 5:
                return "End [Sector]"
            elif pSection == 6:
                return "Size [Bytes/Sectors]"

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
