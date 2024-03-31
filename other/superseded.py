# // ListView {
#                     //     id: view
#                     //     //width: 200
#                     //     //height: 200
#                     //     //anchors.top: slide2.bottom
#                     //     anchors.fill: parent
#                     //     //model: sitesModel
#                     //     model: visualModel
#                     //     //delegate: dele
#                     //     clip: true
#                     //     focus: true
#                     //     interactive: false
#                     // }
#                     //
#                     // DelegateModel {
#                     //     id: visualModel
#                     //     model: sitesModel
#                     //     delegate: dele
#                     //
#                     //     groups: [
#                     //         DelegateModelGroup {
#                     //             name: "newSite"
#                     //             includeByDefault: false
#                     //         }
#                     //     ]
#                     //
#                     //     filterOnGroup: {"newSite"}
#                     //
#                     //     Component.onCompleted: {
#                     //         items.remove(0, sitesModel.rowCount());
#                     //         for (var i = 0; i < sitesModel.rowCount(); i++ ) {
#                     //             var entry = sitesModel.get(i);
#                     //             if(entry.editing === true) {
#                     //                 items.insert(entry, "newSite");
#                     //             }
#                     //         }
#                     //     }
#                     // }
#                     //
#                     // Component {
#                     //     id: dele
#                     //     Rectangle {
#                     //         height: 25
#                     //         width: 100
#                     //         //visible: model.editing
#                     //         Text { text: "Code: " + model.code}
#                     //
#                     //     }
#                     // }
#
#                     // Component {
#                     //     id: dele
#                     //
#                     //     Rectangle {
#                     //         //width: 100
#                     //         //height: 50
#                     //         //required property int index
#                     //         visible: model.editing
#                     //
#                     //         Text {
#                     //             id: txt
#                     //             text: model.code
#                     //         }
#                     //
#                     //         Slider {
#                     //             id: slide
#                     //             anchors.top: txt.bottom
#                     //             from: 2016
#                     //             to: 2024
#                     //             stepSize: 1
#                     //             value: model.train_start
#                     //             onMoved: {
#                     //                 model.train_start = value
#                     //             //     //calibModel.run_ewmacd()
#                     //             //     //calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
#                     //             }
#                     //         }
#                     //
#                     //         // Button {
#                     //         //     anchors.top: slide.bottom
#                     //         //     onClicked: sitesModel.edit(2)
#                     //         //     text: "test"
#                     //         // }
#                     //     }
#                     // }


# class NewSite(QtCore.QObject):
#
#     CodeSignal = QtCore.Signal()
#     TrainStartSignal = QtCore.Signal()
#     TrainEndSignal = QtCore.Signal()
#
#     def __init__(self):
#         super().__init__()
#
#         self._code = ''
#         self._year = ''
#         self._poly = []
#         self._train_start = 2018
#         self._train_end = 2021
#
#     # region EWMACD GETTERS/SETTERS
#     @QtCore.Property(str, notify=CodeSignal)
#     def code(self):
#         return self._code
#
#     @code.setter
#     def code(self, value):
#         if self._code != value:
#             self._code = value
#             self.CodeSignal.emit()
#     # endregion
#
#     # region EWMACD GETTERS/SETTERS
#     @QtCore.Property(int, notify=TrainStartSignal)
#     def train_start(self):
#         return self._train_start
#
#     @train_start.setter
#     def train_start(self, value):
#         if self._train_start != value:
#             self._train_start = value
#             self.TrainStartSignal.emit()
#
#     @QtCore.Property(int, notify=TrainEndSignal)
#     def train_end(self):
#         return self._train_end
#
#     @train_end.setter
#     def train_end(self, value):
#         if self._train_end != value:
#         # if val <= self._train_start:
#         #     val = self._train_start + 1
#         #
#         # if val >= self._test_end:
#         #     val = self._test_end - 1
#
#             self._train_end = value
#             self.TrainEndSignal.emit()
#     # endregion





