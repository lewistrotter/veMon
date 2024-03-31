import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning

import "../controls" as MonControls

Item {
    implicitWidth: 300
    implicitHeight: 300

    property alias mapView: map

    Plugin {
        id: plugin
        name: "osm"
    }

    MapView {
        id: map
        anchors.fill: parent

        map {
            plugin: plugin
            center: QtPositioning.coordinate(-32.05233, 115.757064)
            zoomLevel: 18
            copyrightsVisible: false
        }
    }
}