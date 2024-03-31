
import sys

from PySide6 import QtQml
from PySide6 import QtWidgets
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtPositioning import QGeoCoordinate

from models import core


def main():
    QQuickStyle.setStyle('Fusion')

    app = QtWidgets.QApplication([])

    QtQml.qmlRegisterType(core.NewSite, 'MonObjects', 1, 0, 'NewSite')
    #QtQml.qmlRegisterType(core.NewSite, 'MonObjects', 1, 0, 'NewSite2')

    engine = QtQml.QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.load('qml/containers/Main.qml')

    # could load sites here and use as input to model

    sites_model = core.SitesModel()
    sites_model.load()  # load existing data

    engine.rootContext().setContextProperty('sitesModel', sites_model)

    #new_site_filter = core.SiteFilter()
    #new_site_filter.setSourceModel(sites_model)
    #engine.rootContext().setContextProperty('newSiteFilterModel', new_site_filter)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