#class NewSiteCharts(QtCore.QAbstractTableModel):
#
#     def __init__(self, parent=None):
#         super(NewSiteCharts, self).__init__(parent)
#
#         self.column_count = 2
#         self.row_count = 5
#
#         self._data = []
#
#     def rowCount(self, parent=QtCore.QModelIndex()):
#         return len(self._data)
#
#     def columnCount(self, parent=QtCore.QModelIndex()):
#         return self.column_count
#
#     def data(self, index, role):
#         if role == QtCore.Qt.DisplayRole:
#             return self._data[index.row()][index.column()]
#         elif role == QtCore.Qt.EditRole:
#             return self._data[index.row()][index.column()]
#
#         return
#
#     @QtCore.Slot(result=bool)
#     def reset(self):
#         """"""
#         self.beginResetModel()
#         self.resetInternalData()  # should work without calling it ?
#         self.endResetModel()
#
#         return True
#
#     def resetInternalData(self):
#         """"""
#         #self._data = []
#
#         self._data = [
#             [0.0, 0.1],
#             [0.25, 0.3],
#             [0.50, 0.7],
#             [0.75, 0.5],
#             [1.0, 0.2]
#         ]
#
#
#     @QtCore.Slot(result=bool)
#     def update_chart_data(self):
#
#         self.beginResetModel()
#
#         self._data = [
#             [0.0, 0.1],
#             [0.25, 0.3],
#             [0.50, 0.7],
#             [0.75, 0.5],
#             [1.0, 0.2]
#         ]
#
#         self.endResetModel()
#
#         return True



