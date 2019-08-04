# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import numpy as np
from PySide2.QtCore import QObject, Signal


def read_spectrum(path):
    return np.loadtxt(path, delimiter=";", usecols=1)


class Coins(QObject):
    new_spectrum = Signal()

    def __init__(self, multiprocessing_pool):
        QObject.__init__(self)

        self.working_directory = ""

        self.tags = np.array([])
        self.tags_found = None
        self.spectrum = np.array([])
        self.labels = []

        self.pool = multiprocessing_pool

    def load_file(self, path):
        self.working_directory = os.path.dirname(path)

        print("coins working directory: ", self.working_directory)

        self.tags = np.genfromtxt(path, delimiter=";", dtype=str).T

        print("coins tag matrix shape: ", self.tags.shape)

        self.spectrum, self.labels = self.get_spectrum()

        self.new_spectrum.emit()

    def get_spectrum(self):
        spectrum = []
        labels = []
        f_list = []
        self.tags_found = []

        for row in self.tags:
            aux_row = [row[0]]

            for n, col in enumerate(row):
                if n > 0:
                    f_path = os.path.join(self.working_directory, col + ".txt")

                    if os.path.isfile(f_path):
                        labels.append(row[0])

                        f_list.append(f_path)

                        aux_row.append(col)
                    else:
                        print("file not found: ", f_path)

                        aux_row.append("missing")

            self.tags_found.append(aux_row)

        self.tags_found = np.asarray(self.tags_found)

        spectrum = self.pool.map(read_spectrum, f_list)

        labels = list(OrderedDict.fromkeys(labels))
        spectrum = np.asarray(spectrum)

        print("spectrum shape: ", spectrum.shape)

        """
            In order to the average fast we reshape the matrix in a higher dimensionality. It is now a cube where
            each horizontal slice is a matrix with 3 rows and spectrum.shape[1] columns. The number of slices is
            int(spectrum.shape[0] / 3). After the reshape the average of each 3 measurements can be done applying
            np.mean in the axis = 1 (the one with 3 rows)
        """

        spectrum = spectrum.reshape(int(spectrum.shape[0] / 3), 3, spectrum.shape[1])

        avg_spectrum = np.mean(spectrum, axis=1)

        return avg_spectrum, labels
