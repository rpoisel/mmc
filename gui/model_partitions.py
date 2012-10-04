from PySide.QtCore import Qt
from PySide.QtCore import QAbstractTableModel
from PySide.QtCore import QModelIndex
from PySide.QtGui import QBrush
from PySide.QtGui import QColor


class CModelPartitions(QAbstractTableModel):

    def __init__(self, pPartitions, parent=None):
        super(CModelPartitions, self).__init__(parent)

        self.__mPartitions = pPartitions

    def rowCount(self, index=QModelIndex()):
        if self.__mPartitions is None:
            return 0
        return len(self.__mPartitions)

    def columnCount(self, pIndex=QModelIndex()):
        return 4

    def data(self, pIndex, pRole=Qt.DisplayRole):
        if not pIndex.isValid():
            return None

        if not 0 <= pIndex.row() < len(self.__mPartitions):
            return None

        if pRole == Qt.DisplayRole:
            lPartition = self.__mPartitions[pIndex.row()]

            if pIndex.column() == 0:
                # type
                return lPartition[3]
            elif pIndex.column() == 1:
                # start
                return lPartition[0]
            elif pIndex.column() == 2:
                # end
                return lPartition[1]
            elif pIndex.column() == 3:
                # len
                return lPartition[2]
            return None

        elif pRole == Qt.TextAlignmentRole:
            if pIndex.column() == 0:
                return int(Qt.AlignLeft) | int(Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight) | int(Qt.AlignVCenter)

        elif pRole == Qt.BackgroundRole:
            if self.__mPartitions[pIndex.row()][
                    3].find("(0x07)") != -1:
                return QBrush(QColor(0x95, 0xe6, 0xe9))
            elif self.__mPartitions[pIndex.row()][
                    3].lower().find("unallocated") != -1:
                return QBrush(QColor(0xfe, 0xc7, 0x36))
            elif self.__mPartitions[pIndex.row()][
                    3].find("0x3c") != -1:
                return QBrush(QColor(0xfe, 0xc7, 0xd7))
            elif self.__mPartitions[pIndex.row()][
                    3].lower().find("primary table") != -1:
                return QBrush(QColor(0xdd, 0xdd, 0xdd))
            elif self.__mPartitions[pIndex.row()][
                    3].find("0x83") != -1:
                return QBrush(QColor(0x50, 0xf8, 0x64))
            elif self.__mPartitions[pIndex.row()][
                    3].find("0x05") != -1:
                return QBrush(QColor(0x50, 0x97, 0x64))
            elif self.__mPartitions[pIndex.row()][
                    3].find("0x82") != -1:
                return QBrush(QColor(0xf8, 0xf0, 0x51))
            elif self.__mPartitions[pIndex.row()][
                    3].lower().find("extended table") != -1:
                return QBrush(QColor(0x99, 0x99, 0x99))

    def headerData(self, pSection, pOrientation, pRole=Qt.DisplayRole):
        """ Set the headers to be displayed. """

        if pRole != Qt.DisplayRole:
            return None

        if pOrientation == Qt.Horizontal:
            if pSection == 0:
                return "Type"
            elif pSection == 1:
                return "Start"
            elif pSection == 2:
                return "End"
            elif pSection == 3:
                return "Length"

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