# class SiteFilter(QSortFilterProxyModel):
#
#     def __init__(self, parent=None):
#         super(SiteFilter, self).__init__(parent)
#         self._row_filter_id = None
#         self._poly = []
#
#         self._pool = QtCore.QThreadPool()
#         self._pool.setMaxThreadCount(1)
#
#         self._progress_text = ''
#
#     def clearFilter(self):
#         """"""
#         self._row_filter_id = None
#         self.invalidateFilter()
#
#     def filterAcceptsRow(self, source_row, source_parent):
#         """"""
#         if self._row_filter_id:
#             if source_row == self._row_filter_id:
#                 return True
#
#         return False
#
#     @QtCore.Slot()
#     def setFilterToLastRow(self):
#         """"""
#         sites = self.sourceModel()._sites
#
#         if sites:
#             last_id = max([site.id for site in sites])
#             self._row_filter_id = last_id
#             self.invalidateFilter()
#
#     @QtCore.Slot(QtPositioning.QGeoCoordinate)
#     def addVertexToPolygon(self, coord):
#         # TODO: firing twice
#
#         idx = self.index(0, 0)
#         poly_role = self.sourceModel().PolyRole
#
#         #xys = self.data(idx, poly_role)  # also works
#         #xys = idx.data(poly_role)
#         #xys.append(coord)
#
#         self._poly.append(coord)
#
#         self.setData(idx, self._poly, poly_role)
#
#     @QtCore.Slot()
#     def removeVertexFromPolygon(self):
#
#         idx = self.index(0, 0)
#         poly_role = self.sourceModel().PolyRole
#
#         #xys = self.data(idx, poly_role)  # also works
#
#         if len(self._poly) > 0:
#             self._poly.pop()
#             self.setData(idx, self._poly, poly_role)
#
#     @QtCore.Slot(bool)
#     def isProcessing(self, value):
#         """"""
#         idx = self.index(0, 0)
#         is_processing_role = self.sourceModel().IsProcessingRole
#         self.setData(idx, value, is_processing_role)
#
#     @QtCore.Slot()
#     def downloadCube(self):
#         """"""
#         worker = workers.NewSiteDownloadsWorker(self._downloadCubeWrapper)
#
#         worker.signals.stac_progress.connect(self._inc_stac_progress)
#         worker.signals.mask_progress.connect(self._inc_mask_progress)
#         worker.signals.band_progress.connect(self._inc_band_progress)
#         worker.signals.progress_text.connect(self._add_progress_text)
#
#         self._pool.start(worker)  # start pool
#
#
#     def _downloadCubeWrapper(
#             self,
#             cb_stac_progress,  # stac progress callback, see worker
#             cb_mask_progress,  # mask progress callback, see worker
#             cb_band_progress,  # band progress callback, see worker
#             cb_progress_text,  # progress text callback, see worker
#     ):
#
#         poly = [(xy.longitude(), xy.latitude()) for xy in self._poly]
#
#         #out_folder = self.output_folder  # FIXME: need to implement
#         out_folder = r'C:\Users\Lewis\Desktop\mon'
#         out_nc = os.path.join(out_folder, 'new_site.nc')
#
#         # check existence of nc
#
#         self.isProcessing(True)
#
#         if len(poly) >= 3:
#             ds = None
#
#             try:
#                 ds = downloader.download_new_site_cube(
#                     in_poly=poly,
#                     out_nc=out_nc,
#                     stac_cb_fn=cb_stac_progress,
#                     mask_cb_fn=cb_mask_progress,
#                     band_cb_fn=cb_band_progress,
#                     progress_text=cb_progress_text
#                 )
#
#                 idx = self.index(0, 0)
#
#                 nc_role = self.sourceModel().NCDatasetRole
#                 ds_role = self.sourceModel().XRDatasetRole
#
#                 self.setData(idx, out_nc, nc_role)
#                 self.setData(idx, ds, ds_role)
#
#                 #self.invalidateFilter()
#
#             except:
#                 #self.isProcessing(False)
#                 assert 'Error during download!!!'
#                 pass
#
#         self.isProcessing(False)
#
#
#     def run_ewmacd(self):  # include callbacks
#
#         # get current selected self values
#         # send to ewmacd func in an algo module
#         # get result from ewmacd
#         # add to self (ds, vectors, etc)
#
#
#
#         idx = self.index(0, 0)
#         #x_role = self.sourceModel().XTestRole
#         #y_role = self.sourceModel().YTestRole
#         #x_role = [0, 1, 2, 3, 4]
#         #y_role = [0.0, 0.25, 0.5, 0.75, 1.0]
#
#         #self.setData(idx, y_role, x_role)
#
#         #import numpy as np
#         #_y = np.random.uniform(low=0.0, high=1.0, size=(5,))
#
#         #self.setData(idx, _y, y_role)
#
#         #self.invalidateFilter()
#
#         #print('cool!')
#
#
#     @QtCore.Slot(QtCharts.QAbstractSeries)
#     def update_chart_data(self, series_raw):
#
#         # re-run ewmacd
#         # get new values
#         # populate series
#         # refresh axes (might do in qml)
#
#         idx = self.index(0, 0)
#         nc_role = self.sourceModel().NCDatasetRole
#
#         # x_role = self.sourceModel().XTestRole
#         # y_role = self.sourceModel().YTestRole
#         # xs = self.data(idx, x_role)
#         # ys = self.data(idx, y_role)
#
#         # TODO: testing
#         nc_file = self.data(idx, nc_role)
#         with xr.open_dataset(nc_file) as ds:
#             ds.load()
#
#         ds['ndvi'] = (ds['nir_1'] - ds['red']) / (ds['nir_1'] + ds['red'])
#         ds = ds[['ndvi']].median(['x', 'y'])
#         ds = ds * 10000
#         #self._ds = ds.copy(deep=True)
#         #ds.close()
#         #ds = None
#
#         #xs, ys = self.run_ewmacd()
#
#         xs = ds['time'].values
#         xs = pd.DatetimeIndex(xs)
#         xs = [QtCore.QDateTime(x) for x in xs]
#
#         ys = ds['ndvi'].values
#
#         series_raw.clear()
#         for x, y in zip(xs, ys):
#             series_raw.append(x.toMSecsSinceEpoch(), y)
#
#         x_axis, y_axis = series_raw.attachedAxes()
#
#         #x_axis.setMin(xs[0])
#         #x_axis.setMax(xs[-1])
#         x_axis.setRange(xs[0], xs[-1])
#
#         y_axis.setMin(min(ys))
#         y_axis.setMax(max(ys))
#
#         years = np.unique(ds['time.year'])[:-1]
#         num_ticks = len(years) * 4
#         x_axis.setTickCount(num_ticks)
#
#     # region PRIVATE
#     def _inc_stac_progress(self, i):
#         idx = self.index(0, 0)
#         stac_progress_role = self.sourceModel().StacProgressRole
#         self.setData(idx, i, stac_progress_role)
#
#     def _inc_mask_progress(self, i):
#         idx = self.index(0, 0)
#         mask_progress_role = self.sourceModel().MaskProgressRole
#         self.setData(idx, i, mask_progress_role)
#
#     def _inc_band_progress(self, i):
#         idx = self.index(0, 0)
#         band_progress_role = self.sourceModel().BandProgressRole
#         self.setData(idx, i, band_progress_role)
#
#     def _add_progress_text(self, txt):
#         self._progress_text += txt + '\n'
#
#         idx = self.index(0, 0)
#         progress_text_role = self.sourceModel().ProgressTextRole
#         self.setData(idx, self._progress_text, progress_text_role)
#     # endregion
