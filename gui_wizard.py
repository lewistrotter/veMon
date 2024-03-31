import sys

import numpy as np
import pandas as pd
import xarray as xr

import working as work

from PySide6.QtCore import QAbstractListModel, Qt, QObject, Signal, Slot, QPointF
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6 import QtCharts

import PySide6.QtPositioning
#import PySide6.QtLocation

import models.charts



# we could use  a model vxy model here to control charts but
# likely easier to just use signals, slots, events
class Backend(QObject):

    #poly_coords = Signal(list)  # , arguments=['train_start']
    increase = Signal(float)

    def __init__(self):
        super().__init__()

        self.poly_coords = []
        self.ds = None

        self.training_start = 2018
        self.training_end = 2021
        self.testing_end = 2024
        self.num_harmonics = 2
        self.xbar_limit_1 = 1.5
        self.xbar_limit_2 = 20
        self.lam = 0.3
        self.lam_sigs = 3
        self.rounding = True
        self.low_threshold = 100
        self.persistence = 3

        self.ndvi_y = []
        self.harm_y = []
        self.resi_y = []

        #self.inc_progress.connect(self.fetch_dea_data)

    @Slot(list)
    def set_poly_coords(self, coords):
        #self.poly_coords.emit(coords)

        # convert to tuple of lat/lon floats
        coords = [(c.latitude(), c.longitude()) for c in coords]
        self.poly_coords = coords

        print(f"It is {coords}")

    @Slot()
    def fetch_dea_data(self):
        print('Fetching DEA data')

        if len(self.poly_coords) == 0:
            print('No polygon set.')
            return

        # TODO: implement dea tool

        # progressor
        for i in np.linspace(0, 1, 10):
            self.increase.emit(i)

        # testing: load netcdf normal
        # do preprocessing before charts called
        ds = xr.open_dataset(r"C:\Users\Lewis\Desktop\efreo_park\bwr_fire_ndvi.nc")
        ds = ds.resample(time='M').median()
        ds = ds * 10000  # FIXME: decimal values not working when rounding=False, need to * 10000
        self.ds = ds

        print('Done!')

    @Slot()
    def run_ewmacd(
            self,
            training_start=2018,
            training_end=2021,
            testing_end=2024,
            num_harmonics=2,
            xbar_lim_1=1.5,
            xbar_lim_2=20,
            low_thresh=100,
            lam=0.3,
            lam_sigs=3,
            persistence=3
    ):

        ds = self.ds

        ndvi_y, harm_y, resi_y = work.ewmacd(ds=ds,
                                             training_start=self.training_start,
                                             training_end=self.training_end,
                                             testing_end=self.testing_end,
                                             number_harmonics=self.num_harmonics,
                                             xbar_limit_1=self.xbar_limit_1,
                                             xbar_limit_2=self.xbar_limit_2,
                                             lam=self.lam,
                                             lam_sigs=self.lam_sigs,
                                             low_thresh=self.low_threshold,
                                             rounding=self.rounding,
                                             persistence=persistence,
                                             number_cpu=1)

        self.ndvi_y = ndvi_y
        self.harm_y = harm_y
        self.resi_y = resi_y

        print('Did ewmacd!')


    @Slot(int)
    def set_training_start(self, val):
        self.training_start = int(val)
        print(f"Train start: {int(val)}")

    @Slot(int)
    def set_training_end(self, val):
        self.training_end = int(val)
        print(f"Train end: {int(val)}")

    @Slot(int)
    def set_testing_end(self, val):
        self.testing_end = int(val)
        print(f"Testing end: {int(val)}")

    @Slot(int)
    def set_num_harmonics(self, val):
        self.num_harmonics = int(val)
        print(f"Num. harmonics: {int(val)}")

    @Slot(float)
    def set_xbar_limit_1(self, val):
        self.xbar_limit_1 = float(val)
        print(f"X-Bar limit 1: {float(val)}")

    @Slot(float)
    def set_xbar_limit_2(self, val):
        self.xbar_limit_2 = float(val)
        print(f"X-Bar limit 2: {float(val)}")

    @Slot(float)
    def set_lambda(self, val):
        self.lam = float(val)
        print(f"Lambda: {str(round(float(val), 1))}")

    @Slot(int)
    def set_lambda_sigs(self, val):
        self.lam_sigs = int(val)
        print(f"Lambda Sigs: {int(val)}")

    @Slot(bool)
    def set_rounding(self, val):
        self.rounding = val
        print(f"Rounding: {val}")

    @Slot(str)
    def set_low_threshold(self, val):
        self.low_threshold = float(val)
        print(f"Low Threshold: {float(val)}")

    @Slot(int)
    def set_persistence(self, val):
        self.persistence = int(val)
        print(f"Persistence: {int(val)}")

    @Slot(QtCharts.QAbstractSeries, QtCharts.QAbstractSeries)
    def update_top_chart_data(self, series_raw, series_harm):

        if series_raw is None or series_harm is None:
            return

        series_raw.clear()

        xs = np.arange(len(self.ndvi_y))
        ys = self.ndvi_y

        for x, y in zip(xs, ys):
            #point = QPointF(x, y)
            #series.append(point)
            #series_raw.append(point.x(), point.y())
            series_raw.append(x, y)

        # get chart axes and update ranges
        # x_raw_axis, y_raw_axis = series_raw.attachedAxes()
        # x_raw_axis.setMin(np.nanmin(xs))
        # x_raw_axis.setMax(np.nanmax(xs))
        # y_raw_axis.setMin(np.nanmin(ys))
        # y_raw_axis.setMax(np.nanmax(ys))

        x_raw_min = np.nanmin(xs)
        x_raw_max = np.nanmax(xs)
        y_raw_min = np.nanmin(ys)
        y_raw_max = np.nanmax(ys)

        series_harm.clear()

        xs = np.arange(len(self.harm_y))
        ys = self.harm_y

        for x, y in zip(xs, ys):
            #point = QPointF(x, y)
            #series.append(point)
            #series_raw.append(point.x(), point.y())
            series_harm.append(x, y)

        # get chart axes and update ranges
        # x_harm_axis, y_harm_axis = series_harm.attachedAxes()
        # x_harm_axis.setMin(np.nanmin(xs))
        # x_harm_axis.setMax(np.nanmax(xs))
        # y_harm_axis.setMin(np.nanmin(ys))
        # y_harm_axis.setMax(np.nanmax(ys))

        x_harm_min = np.nanmin(xs)
        x_harm_max = np.nanmax(xs)
        y_harm_min = np.nanmin(ys)
        y_harm_max = np.nanmax(ys)

        x_axis, y_axis = series_raw.attachedAxes()
        x_axis.setMin(np.nanmin([x_raw_min, x_harm_min]))
        x_axis.setMax(np.nanmax([x_raw_max, x_harm_max]))
        y_axis.setMin(np.nanmin([y_raw_min, y_harm_min]))
        y_axis.setMax(np.nanmax([y_raw_max, y_harm_max]))

    @Slot(str)
    def test(self, msg):
        #self.poly_coords.emit(coords)
        print(f"It is {msg}")




app = QApplication()

QQuickStyle.setStyle("Fusion")

engine = QQmlApplicationEngine()

backend = Backend()
engine.rootContext().setContextProperty("backend", backend)

# self.threadpool = QThreadPool()
# print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

# TESTING
calib_model = models.charts.CalibrateModel()
engine.rootContext().setContextProperty("calibModel", calib_model)

engine.quit.connect(app.quit)

engine.load('qml/containers/NewSite.qml')

sys.exit(app.exec())

# chart examples:
# https://gist.github.com/keithel/e0b47eaedeecfa2bab77756842bbed79
# https://stackoverflow.com/questions/54890951/y-axis-maximum-in-qml-barseries-not-updating
# https://stackoverflow.com/questions/69053154/how-to-create-a-vertical-line-on-the-chart-view-to-get-the-positions-of-the-plot -- mouse interact