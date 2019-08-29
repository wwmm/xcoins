# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as et
from operator import add

import numpy as np
from PySide2.QtCore import QObject, Signal


def read_spectrum(path):
    tree = et.parse(path)

    spectrum = np.asarray(tree.find(".//Channels").text.split(","), dtype=np.int32)
    max_energy = float(tree.find(".//MaxEnergy").text.replace(",", "."))

    max_count = np.max(spectrum)

    file_name = os.path.basename(path)

    name = file_name.split("_")[0]

    return name, spectrum, max_energy, max_count


class Coins(QObject):
    new_spectrum = Signal()

    def __init__(self, multiprocessing_pool):
        QObject.__init__(self)

        self.working_directory = ""

        self.tags = np.array([])
        self.tags_found = None  # first column has labels but there is repetition
        self.spectrum = None
        self.max_energy = 0.0
        self.max_count = 0
        self.labels = None  # labels without repetion

        self.pool = multiprocessing_pool

    def load_file(self, path):
        self.working_directory = path

        print("coins working directory: ", self.working_directory)

        spx_name_set = set()
        spx_file_list = []

        for f in os.listdir(self.working_directory):
            if f.endswith(".spx"):
                spx_name_set.add(f.split("_")[0])

                spx_file_list.append(os.path.join(self.working_directory, f))

        if len(spx_file_list) > 0:
            self.labels = list(spx_name_set)

            self.labels.sort()

            self.build_pca_matrix(spx_file_list)

    def build_pca_matrix(self, file_list):
        self.spectrum = []

        map_output = self.pool.map(read_spectrum, file_list)

        for name, s, energy, count in map_output:
            if energy > self.max_energy:
                self.max_energy = energy

            if count > self.max_count:
                self.max_count = count

        for label in self.labels:
            spectrum_row = []
            count = 0

            for name, s, energy, count in map_output:
                if name == label:
                    if len(spectrum_row) == 0:
                        spectrum_row = s

                        count = 1
                    else:
                        spectrum_row = list(map(add, spectrum_row, s))

                        count = count + 1

            if count > 0:
                spectrum_row = [x / count for x in spectrum_row]

            self.spectrum.append(spectrum_row)

        self.spectrum = np.asarray(self.spectrum)

        self.new_spectrum.emit()
