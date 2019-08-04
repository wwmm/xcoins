# -*- coding: utf-8 -*-

import os
import threading
from multiprocessing import Pool, cpu_count

import h5py
import numpy as np
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QFile, QObject, Qt
from PySide2.QtGui import QColor, QPainter
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import (QFileDialog, QFrame, QGraphicsDropShadowEffect,
                               QHeaderView, QPushButton, QTableView)

from XCoins.coins import MAX_COUNT, MAX_ENERGY, Coins
from XCoins.model import Model


class ApplicationWindow(QObject):
    def __init__(self):
        QObject.__init__(self)

        self.module_path = os.path.dirname(__file__)

        self.tables = []

        n_cpu_cores = cpu_count()

        print("number of cpu cores: ", n_cpu_cores)

        self.pool = Pool(processes=n_cpu_cores)
        self.coins = Coins(self.pool)
        self.model = Model()

        # loading widgets from designer file

        loader = QUiLoader()

        loader.registerCustomWidget(QtCharts.QChartView)

        self.window = loader.load(self.module_path + "/ui/application_window.ui")

        main_frame = self.window.findChild(QFrame, "main_frame")
        chart_frame = self.window.findChild(QFrame, "chart_frame")
        button_read_tags = self.window.findChild(QPushButton, "button_read_tags")
        button_save_matrix = self.window.findChild(QPushButton, "button_save_matrix")
        self.table_view = self.window.findChild(QTableView, "table_view")
        self.chart_view = self.window.findChild(QtCharts.QChartView, "chart_view")

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.setModel(self.model)

        # signal connection

        button_read_tags.clicked.connect(self.read_tags)
        button_save_matrix.clicked.connect(self.save_matrix)
        self.table_view.selectionModel().selectionChanged.connect(self.selection_changed)
        self.coins.new_spectrum.connect(self.on_new_spectrum)

        # Creating QChart
        self.chart = QtCharts.QChart()
        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setTheme(QtCharts.QChart.ChartThemeLight)
        self.chart.setAcceptHoverEvents(True)

        self.axis_x = QtCharts.QValueAxis()
        self.axis_x.setTitleText("Energy [keV]")
        self.axis_x.setRange(0, 100)
        self.axis_x.setLabelFormat("%.1f")

        self.axis_y = QtCharts.QValueAxis()
        self.axis_y.setTitleText("Intensity [a.u.]")
        self.axis_y.setRange(0, 100)
        self.axis_y.setLabelFormat("%d")

        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setRubberBand(QtCharts.QChartView.RectangleRubberBand)

        # custom stylesheet

        style_file = QFile(self.module_path + "/ui/custom.css")
        style_file.open(QFile.ReadOnly)

        self.window.setStyleSheet(style_file.readAll().data().decode("utf-8"))

        style_file.close()

        # effects

        main_frame.setGraphicsEffect(self.card_shadow())
        chart_frame.setGraphicsEffect(self.card_shadow())
        button_read_tags.setGraphicsEffect(self.button_shadow())
        button_save_matrix.setGraphicsEffect(self.button_shadow())

        self.window.show()

    def button_shadow(self):
        effect = QGraphicsDropShadowEffect(self.window)

        effect.setColor(QColor(0, 0, 0, 100))
        effect.setXOffset(1)
        effect.setYOffset(1)
        effect.setBlurRadius(5)

        return effect

    def card_shadow(self):
        effect = QGraphicsDropShadowEffect(self.window)

        effect.setColor(QColor(0, 0, 0, 100))
        effect.setXOffset(2)
        effect.setYOffset(2)
        effect.setBlurRadius(5)

        return effect

    def read_tags(self):
        file_path = QFileDialog.getOpenFileName(self.window, "Open File", os.path.expanduser("~"),
                                                "Coin Tags (*.csv);; *.* (*.*)")[0]

        if file_path != "":
            t = threading.Thread(target=self.coins.load_file, args=(file_path,), daemon=True)
            t.start()

    def on_new_spectrum(self):
        self.model.beginResetModel()

        self.model.data_name = self.coins.tags_found[:, 0]
        self.model.data_file_1 = self.coins.tags_found[:, 1]
        self.model.data_file_2 = self.coins.tags_found[:, 2]
        self.model.data_file_3 = self.coins.tags_found[:, 3]

        self.model.endResetModel()

        self.axis_x.setRange(0, MAX_ENERGY.value)
        self.axis_y.setRange(0, MAX_COUNT.value)

    def save_matrix(self):
        home = os.path.expanduser("~")

        path = QFileDialog.getSaveFileName(self.window, "Save PCA Matrix",  home, "Matrix (*.hdf5)")[0]

        if path != "":
            if not path.endswith(".hdf5"):
                path += ".hdf5"

            with h5py.File(path, "w") as f:
                dset = f.create_dataset("pca_matrix", data=self.coins.spectrum)

                dset.attrs["pca_sample_labels"] = self.coins.labels

    def selection_changed(self, selected, deselected):
        if self.model.data_name.size == 1:
            return

        s_model = self.table_view.selectionModel()

        if s_model.hasSelection():
            self.chart.removeAllSeries()

            indexes = s_model.selectedRows()

            for index in indexes:
                row_idx = index.row()

                name = self.model.data_name[row_idx]

                if name in self.coins.labels:
                    pca_matrix_idx = self.coins.labels.index(name)
                    spectrum = self.coins.spectrum[pca_matrix_idx, :]
                    nchannels = spectrum.size

                    xaxis = np.linspace(0, MAX_ENERGY.value, nchannels)

                    series = QtCharts.QLineSeries(self.window)
                    series.setName(name)
                    # series.setUseOpenGL(True)

                    for n in range(nchannels):
                        series.append(xaxis[n], spectrum[n])

                    self.chart.addSeries(series)
