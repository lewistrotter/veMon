
import os
#import sys
import time
import datetime
import shutil
#import traceback
import numpy as np
import xarray as xr
import shapely
import geopandas as gpd

from PySide6 import QtCore
from PySide6 import QtPositioning
from PySide6 import QtCharts

# https://forum.qt.io/topic/77439/can-someone-provide-a-working-example-of-vxymodelmapper-with-lineseries-chart/2
import working

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from dea import stac, cube


class CalibrateModel(QtCore.QObject):

    # region SIGNALS
    # general parameters
    isMapValidChanged = QtCore.Signal()

    # ewmacd parameters
    trainStartChanged = QtCore.Signal()
    trainEndChanged = QtCore.Signal()
    testEndChanged = QtCore.Signal()
    numHarmonicsChanged = QtCore.Signal()
    xBarLimit1Changed = QtCore.Signal()
    xBarLimit2Changed = QtCore.Signal()
    lambdaValueChanged = QtCore.Signal()
    lambdaStdvsChanged = QtCore.Signal()
    lowThreshChanged = QtCore.Signal()
    persistenceChanged = QtCore.Signal()
    roundingChanged = QtCore.Signal()
    isProcessingChanged = QtCore.Signal()
    stacQueryProgressChanged = QtCore.Signal()
    stacIsIndeterminate = QtCore.Signal()
    cubeMaskProgressChanged = QtCore.Signal()
    cubeBandProgressChanged = QtCore.Signal()
    progressTextChanged = QtCore.Signal()

    # endregion

    # region INIT
    def __init__(self):
        super().__init__()

        # mapping
        self._poly = []

        # sat data cube
        self._nc = r"C:\Users\Lewis\Desktop\mon\cube.nc"
        self._ds = None



        # FIXME: disable this when charts fixed
        # FIXIME: also set stkrootstackview init item back to map
        ds = xr.open_dataset(self._nc)
        ds['ndvi'] = (ds['nir_1'] - ds['red']) / (ds['nir_1'] + ds['red'])
        ds = ds[['ndvi']].median(['x', 'y'])          #ds = ds # ds.resample(time='M').median()
        ds = ds * 10000  # FIXME: decimal values not working when rounding=False, need to * 10000
        self._ds = ds.copy(deep=True)
        ds.close()
        ds = None


        # TODO: set some of the min/max values based on ls/s2 data
        # TODO: set test end from current date + 1
        # ewmacd parameters
        self._train_start = 2018
        self._train_end = 2021
        self._test_end = 2024
        self._num_harmonics = 2
        self._xbar_limit_1 = 1.5
        self._xbar_limit_2 = 20
        self._lambda_value = 0.3
        self._lambda_stdvs = 3
        self._low_thresh = 0.1
        self._persistence = 3
        self._rounding = True

        # ewmacd outputs
        self._dts = []
        self._raw = []
        self._hrm = []
        self._chg = []

        # threads
        self._pool = QtCore.QThreadPool()  # TODO: move this to outer container eventually
        self._pool.setMaxThreadCount(1)

        # processing flags
        self._is_processing = False

        # progress
        self._stac_query_progress = 0
        self._stac_is_indeterminate = False
        self._cube_mask_progress = 0
        self._cube_band_progress = 0
        self._progress_text = ""

    # endregion

    # region GETTERS / SETTERS
    # note: property / setter method removes need for property objs
    @QtCore.Property(int, notify=trainStartChanged)
    def train_start(self):
        return self._train_start

    @train_start.setter
    def train_start(self, val):
        if val >= self._train_end:
            val = self._train_end - 1

        self._train_start = val
        self.trainStartChanged.emit()

    @QtCore.Property(int, notify=trainEndChanged)
    def train_end(self):
        return self._train_end

    @train_end.setter
    def train_end(self, val):
        if val <= self._train_start:
            val = self._train_start + 1

        if val >= self._test_end:
            val = self._test_end - 1

        self._train_end = val
        self.trainEndChanged.emit()

    @QtCore.Property(int, notify=testEndChanged)
    def test_end(self):
        return self._test_end

    @test_end.setter
    def test_end(self, val):
        if val <= self._train_end:
            val = self._train_end + 1

        self._test_end = val
        self.testEndChanged.emit()

    @QtCore.Property(int, notify=numHarmonicsChanged)
    def num_harmonics(self):
        return self._num_harmonics

    @num_harmonics.setter
    def num_harmonics(self, val):
        self._num_harmonics = val
        self.numHarmonicsChanged.emit()

    @QtCore.Property(float, notify=xBarLimit1Changed)
    def xbar_limit_1(self):
        return self._xbar_limit_1

    @xbar_limit_1.setter
    def xbar_limit_1(self, val):
        self._xbar_limit_1 = val
        self.xBarLimit1Changed.emit()

    @QtCore.Property(int, notify=xBarLimit2Changed)
    def xbar_limit_2(self):
        return self._xbar_limit_2

    @xbar_limit_2.setter
    def xbar_limit_2(self, val):
        self._xbar_limit_2 = val
        self.xBarLimit2Changed.emit()

    @QtCore.Property(float, notify=lambdaValueChanged)
    def lambda_value(self):
        return self._lambda_value

    @lambda_value.setter
    def lambda_value(self, val):
        self._lambda_value = val
        self.lambdaValueChanged.emit()

    @QtCore.Property(float, notify=lambdaStdvsChanged)
    def lambda_stdvs(self):
        return self._lambda_stdvs

    @lambda_stdvs.setter
    def lambda_stdvs(self, val):
        self._lambda_stdvs = val
        self.lambdaStdvsChanged.emit()

    @QtCore.Property(float, notify=lowThreshChanged)
    def low_thresh(self):
        return self._low_thresh

    @low_thresh.setter
    def low_thresh(self, val):
        self._low_thresh = val
        self.lowThreshChanged.emit()

    @QtCore.Property(int, notify=persistenceChanged)
    def persistence(self):
        return self._persistence

    @persistence.setter
    def persistence(self, val):
        self._persistence = val
        self.persistenceChanged.emit()

    @QtCore.Property(bool, notify=roundingChanged)
    def rounding(self):
        return self._rounding

    @rounding.setter
    def rounding(self, val):
        self._rounding = val
        self.roundingChanged.emit()

    @QtCore.Property(bool, notify=isProcessingChanged)
    def is_processing(self):
        return self._is_processing

    @is_processing.setter
    def is_processing(self, val):
        self._is_processing = val
        self.isProcessingChanged.emit()

    @QtCore.Property(bool, notify=stacIsIndeterminate)
    def stac_is_indeterminate (self):
        return self._stac_is_indeterminate

    @stac_is_indeterminate.setter
    def stac_is_indeterminate(self, val):
        self._stac_is_indeterminate = val
        self.stacIsIndeterminate.emit()

    @QtCore.Property(float, notify=stacQueryProgressChanged)
    def stac_query_progress(self):
        return self._stac_query_progress

    @stac_query_progress.setter
    def stac_query_progress(self, val):
        self._stac_query_progress = val
        self.stacQueryProgressChanged.emit()

    @QtCore.Property(float, notify=cubeMaskProgressChanged)
    def cube_mask_progress(self):
        return self._cube_mask_progress

    @cube_mask_progress.setter
    def cube_mask_progress(self, val):
        self._cube_mask_progress = val
        self.cubeMaskProgressChanged.emit()

    @QtCore.Property(float, notify=cubeBandProgressChanged)
    def cube_band_progress(self):
        return self._cube_band_progress

    @cube_band_progress.setter
    def cube_band_progress(self, val):
        self._cube_band_progress = val
        self.cubeBandProgressChanged.emit()

    @QtCore.Property(str, notify=progressTextChanged)
    def progress_text(self):
        return self._progress_text

    @progress_text.setter
    def progress_text(self, txt):
        self._progress_text += txt + '\n'
        self.progressTextChanged.emit()

    # endregion

    # region CALLBACKS
    def flip_processing_flag(self, val):
        self.is_processing = val

    def inc_stac_query_progress(self, i):
        self.stac_query_progress = i

    def flip_stac_is_indeterminate(self, val):
        self.stac_is_indeterminate = val

    def inc_cube_mask_progress(self, i):
        self.cube_mask_progress = i

    def inc_cube_band_progress(self, i):
        self.cube_band_progress = i

    def add_progress_text(self, txt):
        self.progress_text = txt

    # endregion

    # region MAP
    @QtCore.Slot(QtPositioning.QGeoCoordinate)
    def append_poly_vertex(self, vertex):
        xy = vertex.longitude(), vertex.latitude()
        self._poly.append(xy)

        if len(self._poly) >= 3:
            self.is_map_valid = True

    @QtCore.Slot()
    def reset_poly_vertices(self):
        self._poly = []
        self.is_map_valid = False
    # endregion

    # region ANALYSIS
    @QtCore.Slot()
    def run_ewmacd(self):

        # TODO: return x dates too
        dates, y_raw, y_hrm, y_res = working.ewmacd(self._ds,
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

        #self._dts = np.arange(len(y_raw))  # TODO: remove when abvoe done
        self._dts = dates
        self._raw, self._hrm, self._chg = y_raw, y_hrm, y_res

    @QtCore.Slot()
    def _download_dea_data(
            self,
            is_processing_cb,
            stac_progress_cb,
            stac_is_indeterminate_cb,
            mask_progress_cb,
            band_progress_cb,
            progress_text_cb
    ):
        # flag processing is on
        is_processing_cb.emit(True)

        # uncomment these when testing
        #in_lyr = r'C:\Users\Lewis\Desktop\arcdea\studyarea.shp'
        #out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_oh.nc'
        in_start_date = datetime.datetime(2016, 1, 1)
        in_end_date = datetime.datetime.now()
        in_collections = "'Sentinel 2A';'Sentinel 2B'"
        in_band_assets = "'Blue';'Green';'Red';'NIR 1'"
        in_mask_algorithm = 'S2Cloudless'  # 'fMask'  # 'S2Cloudless'  # FIXME: s2cloudless removes a lot of images... even at 50%!
        in_quality_flags = "Valid"  # "'Valid';'Shadow';'Snow';'Water'"  # "Valid"
        in_max_out_of_bounds = 10
        in_max_invalid_pixels = 5
        in_keep_mask = False
        in_nodata_value = -999
        in_srs = 'GDA94 Australia Albers (EPSG: 3577)'  # 'WGS84 (EPSG: 4326)'
        in_res = 10
        in_max_threads = None

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region PREPARE PARAMETERS

        progress_text_cb.emit('Preparing DEA STAC query parameters...')

        # fc_bbox = shared.get_bbox_from_featureclass(in_lyr)
        # fc_epsg = shared.get_epsg_from_featureclass(in_lyr)
        fc_bbox = self._poly
        xs = [xy[0] for xy in self._poly]
        ys = [xy[1] for xy in self._poly]
        fc_bbox = [np.min(xs), np.min(ys), np.max(xs), np.max(ys)]

        fc_epsg = 4326

        start_date = in_start_date.date().strftime('%Y-%m-%d')
        end_date = in_end_date.date().strftime('%Y-%m-%d')

        # collections = shared.prepare_collections(in_collections)
        # assets = shared.prepare_assets(in_band_assets)
        collections = ['ga_s2am_ard_3', 'ga_s2bm_ard_3']
        assets = ['red', 'nir_1']

        # quality_flags = shared.prepare_quality_flags(in_quality_flags, in_mask_algorithm)
        # mask_algorithm = shared.prepare_mask_algorithm(in_mask_algorithm)
        # assets = shared.append_mask_band(assets, mask_algorithm)  # append mask band to user bands
        quality_flags = [1]
        mask_algorithm = 'oa_s2cloudless_mask'
        assets = assets + [mask_algorithm]

        # max_out_of_bounds = shared.prepare_max_out_of_bounds(in_max_out_of_bounds)
        # max_invalid_pixels = shared.prepare_max_invalid_pixels(in_max_invalid_pixels)
        max_out_of_bounds = 5.0
        max_invalid_pixels = 5.0

        # out_nodata = in_nodata_value
        # out_epsg = shared.prepare_spatial_reference(in_srs)
        # out_res = shared.prepare_resolution(in_res, out_epsg)
        # out_dtype = 'int16'  # output dtype always int16 for baseline
        out_nodata = -999
        out_epsg = 3577
        out_res = 10.0
        out_dtype = 'int16'

        # max_threads = shared.prepare_max_threads(in_max_threads)  # if user gave none, uses max cpus - 1
        max_threads = 12

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region QUERY STAC ENDPOINT

        progress_text_cb.emit('Querying DEA STAC endpoint...')

        try:
            stac_progress_cb.emit(0)
            stac_is_indeterminate_cb.emit(True)

            # reproject stac bbox to wgs 1984, fetch all available stac items
            # stac_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, 4326)
            stac_bbox = fc_bbox
            stac_features = stac.fetch_all_stac_feats(collections,
                                                      start_date,
                                                      end_date,
                                                      stac_bbox,
                                                      100)

            stac_progress_cb.emit(100)
            stac_is_indeterminate_cb.emit(False)

        except Exception as e:
            # arcpy.AddError('Error occurred during DEA STAC query. See messages.')
            # arcpy.AddMessage(str(e))
            raise  # return

        if len(stac_features) == 0:
            # arcpy.AddWarning('No STAC features were found.')
            raise  # return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region PREPARING STAC FEATURES

        progress_text_cb.emit('Preparing STAC downloads...')

        root_folder = os.path.dirname(self._nc)
        tmp_folder = os.path.join(root_folder, 'tmp')

        # shared.drop_temp_folder(tmp_folder)
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)

        # shared.create_temp_folder(tmp_folder)
        if not os.path.exists(tmp_folder):
            os.mkdir(tmp_folder)

        try:
            # TODO: needs rework for threading
            # out_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
            poly_geom = shapely.Polygon(self._poly)
            poly = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[poly_geom])
            poly = poly.to_crs('epsg:3577')
            out_bbox = list(poly.total_bounds)

            stac_downloads = stac.convert_stac_feats_to_stac_downloads(stac_features,
                                                                       assets,
                                                                       mask_algorithm,
                                                                       quality_flags,
                                                                       max_out_of_bounds,
                                                                       max_invalid_pixels,
                                                                       out_bbox,
                                                                       out_epsg,
                                                                       out_res,
                                                                       out_nodata,
                                                                       out_dtype,
                                                                       tmp_folder)

        except Exception as e:
            progress_text_cb.emit('Error occurred during STAC download preparation.')
            progress_text_cb.emit(str(e))
            return

        stac_downloads = stac.group_stac_downloads_by_solar_day(stac_downloads)

        if len(stac_downloads) == 0:
            progress_text_cb.emit('No valid downloads were found.')
            return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region DOWNLOAD WCS MASK DATA

        progress_text_cb.emit('\n' + 'Downloading and validating mask data...')

        try:
            mask_progress_cb.emit(0)
            i = 0
            with ThreadPoolExecutor(max_workers=max_threads) as pool:
                futures = []
                for stac_download in stac_downloads:
                    task = pool.submit(cube.worker_read_mask_and_validate, stac_download)
                    futures.append(task)

                for future in as_completed(futures):
                    msg = '-' + ' ' + future.result()
                    progress_text_cb.emit(msg)

                    i += 1
                    if i % 1 == 0:
                        mask_progress_cb.emit((i / len(stac_downloads) * 100))

        except Exception as e:
            progress_text_cb.emit('Error occurred while downloading and validating mask data.')
            progress_text_cb.emit(str(e))
            return

        stac_downloads = cube.remove_mask_invalid_downloads(stac_downloads)

        if len(stac_downloads) == 0:
            progress_text_cb.emit('No valid downloads were found.')
            return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region DOWNLOAD WCS VALID DATA

        progress_text_cb.emit('\n' + 'Downloading valid data...')

        try:
            band_progress_cb.emit(0)
            i = 0
            with ThreadPoolExecutor(max_workers=max_threads) as pool:
                futures = []
                for download in stac_downloads:
                    task = pool.submit(cube.worker_read_bands_and_export, download)
                    futures.append(task)

                for future in as_completed(futures):
                    msg = '-' + ' ' + future.result()
                    progress_text_cb.emit(msg)

                    i += 1
                    if i % 1 == 0:
                        band_progress_cb.emit((i / len(stac_downloads) * 100))

        except Exception as e:
            # arcpy.AddError('Error occurred while downloading valid data. See messages.')
            # arcpy.AddMessage(str(e))
            raise  # return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region CLEAN AND COMBINE NETCDFS

        progress_text_cb.emit('\n' + 'Cleaning and combining NetCDFs...')

        try:
            ds = cube.fix_xr_meta_and_combine(stac_downloads)

        except Exception as e:
            # arcpy.AddError('Error occurred while cleaning and combining NetCDFs. See messages.')
            # arcpy.AddMessage(str(e))
            raise  # return

        time.sleep(1)

        #progress_text_cb.emit('\n' + 'Finished!')

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region MASK OUT INVALID NETCDF PIXELS

        progress_text_cb.emit('Masking out invalid NetCDF pixels...')

        try:
            ds = cube.apply_xr_mask(ds,
                                    quality_flags,
                                    out_nodata,
                                    in_keep_mask)

        except Exception as e:
            #arcpy.AddError('Error occurred while masking out invalid NetCDF pixels. See messages.')
            #arcpy.AddMessage(str(e))
            return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region EXPORT COMBINED NETCDF

        progress_text_cb.emit('Exporting combined NetCDF...')

        try:
            ds.load()
            cube.export_xr_to_nc(ds, self._nc)

        except Exception as e:
            #arcpy.AddError('Error occurred while exporting combined NetCDF. See messages.')
            #arcpy.AddMessage(str(e))
            return

        time.sleep(1)

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region AGGREGATE NDVI

        # TODO: figure out how to implement this better
        progress_text_cb.emit('Calculating NDVI and aggregating (temp)...')

        ds['ndvi'] = (ds['nir_1'] - ds['red']) / (ds['nir_1'] + ds['red'])
        ds = ds[['ndvi']].median(['x', 'y'])          #ds = ds # ds.resample(time='M').median()
        ds = ds * 10000  # FIXME: decimal values not working when rounding=False, need to * 10000
        self._ds = ds.copy(deep=True)

        ds.close()
        ds = None

        # endregion

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # region CLEAN UP ENVIRONMENT

        #arcpy.SetProgressor('default', 'Cleaning up environment...')
        progress_text_cb.emit('Cleaning up environment...')

        cube.safe_close_ncs(tmp_folder)  # TODO: surely there is better way

        #shared.drop_temp_folder(tmp_folder)
        try:
            if os.path.exists(tmp_folder):
                shutil.rmtree(tmp_folder)
        except:
            pass

        time.sleep(1)

        progress_text_cb.emit('\n' + 'Finished!')

        # flag processing is on
        is_processing_cb.emit(False)

        # endregion

    @QtCore.Slot()
    def run_dea_downloader(self):
        worker = Worker(self._download_dea_data)

        worker.signals.is_processing.connect(self.flip_processing_flag)
        worker.signals.stac_progress.connect(self.inc_stac_query_progress)
        worker.signals.stac_indeterminate.connect(self.flip_stac_is_indeterminate)
        worker.signals.mask_progress.connect(self.inc_cube_mask_progress)
        worker.signals.band_progress.connect(self.inc_cube_band_progress)
        worker.signals.progress_text.connect(self.add_progress_text)

        self._pool.start(worker)

    # endregion

    # region CHARTS

    @QtCore.Slot(QtCharts.QAbstractSeries, QtCharts.QAbstractSeries, QtCharts.QAbstractSeries)
    def refresh_charts(self, series_raw, series_hrm, series_chg):

        # TODO: consider if this should be saved as property or not
        self._dts = [QtCore.QDateTime(dt) for dt in self._dts]

        # update veg (raw)  chart data points
        series_raw.clear()
        for x, y in zip(self._dts, self._raw):
            series_raw.append(x.toMSecsSinceEpoch(), y)

        # update veg (harmonic) chart data points
        series_hrm.clear()
        for x, y in zip(self._dts, self._hrm):
            series_hrm.append(x.toMSecsSinceEpoch(), y)

        # update chg chart data points
        series_chg.clear()
        for x, y in zip(self._dts, self._chg):
            series_chg.append(x.toMSecsSinceEpoch(), y)

        try:
            # update veg, chg chart axes
            self._refresh_veg_chart_axes(series_raw, series_hrm)
            self._refresh_chg_chart_axes(series_chg)
            self._align_x_axes(series_raw, series_chg)

        except:
            print('error')

    def _refresh_veg_chart_axes(self, series_raw, series_hrm):

        #x_min, x_max = np.nanmin(self._dts), np.nanmax(self._dts)
        x_min, x_max = self._dts[0], self._dts[-1]

        ys = np.concatenate([self._raw, self._hrm])
        y_min, y_max = np.nanmin(ys), np.nanmax(ys)

        for series in [series_raw, series_hrm]:
            x_axis, y_axis = series_raw.attachedAxes()  # TODO: see if inplace poss

            x_axis.setMin(x_min)
            x_axis.setMax(x_max)
            y_axis.setMin(y_min)
            y_axis.setMax(y_max)

            x_ticks = (self._train_end - self._train_start) * 3
            x_axis.setTickCount(x_ticks)

    def _refresh_chg_chart_axes(self, series_chg):

        x_min, x_max = np.nanmin(self._dts), np.nanmax(self._dts)

        y_min, y_max = np.nanmin(self._chg), np.nanmax(self._chg)
        y_min, y_max = np.floor(y_min) - 1, np.ceil(y_max) + 1

        x_axis, y_axis = series_chg.attachedAxes()  # TODO: see if inplace poss

        x_axis.setMin(x_min)
        x_axis.setMax(x_max)
        y_axis.setMin(y_min)
        y_axis.setMax(y_max)

        x_ticks = (self._train_end - self._train_start) * 3
        x_axis.setTickCount(x_ticks)

    def _align_x_axes(self, series_raw, series_chg):

        chart_raw = series_raw.chart()
        chart_chg = series_chg.chart()

        print(chart_raw.margins().left(), chart_raw.plotArea().left())
        print(chart_chg.margins().left(), chart_chg.plotArea().left())
        print()

        if chart_raw.plotArea().left() > chart_chg.plotArea().left():
            l = chart_chg.margins().left() + (chart_raw.plotArea().left() - chart_chg.plotArea().left())
            r = chart_chg.margins().right() + (chart_chg.plotArea().right() - chart_raw.plotArea().right())
            chart_chg.setMargins(QtCore.QMargins(l, 0, r, 0))

        if chart_raw.plotArea().left() < chart_chg.plotArea().left():
            # this works but breaks resizing of bottom graph...
            _, b, r, t = chart_chg.plotArea().getRect()
            rec = QtCore.QRectF(chart_raw.plotArea().left(), 0, 0, 0) #b, r, t)
            chart_chg.setPlotArea(rec)

            #chart_chg.setMargins(QtCore.QMargins(20, 0, 20, 0))

        print(chart_raw.margins().left(), chart_raw.plotArea().left())
        print(chart_chg.margins().left(), chart_chg.plotArea().left())
        print()

    # endregion



class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['is_processing_cb'] = self.signals.is_processing
        self.kwargs['stac_progress_cb'] = self.signals.stac_progress
        self.kwargs['stac_is_indeterminate_cb'] = self.signals.stac_indeterminate
        self.kwargs['mask_progress_cb'] = self.signals.mask_progress
        self.kwargs['band_progress_cb'] = self.signals.band_progress
        self.kwargs['progress_text_cb'] = self.signals.progress_text

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            # traceback.print_exc()
            # exctype, value = sys.exc_info()[:2]
            # self.signals.error.emit((exctype, value, traceback.format_exc()))
            ...
        finally:
            self.signals.finished.emit()


class WorkerSignals(QtCore.QObject):
    """
    ...
    """
    is_processing = QtCore.Signal(bool)
    stac_progress = QtCore.Signal(float)
    stac_indeterminate = QtCore.Signal(bool)
    mask_progress = QtCore.Signal(float)
    band_progress = QtCore.Signal(float)
    progress_text = QtCore.Signal(str)
    finished = QtCore.Signal()
    result = QtCore.Signal(object)
    error = QtCore.Signal(tuple)
