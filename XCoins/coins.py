# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as et
from collections import OrderedDict

import numpy as np
from PySide2.QtCore import QObject, Signal
from multiprocessing import Value, Lock

MAX_ENERGY = Value('d', 0.0)
MAX_COUNT = Value('i', 0)

lock = Lock()


def read_spectrum(path):
    tree = et.parse(path)

    spectrum = np.asarray(tree.find(".//Channels").text.split(","), dtype=np.int32)

    maxv = np.max(spectrum)

    # if maxv > 0:
    #     spectrum = spectrum / maxv

    with lock:
        v = float(tree.find(".//MaxEnergy").text.replace(",", "."))

        if v > MAX_ENERGY.value:
            MAX_ENERGY.value = v

        if maxv > MAX_COUNT.value:
            MAX_COUNT.value = maxv

    return spectrum


class Coins(QObject):
    new_spectrum = Signal()

    def __init__(self, multiprocessing_pool):
        QObject.__init__(self)

        self.working_directory = ""

        self.tags = np.array([])
        self.tags_found = None  # first column has labels but there is repetition
        self.spectrum = None
        self.labels = None  # labels without repetion

        self.pool = multiprocessing_pool

    def load_file(self, path):
        self.working_directory = os.path.dirname(path)

        print("coins working directory: ", self.working_directory)

        self.tags = np.genfromtxt(path, delimiter=";", dtype=str).T

        print("coins tag matrix shape: ", self.tags.shape)

        self.build_pca_matrix()

    def build_pca_matrix(self):
        self.spectrum = []
        self.labels = []
        f_list = []
        self.tags_found = []

        for row in self.tags:
            aux_row = [row[0]]

            for n, col in enumerate(row):
                if n > 0:
                    f_path = os.path.join(self.working_directory, col + ".spx")

                    if os.path.isfile(f_path):
                        self.labels.append(row[0])

                        f_list.append(f_path)

                        aux_row.append(col)
                    else:
                        print("file not found: ", f_path)

                        aux_row.append("missing")

            self.tags_found.append(aux_row)

        self.tags_found = np.asarray(self.tags_found)

        self.spectrum = self.pool.map(read_spectrum, f_list)

        self.labels = list(OrderedDict.fromkeys(self.labels))
        self.spectrum = np.asarray(self.spectrum)

        print("spectrum shape: ", self.spectrum.shape)

        """
            In order to the average fast we reshape the matrix in a higher dimensionality. It is now a cube where
            each horizontal slice is a matrix with 3 rows and spectrum.shape[1] columns. The number of slices is
            int(spectrum.shape[0] / 3). After the reshape the average of each 3 measurements can be done applying
            np.mean in the axis = 1 (the one with 3 rows)
        """

        if self.spectrum.shape[0] % 3 == 0:
            self.spectrum = self.spectrum.reshape(int(self.spectrum.shape[0] / 3), 3, self.spectrum.shape[1])

            self.spectrum = np.mean(self.spectrum, axis=1)
        else:
            print("Spectrum matrix has wrong size. Can not calculate average!")

        self.new_spectrum.emit()
