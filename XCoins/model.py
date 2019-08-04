# -*- coding: utf-8 -*-

import numpy as np
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QColor


class Model(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.ncols = 4
        nrows = 1  # initial number of rows

        self.data_name = np.empty(nrows, dtype="object")
        self.data_file_1 = np.empty(nrows, dtype="object")
        self.data_file_2 = np.empty(nrows, dtype="object")
        self.data_file_3 = np.empty(nrows, dtype="object")

        self.data_name[0] = "sample name"
        self.data_file_1[0] = "file 1"
        self.data_file_2[0] = "file 2"
        self.data_file_3[0] = "file 3"

    def rowCount(self, parent=QModelIndex()):
        return self.data_name.size

    def columnCount(self, parent=QModelIndex()):
        return self.ncols

    def flags(self, index):
        column = index.column()

        if column == 0:
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return ("Name", "File 1", "File 2", "File 3")[section]

        return "{}".format(section)

    def data(self, index, role):
        if role == Qt.BackgroundRole:
            return QColor(Qt.white)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        elif role == Qt.DisplayRole:
            column = index.column()
            row = index.row()

            if column == 0:
                return self.data_name[row]

            if column == 1:
                return self.data_file_1[row]

            if column == 2:
                return self.data_file_2[row]

            if column == 3:
                return self.data_file_3[row]

    def remove_rows(self, index_list):
        index_list.sort(reverse=True)

        for index in index_list:
            self.beginRemoveRows(QModelIndex(), index, index)
            self.endRemoveRows()

        self.data_name = np.delete(self.data_name, index_list)
        self.data_file_1 = np.delete(self.data_file_1, index_list)
        self.data_file_2 = np.delete(self.data_file_2, index_list)
        self.data_file_3 = np.delete(self.data_file_3, index_list)
