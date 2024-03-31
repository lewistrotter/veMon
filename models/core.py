
import os
import json
import datetime
import numpy as np
import pandas as pd
import xarray as xr

from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from PySide6.QtCore import QObject
from PySide6.QtCore import Property
from PySide6.QtCore import QByteArray
from PySide6.QtCore import QDateTime
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QAbstractListModel
from PySide6.QtCore import QThreadPool
from PySide6.QtCharts import QAbstractSeries
from PySide6.QtQuick import QQuickItem
from PySide6.QtPositioning import QGeoPolygon
from PySide6.QtPositioning import QGeoCoordinate

from dea import downloader
from algorithms import algos
from models import workers


class SitesModel(QAbstractListModel):

    # see url beneath for full pyside6 example with editing, etc.
    # https://doc.qt.io/qtforpython-6.2/examples/example_declarative__editingmodel.html

    # region ROLE DEFINITIONS
    IdRole = Qt.UserRole + 1
    ProjectRole = Qt.UserRole + 2
    CodeRole = Qt.UserRole + 3
    PolyRole = Qt.UserRole + 4
    TrainStartRole = Qt.UserRole + 5
    TrainEndRole = Qt.UserRole + 6
    TestEndRole = Qt.UserRole + 7
    NumHarmonicsRole = Qt.UserRole + 8
    XBarLimit1Role = Qt.UserRole + 9
    XBarLimit2Role = Qt.UserRole + 10
    LambdaValueRole = Qt.UserRole + 11
    LambdaStdvsRole = Qt.UserRole + 12
    LowThreshRole = Qt.UserRole + 13
    PersistenceRole = Qt.UserRole + 14
    RoundingRole = Qt.UserRole + 15
    OutputFolderRole = Qt.UserRole + 16
    NCDatasetRole = Qt.UserRole + 17
    XRDatasetRole = Qt.UserRole + 18
    IsProcessingRole = Qt.UserRole + 19
    StacProgressRole = Qt.UserRole + 20
    MaskProgressRole = Qt.UserRole + 21
    BandProgressRole = Qt.UserRole + 22
    ProgressTextRole = Qt.UserRole + 23
    # endregion

    def __init__(self, sites=None):
        super().__init__()
        self._sites = sites if sites else []

        self._out_folder = r'C:\Users\Lewis\Desktop\mon\output'  # TODO: improve

    def rowCount(self, parent=QModelIndex()):
        return len(self._sites)

    def roleNames(self):
        roles = super().roleNames()

        roles[self.IdRole] = QByteArray(b'id')
        roles[self.ProjectRole] = QByteArray(b'project')
        roles[self.CodeRole] = QByteArray(b'code')
        roles[self.PolyRole] = QByteArray(b'poly')
        roles[self.TrainStartRole] = QByteArray(b'train_start')
        roles[self.TrainEndRole] = QByteArray(b'train_end')
        roles[self.TestEndRole] = QByteArray(b'test_end')
        roles[self.NumHarmonicsRole] = QByteArray(b'num_harmonics')
        roles[self.XBarLimit1Role] = QByteArray(b'xbar_limit_1')
        roles[self.XBarLimit2Role] = QByteArray(b'xbar_limit_2')
        roles[self.LambdaValueRole] = QByteArray(b'lambda_value')
        roles[self.LambdaStdvsRole] = QByteArray(b'lambda_stdvs')
        roles[self.LowThreshRole] = QByteArray(b'low_thresh')
        roles[self.PersistenceRole] = QByteArray(b'persistence')
        roles[self.RoundingRole] = QByteArray(b'rounding')
        roles[self.OutputFolderRole] = QByteArray(b'output_folder')
        roles[self.NCDatasetRole] = QByteArray(b'nc_dataset')
        roles[self.XRDatasetRole] = QByteArray(b'xr_dataset')
        roles[self.IsProcessingRole] = QByteArray(b'is_processing')
        roles[self.StacProgressRole] = QByteArray(b'stac_progress')
        roles[self.MaskProgressRole] = QByteArray(b'mask_progress')
        roles[self.BandProgressRole] = QByteArray(b'band_progress')
        roles[self.ProgressTextRole] = QByteArray(b'progress_text')

        return roles

    def data(self, index, role=Qt.DisplayRole):
        if not self._sites:
            return
        elif not index.isValid():
            return

        # can use display role for displaying raw values differently
        # can use background role for styling
        #if role == Qt.DisplayRole:
            #return self._sites[index.row()]['text']
        #elif role == Qt.BackgroundRole:
            #return self._sites[index.row()]["bgColor"]

        site = self._sites[index.row()]

        if role == self.IdRole:
            return site['id']
        elif role == self.ProjectRole:
            return site['project']
        elif role == self.CodeRole:
            return site['code']
        elif role == self.PolyRole:
            return site['polygon']
        elif role == self.TrainStartRole:
            return site['train_start']
        elif role == self.TrainEndRole:
            return site['train_end']
        elif role == self.TestEndRole:
            return site['test_end']
        elif role == self.NumHarmonicsRole:
            return site['num_harmonics']
        elif role == self.XBarLimit1Role:
            return site['xbar_limit_1']
        elif role == self.XBarLimit2Role:
            return site['xbar_limit_2']
        elif role == self.LambdaValueRole:
            return site['lambda_value']
        elif role == self.LambdaStdvsRole:
            return site['lambda_stdvs']
        elif role == self.LowThreshRole:
            return site['low_thresh']
        elif role == self.PersistenceRole:
            return site['persistence']
        elif role == self.RoundingRole:
            return site['rounding']
        elif role == self.OutputFolderRole:
            return site['output_folder']
        elif role == self.NCDatasetRole:
            return site['nc_dataset']
        elif role == self.XRDatasetRole:
            return site['xr_dataset']
        elif role == self.IsProcessingRole:
            return site['is_processing']
        elif role == self.StacProgressRole:
            return site['stac_progress']
        elif role == self.MaskProgressRole:
            return site['mask_progress']
        elif role == self.BandProgressRole:
            return site['band_progress']
        elif role == self.ProgressTextRole:
            return site['progress_text']

        return

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        site = self._sites[index.row()]

        if role == self.IdRole:
            site.id = int(value)
        elif role == self.ProjectRole:
            site.project = str(value)
        elif role == self.CodeRole:
            site.code = str(value)
        elif role == self.PolyRole:
            site.poly = value
        elif role == self.TrainStartRole:
            site.train_start = int(value)
        elif role == self.TrainEndRole:
            site.train_end = int(value)
        elif role == self.TestEndRole:
            site.test_end = int(value)
        elif role == self.NumHarmonicsRole:
            site.num_harmonics = int(value)
        elif role == self.XBarLimit1Role:
            site.xbar_limit_1 = float(value)
        elif role == self.XBarLimit2Role:
            site.xbar_limit_2 = int(value)
        elif role == self.LambdaValueRole:
            site.lambda_value = float(value)
        elif role == self.LambdaStdvsRole:
            site.lambda_stdvs = int(value)
        elif role == self.LowThreshRole:
            site.low_thresh = float(value)  # TODO: this control needs fixing
        elif role == self.PersistenceRole:
            site.persistence = int(value)
        elif role == self.RoundingRole:
            site.rounding = bool(value)
        elif role == self.OutputFolderRole:
            site.output_folder = value
        elif role == self.NCDatasetRole:
            site.nc_dataset = value
        elif role == self.XRDatasetRole:
            site.xr_dataset = value
        elif role == self.IsProcessingRole:
            site.is_processing = bool(value)
        elif role == self.StacProgressRole:
            site.stac_progress = float(value)
        elif role == self.MaskProgressRole:
            site.mask_progress = float(value)
        elif role == self.BandProgressRole:
            site.band_progress = float(value)
        elif role == self.ProgressTextRole:
            site.progress_text = str(value)
        else:
            return False

        self._sites[index.row()] = site
        self.dataChanged.emit(index, index, role)

        return True

    def insertRows(self, row, count, index=QModelIndex()):
        """Insert n rows (n = 1 + count) at row"""

        self.beginInsertRows(QModelIndex(), row, row + count)

        if len(self._sites) > 0:
            new_id = max(site['id'] for site in self._sites) + 1
        else:
            new_id = 1

        for i in range(count + 1):  # at least one row
            new_row = {
                'id': new_id + i,
                'project': None,
                'code': None,
                # TODO: set all defaults here
            }

            raise NotImplemented

            self._sites.insert(row, new_row)

        self.endInsertRows()

        return True

    def insertRow(self, row):
        """Insert a single row at row"""

        return self.insertRows(row, 0)

    # def moveRows

    def removeRows(self, row, count, parent=QModelIndex()):
        """Remove n rows (n=1+count) starting at row"""

        self.beginRemoveRows(QModelIndex(), row, row + count)
        self._sites = self._sites[:row] + self._sites[row + count + 1:]
        self.endRemoveRows()

        return True

    def removeRow(self, row, parent=QModelIndex()):
        """Remove one row at index row"""

        return self.removeRows(row, 0, parent)

    # region GETTERS & SETTERS (QML-SIDE)
    @Slot(QObject)
    def ingestNewSite(self, new_site):
        """Slot to ingest and insert new site after calibration"""

        if len(self._sites) > 0:
            new_id = max(site['id'] for site in self._sites) + 1
        else:
            new_id = 1

        new_site = new_site.export_site()
        new_site['id'] = new_id

        self.beginInsertRows(QModelIndex(), len(self._sites), len(self._sites))
        self._sites.append(new_site)
        self.endInsertRows()

        self.save()

        return

    @Slot(int)
    def remove(self, row):
        """Slot to remove one row"""

        return self.removeRow(row)
    # endregion

    # region MAP FUNCS
    @Slot(list, QQuickItem)
    def zoomToClickedSiteItem(self, poly, map):
        """Zoom to clicked site on main view."""

        poly = QGeoPolygon(poly)
        map.fitViewportToGeoShape(poly, 200)

        return
    # endregion

    # region IO FUNCS
    def _decodeSites(self):
        """Some formats not supported by json, this decodes them."""

        sites = [site.copy() for site in self._sites]
        for site in sites:

            if site['polygon']:
                xs = [xy.longitude() for xy in site['polygon']]
                ys = [xy.latitude() for xy in site['polygon']]
                site['polygon'] = list(zip(xs, ys))

            site['xr_dataset'] = None  # close xr

            if site['algo_xs_date']:
                dates = [dt for dt in site['algo_xs_date']]
                dates = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in dates]
                site['algo_xs_date'] = dates

            if site['algo_ys_vege']:
                vals = [float(val) for val in site['algo_ys_vege']]
                site['algo_ys_vege'] = vals

            if site['algo_ys_harm']:
                vals = [float(val) for val in site['algo_ys_harm']]
                site['algo_ys_harm'] = vals

            if site['algo_ys_chng']:
                vals = [float(val) for val in site['algo_ys_chng']]
                site['algo_ys_chng'] = vals

        return sites

    def _encodeSites(self, sites):
        """Some formats not supported by json, this encodes them."""

        for site in sites:

            if site['polygon']:
                coords = [QGeoCoordinate(y, x) for x, y in site['polygon']]
                site['polygon'] = coords

            # TODO: load xr?

            if site['algo_xs_date']:
                dates = [dt for dt in site['algo_xs_date']]
                dates = [datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') for dt in dates]
                site['algo_xs_date'] = dates

        return sites

    def save(self):
        """Save all sites as json file to output folder."""

        decoded_sites = self._decodeSites()

        out_fn = os.path.join(self._out_folder, 'sites.json')
        with open(out_fn, 'w') as f:
            json.dump(decoded_sites, f)

        return

    def load(self):
        """Load existing sites from json file in output folder"""
        try:
            in_fn = os.path.join(self._out_folder, 'sites.json')

            if not os.path.exists(in_fn):
                return []

            with open(in_fn, 'r') as f:
                sites = json.load(f)

        except Exception:
            raise 'Error loading json!'

        if sites:
            self._sites = self._encodeSites(sites)

        return
    # endregion


class NewSite(QObject):

    def __init__(self):
        super(NewSite, self).__init__()

        self._id = 0
        self._project = None
        self._code = None
        self._polygon = []
        self._out_folder = None
        self._nc_file = None
        self._xr_dataset = None

        self._train_start = 2018
        self._train_end = 2021
        self._test_end = 2024
        self._num_harmonics = 2
        self._xbar_limit_1 = 1.5
        self._xbar_limit_2 = 20
        self._lambda_value = 0.3
        self._lambda_stdvs = 3
        self._low_thresh = 100
        self._persistence = 3
        self._rounding = True

        self._algo_xs_date = []
        self._algo_ys_vege = []
        self._algo_ys_harm = []
        self._algo_ys_chng = []

        self._is_processing = False
        self._stac_progress = 0
        self._mask_progress = 0
        self._band_progress = 0
        self._progress_text = None

        self._series_vege = None
        self._series_harm = None
        self._series_chng = None

        self._pool = QThreadPool()
        self._pool.setMaxThreadCount(1)

    # region GETTERS & SETTERS (PYTHON-SIDE)
    def get_id(self):
        return self._id

    def set_id(self, val):
        if self._id != val:
            self._id = val
            self.idChanged.emit(self._id)

    def get_project(self):
        return self._project

    def set_project(self, val):
        if self._project != val:
            self._project = val
            self.projectChanged.emit(self._project)

    def get_code(self):
        return self._code

    def set_code(self, val):
        if self._code != val:
            self._code = val
            self.codeChanged.emit(self._code)

    def get_polygon(self):
        return self._polygon

    def set_polygon(self, val):
        if self._polygon != val:
            self._polygon = val
            self.polygonChanged.emit(self._polygon)

    def get_out_folder(self):
        return self._out_folder

    def set_out_folder(self, val):
        if self._out_folder != val:
            self._out_folder = val
            self.outFolderChanged.emit(self._out_folder)

    def get_nc_file(self):
        return self._nc_file

    def set_nc_file(self, val):
        if self._nc_file != val:
            self._nc_file = val
            self.ncFileChanged.emit(self._nc_file)

    def get_xr_dataset(self):
        return self._xr_dataset

    def set_xr_dataset(self, val):
        if self._xr_dataset != val:
            self._xr_dataset = val
            self.xrDatasetChanged.emit(self._xr_dataset)

    def get_train_start(self):
        return self._train_start

    def set_train_start(self, val):
        if self._train_start != val:
            self._train_start = val
            self.trainStartChanged.emit(self._train_start)

    def get_train_end(self):
        return self._train_end

    def set_train_end(self, val):
        if self._train_end != val:
            self._train_end = val
            self.trainEndChanged.emit(self._train_end)

    def get_test_end(self):
        return self._test_end

    def set_test_end(self, val):
        if self._test_end != val:
            self._test_end = val
            self.testEndChanged.emit(self._test_end)

    def get_num_harmonics(self):
        return self._num_harmonics

    def set_num_harmonics(self, val):
        if self._num_harmonics != val:
            self._num_harmonics = val
            self.numHarmonicsChanged.emit(self._num_harmonics)

    def get_xbar_limit_1(self):
        return self._xbar_limit_1

    def set_xbar_limit_1(self, val):
        if self._xbar_limit_1 != val:
            self._xbar_limit_1 = val
            self.xbarLimit1Changed.emit(self._xbar_limit_1)

    def get_xbar_limit_2(self):
        return self._xbar_limit_2

    def set_xbar_limit_2(self, val):
        if self._xbar_limit_2 != val:
            self._xbar_limit_2 = val
            self.xbarLimit2Changed.emit(self._xbar_limit_2)

    def get_lambda_value(self):
        return self._lambda_value

    def set_lambda_value(self, val):
        if self._lambda_value != val:
            self._lambda_value = val
            self.lambdaValueChanged.emit(self._lambda_value)

    def get_lambda_stdvs(self):
        return self._lambda_stdvs

    def set_lambda_stdvs(self, val):
        if self._lambda_stdvs != val:
            self._lambda_stdvs = val
            self.lambdaStdvsChanged.emit(self._lambda_stdvs)

    def get_low_thresh(self):
        return self._low_thresh

    def set_low_thresh(self, val):
        if self._low_thresh != val:
            self._low_thresh = val
            self.lowThreshChanged.emit(self._low_thresh)

    def get_persistence(self):
        return self._persistence

    def set_persistence(self, val):
        if self._persistence != val:
            self._persistence = val
            self.persistenceChanged.emit(self._persistence)

    def get_rounding(self):
        return self._rounding

    def set_rounding(self, val):
        if self._rounding != val:
            self._rounding = val
            self.roundingChanged.emit(self._rounding)

    def get_algo_xs_date(self):
        return self._algo_xs_date

    def set_algo_xs_date(self, val):
        #if self._algo_xs_date != val:  # FIXME: do check
        self._algo_xs_date = val
        self.algoXsDateChanged.emit(self._algo_xs_date)

    def get_algo_ys_vege(self):
        return self._algo_ys_vege

    def set_algo_ys_vege(self, val):
        #if self._algo_ys_vege != val:  # FIXME: do check
        self._algo_ys_vege = val
        self.algoYsVegeChanged.emit(self._algo_ys_vege)

    def get_algo_ys_harm(self):
        return self._algo_ys_harm

    def set_algo_ys_harm(self, val):
        #if self._algo_ys_harm != val:  # FIXME: do check
        self._algo_ys_harm = val
        self.algoYsHarmChanged.emit(self._algo_ys_harm)

    def get_algo_ys_chng(self):
        return self._algo_ys_chng

    def set_algo_ys_chng(self, val):
        #if self._algo_ys_chng != val:  # FIXME: do check
        self._algo_ys_chng = val
        self.algoYsChngChanged.emit(self._algo_ys_chng)

    def get_is_processing(self):
        return self._is_processing

    def set_is_processing(self, val):
        if self._is_processing != val:
            self._is_processing = val
            self.isProcessingChanged.emit(self._is_processing)

    def get_stac_progress(self):
        return self._stac_progress

    def set_stac_progress(self, val):
        if self._stac_progress != val:
            self._stac_progress = val
            self.stacProgressChanged.emit(self._stac_progress)

    def get_mask_progress(self):
        return self._mask_progress

    def set_mask_progress(self, val):
        if self._mask_progress != val:
            self._mask_progress = val
            self.maskProgressChanged.emit(self._mask_progress)

    def get_band_progress(self):
        return self._band_progress

    def set_band_progress(self, val):
        if self._band_progress != val:
            self._band_progress = val
            self.bandProgressChanged.emit(self._band_progress)

    def get_progress_text(self):
        return self._progress_text

    def set_progress_text(self, val):
        if self._progress_text != val:
            self._progress_text = val
            self.progressTextChanged.emit(self._progress_text)
    # endregion

    # region GETTERS & SETTERS (QML-SIDE)
    @Slot(QGeoCoordinate)
    def appendCoordinateToPolygon(self, coordinate):
        polygon = self._polygon.copy()
        polygon.append(coordinate)
        self.set_polygon(polygon)

    @Slot()
    def removeCoordinateFromPolygon(self):
        polygon = self._polygon.copy()
        if len(polygon) > 0:
            polygon.pop()
            self.set_polygon(polygon)

    @Slot()
    def convertPolygonToCoordinates(self):
        if self._polygon:
            xs = [xy.longitude() for xy in self._polygon]
            ys = [xy.latitude() for xy in self._polygon]
            xys = list(zip(xs, ys))

            return xys
    # endregion

    # region CUBE DOWNLOAD FUNCS
    @Slot()
    def downloadCube(self):
        worker = workers.NewSiteDownloadWorker(self._downloadCubeWrapper)

        # callback stac, mask, band and message funcs
        worker.stac_cb_fn = self.incStacProgress
        worker.mask_cb_fn = self.incMaskProgress
        worker.band_cb_fn = self.incBandProgress
        worker.text_cb_fn = self.appendProgressText

        self._pool.start(worker)

    def _downloadCubeWrapper(self, stac_cb_fn, mask_cb_fn, band_cb_fn, text_cb_fn):

        # unpack polygon geocoords to list of lon/lat tuples
        coordinates = self.convertPolygonToCoordinates()

        out_folder = self.out_folder  # FIXME: need to implement
        out_folder = r'C:\Users\Lewis\Desktop\mon'
        out_nc = os.path.join(out_folder, 'new_site.nc')

        if len(self._polygon) < 3:
            raise

        self.set_is_processing(True)

        try:
            ds = downloader.download_new_site_cube(
                in_poly=coordinates,
                out_nc=out_nc,
                stac_cb_fn=stac_cb_fn,
                mask_cb_fn=mask_cb_fn,
                band_cb_fn=band_cb_fn,
                text_cb_fn=text_cb_fn
            )

            # TODO: figure out how to implement this better
            ds['ndvi'] = ((ds['nir_1'] - ds['red']) / (ds['nir_1'] + ds['red']))
            ds = ds[['ndvi']].median(['x', 'y'])
            ds = ds * 10000  # FIXME: decimal values not working when rounding=False, need to * 10000

            ds_tmp = ds.copy(deep=True)
            self.set_xr_dataset(ds_tmp)

            ds.close()
            ds = None

        except:
            self.set_is_processing(False)
            raise

        self.set_is_processing(False)

    @Slot()
    def downloadCubeTesting(self):
        ds = xr.open_dataset(r'C:\Users\Lewis\Desktop\mon\cube_test.nc')
        ds.load()
        self.set_xr_dataset(ds)
    # endregion

    # region CHART FUNCS
    @Slot(QAbstractSeries, QAbstractSeries, QAbstractSeries)
    def refreshCharts(self, series_vege, series_harm, series_chng):
        # update chart series
        self._series_vege = series_vege
        self._series_harm = series_harm
        self._series_chng = series_chng

        worker = workers.EwmacdChartsWorker(self._refreshEwmacdAndChartsWrapper)
        self._pool.start(worker)

        return

    def _refreshEwmacdAndChartsWrapper(self):
        self._refreshEwmacd()
        self._refreshChartSeries()
        #self._align_y_axes()

        return

    def _refreshEwmacd(self):
        dates, y_raw, y_hrm, y_res = algos.ewmacd(self._xr_dataset,
                                                  self._train_start,
                                                  self._train_end,
                                                  self._test_end,
                                                  self._num_harmonics,
                                                  self._xbar_limit_1,
                                                  self._xbar_limit_2,
                                                  self._low_thresh,
                                                  self._lambda_value,
                                                  self._lambda_stdvs,
                                                  self._rounding,
                                                  self._persistence)

        self.set_algo_xs_date(dates)
        self.set_algo_ys_vege(y_raw)
        self.set_algo_ys_harm(y_hrm)
        self.set_algo_ys_chng(y_res)

        return

    def _refreshChartSeries(self):

        xs = self._algo_xs_date
        xs = pd.DatetimeIndex(xs)
        xs = [QDateTime(x) for x in xs]

        ys_vege = self._algo_ys_vege
        ys_harm = self._algo_ys_harm

        self._series_vege.clear()
        for x, y in zip(xs, ys_vege):
            self._series_vege.append(x.toMSecsSinceEpoch(), y)

        self._series_harm.clear()
        for x, y in zip(xs, ys_harm):
            self._series_harm.append(x.toMSecsSinceEpoch(), y)

        x_axis, y_axis = self._series_vege.attachedAxes()  # vege, harm same axes

        x_axis.setRange(xs[0], xs[-1])
        y_axis.setMin(np.min([ys_vege, ys_harm]))
        y_axis.setMax(np.max([ys_vege, ys_harm]))

        # years = np.unique(ds['time.year'])[:-1]
        # num_ticks = len(years) * 4
        # x_axis.setTickCount(num_ticks)

        ys_chng = self._algo_ys_chng

        self._series_chng.clear()
        for x, y in zip(xs, ys_chng):
            self._series_chng.append(x.toMSecsSinceEpoch(), y)

        x_axis, y_axis = self._series_chng.attachedAxes()
        x_axis.setRange(xs[0], xs[-1])
        y_axis.setMin(min(ys_chng))
        y_axis.setMax(max(ys_chng))

    def _align_y_axes(self):
        # TODO: get this working

        chart_vege = self._series_vege.chart()
        chart_chng = self._series_chng.chart()

        #rect = QRectF(60.0, 40.0, 900.0, 270.0)

        #best_rect = chart_vege.plotArea()

        #chart_vege.setPlotArea(rect)
        #chart_chng.setPlotArea(best_rect)

        #chart_vege.plotArea()

        # best_chart = chart_vege
        # best_rect = QRectF() #chart_vege.plotArea() # try empty rect here
        #
        # charts = [chart_vege, chart_chng]
        # for chart in charts:
        #     if chart.plotArea().left() > best_rect.left():
        #         best_chart = chart
        #         best_rect = chart.plotArea()
        #         chart.setMargins(QMargins(20, 0, 20, 0))
        #
        # for chart in charts:
        #     if chart != best_chart:
        #         l = chart.margins().left() + (best_rect.left() - chart.plotArea().left())
        #         r = chart.margins().right() + (chart.plotArea().right() - best_rect.right())
        #         chart.setMargins(QMargins(l, 0, r, 0))

        print('\n')
    # endregion

    # region IO FUNCS
    def export_site(self):

        out = {
            'id': self._id,
            'project': self._project,
            'code': self._code,
            'polygon': self._polygon,
            'out_folder': self._out_folder,
            'nc_file': self._nc_file,
            'xr_dataset': self._xr_dataset,
            'train_start': self._train_start,
            'train_end': self._train_end,
            'test_end': self._test_end,
            'num_harmonics': self._num_harmonics,
            'xbar_limit_1': self._xbar_limit_1,
            'xbar_limit_2': self._xbar_limit_2,
            'lambda_value': self._lambda_value,
            'lambda_stdvs': self._lambda_stdvs,
            'low_thresh': self._low_thresh,
            'persistence': self._persistence,
            'rounding': self._rounding,
            'algo_xs_date': self._algo_xs_date,
            'algo_ys_vege': self._algo_ys_vege,
            'algo_ys_harm': self._algo_ys_harm,
            'algo_ys_chng': self._algo_ys_chng
        }

        return out
    # endregion

    # region CALLBACK FUNCS
    @Slot(float)
    def incStacProgress(self, val):
        if val > self._stac_progress:
            self.set_stac_progress(val)

    @Slot(float)
    def incMaskProgress(self, val):
        if val > self.mask_progress:
            self.set_mask_progress(val)

    @Slot(float)
    def incBandProgress(self, val):
        if val > self.band_progress:
            self.set_band_progress(val)

    @Slot(str)
    def appendProgressText(self, val):
        if val != self._progress_text:
            txt = self._progress_text
            txt = txt if txt else ''
            txt = txt + val + '\n'
            self.set_progress_text(txt)
    # endregion

    # region SIGNALS
    idChanged = Signal(int)
    projectChanged = Signal(str)
    codeChanged = Signal(str)
    polygonChanged = Signal(list)
    outFolderChanged = Signal(str)
    ncFileChanged = Signal(str)
    xrDatasetChanged = Signal(xr.Dataset)

    trainStartChanged = Signal(int)
    trainEndChanged = Signal(int)
    testEndChanged = Signal(int)
    numHarmonicsChanged = Signal(int)
    xbarLimit1Changed = Signal(float)
    xbarLimit2Changed = Signal(float)
    lambdaValueChanged = Signal(float)
    lambdaStdvsChanged = Signal(int)
    lowThreshChanged = Signal(float)
    persistenceChanged = Signal(int)
    roundingChanged = Signal(bool)

    algoXsDateChanged = Signal(list)
    algoYsVegeChanged = Signal(list)
    algoYsHarmChanged = Signal(list)
    algoYsChngChanged = Signal(list)

    isProcessingChanged = Signal(bool)
    stacProgressChanged = Signal(float)
    maskProgressChanged = Signal(float)
    bandProgressChanged = Signal(float)
    progressTextChanged = Signal(str)
    # endregion

    # region PROPERTIES
    id = Property(int, get_id, set_id, notify=idChanged)
    project = Property(str, get_project, set_project, notify=projectChanged)
    code = Property(str, get_code, set_code, notify=codeChanged)
    polygon = Property(list, get_polygon, set_polygon, notify=polygonChanged)
    out_folder = Property(str, get_out_folder, set_out_folder, notify=outFolderChanged)
    nc_file = Property(str, get_nc_file, set_nc_file, notify=ncFileChanged)
    xr_dataset = Property(xr.Dataset, get_xr_dataset, set_xr_dataset, notify=xrDatasetChanged)

    train_start = Property(int, get_train_start, set_train_start, notify=trainStartChanged)
    train_end = Property(int, get_train_end, set_train_end, notify=trainEndChanged)
    test_end = Property(int, get_test_end, set_test_end, notify=testEndChanged)
    num_harmonics = Property(int, get_num_harmonics, set_num_harmonics, notify=numHarmonicsChanged)
    xbar_limit_1 = Property(float, get_xbar_limit_1, set_xbar_limit_1, notify=xbarLimit1Changed)
    xbar_limit_2 = Property(float, get_xbar_limit_2, set_xbar_limit_2, notify=xbarLimit2Changed)
    lambda_value = Property(float, get_lambda_value, set_lambda_value, notify=lambdaValueChanged)
    lambda_stdvs = Property(int, get_lambda_stdvs, set_lambda_stdvs, notify=lambdaStdvsChanged)
    low_thresh = Property(float, get_low_thresh, set_low_thresh, notify=lowThreshChanged)
    persistence = Property(int, get_persistence, set_persistence, notify=persistenceChanged)
    rounding = Property(bool, get_rounding, set_rounding, notify=roundingChanged)

    algo_xs_date = Property(list, get_algo_xs_date, set_algo_xs_date, notify=algoXsDateChanged)
    algo_ys_vege = Property(list, get_algo_ys_vege, set_algo_ys_vege, notify=algoYsVegeChanged)
    algo_ys_harm = Property(list, get_algo_ys_harm, set_algo_ys_harm, notify=algoYsHarmChanged)
    algo_ys_chng = Property(list, get_algo_ys_chng, set_algo_ys_chng, notify=algoYsChngChanged)

    is_processing = Property(bool, get_is_processing, set_is_processing, notify=isProcessingChanged)
    stac_progress = Property(float, get_stac_progress, set_stac_progress, notify=stacProgressChanged)
    mask_progress = Property(float, get_mask_progress, set_mask_progress, notify=maskProgressChanged)
    band_progress = Property(float, get_band_progress, set_band_progress, notify=bandProgressChanged)
    progress_text = Property(str, get_progress_text, set_progress_text, notify=progressTextChanged)
    # endregion

