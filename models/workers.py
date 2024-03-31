
import sys
import traceback

from PySide6 import QtCore


class NewSiteDownloadWorker(QtCore.QRunnable):

    def __init__(self, fn):
        super(NewSiteDownloadWorker, self).__init__()
        self.fn = fn
        self.stac_cb_fn = None
        self.mask_cb_fn = None
        self.band_cb_fn = None
        self.text_cb_fn = None

    @QtCore.Slot()
    def run(self):
        try:
            self.fn(
                stac_cb_fn=self.stac_cb_fn,
                mask_cb_fn=self.mask_cb_fn,
                band_cb_fn=self.band_cb_fn,
                text_cb_fn=self.text_cb_fn
            )

        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.text_cb_fn((exctype, value, traceback.format_exc()))

class EwmacdChartsWorker(QtCore.QRunnable):

    def __init__(self, fn):
        super(EwmacdChartsWorker, self).__init__()
        self.fn = fn

    @QtCore.Slot()
    def run(self):
        try:
            self.fn()

        except:
            #traceback.print_exc()
            #exctype, value = sys.exc_info()[:2]
            #self.text_cb_fn((exctype, value, traceback.format_exc()))
            raise  # TODO: implement error handler