# -*- coding: utf-8 -*-

import numpy as np
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QColor


class Model(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.ncols = 1

        self.data_name = ["sample name"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_name)

    def columnCount(self, parent=QModelIndex()):
        return self.ncols

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return ("Name", "File 1", "File 2", "File 3")[section]

        return "{}".format(section)

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            column = index.column()
            row = index.row()

            if column == 0:
                self.data_name[row] = value

                self.dataChanged.emit(index, index)

        return False

    def data(self, index, role):
        if role == Qt.ForegroundRole:
            row = index.row()

            return QColor(0, 0, 0, 222)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        elif role == Qt.DisplayRole:
            column = index.column()
            row = index.row()

            if column == 0:
                return self.data_name[row]

    def remove_rows(self, index_list):
        index_list.sort(reverse=True)

        for index in index_list:
            self.beginRemoveRows(QModelIndex(), index, index)
            self.endRemoveRows()

        self.data_name = np.delete(self.data_name, index_list)
