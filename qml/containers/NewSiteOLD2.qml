import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning
import QtCharts

import "../controls" as MonControls
import "../components" as MonComponents

Rectangle {
    //title: "Calibration Wizard"
    //width: 1200
    //height: 800
    //minimumWidth: 960
    //minimumHeight: 640
    //visible: true
    color: "pink"

    ColumnLayout {
        anchors.fill: parent

        // main stack and components
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // root stack view
            StackView {
                id: stkRootStackView
                anchors.fill: parent
                initialItem: cmpCalibrateOverview // cmpCalibrateMap
                pushEnter: Transition  {}
                pushExit: Transition  {}
                popEnter: Transition  {}
                popExit: Transition  {}
            }

            // stack component - map
            Component {
                id: cmpCalibrateMap

                // main and nav button containers
                ColumnLayout {

                    // container - top map
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        Plugin {
                            id: mapPlugin
                            name: "osm"
                        }

                        // TODO: perhaps move poly to a model on backend
                        Map {
                            id: map
                            anchors.fill: parent
                            center: QtPositioning.coordinate(-32.052338, 115.757024)
                            zoomLevel: 18
                            plugin: mapPlugin
                            copyrightsVisible: false

                            DragHandler {
                                onTranslationChanged: (delta) => map.pan(-delta.x, -delta.y)
                            }

                            WheelHandler {
                                rotationScale: 1/120
                                property: "zoomLevel"
                            }

                            MapPolygon {
                                id: poly
                                border {
                                    width: 2
                                    color: "#fbff00"
                                }
                                color: "#1Afbff00"
                                antialiasing: true
                                layer {
                                    enabled: true
                                    samples: 2
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (mouse.button == Qt.LeftButton) {
                                        var point = Qt.point(mouseX, mouseY)
                                        var coord = map.toCoordinate(point)
                                        poly.addCoordinate(coord)
                                        calibModel.append_poly_vertex(coord)
                                    }
                                }
                            }

                            Button {
                                id: btnResetPolygon
                                anchors {
                                    top: parent.top
                                    left: parent.left
                                    topMargin: 5
                                    leftMargin: 5
                                }
                                text: "Reset"
                                onClicked: {
                                    poly.path = [];
                                    calibModel.reset_poly_vertices()
                                }
                            }
                        }
                    }

                    // container - bottom nav buttons
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 60

                        // next button
                        Button {
                            id: btnNextToDownload
                            width: 75
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Next"
                            onClicked: {
                                stkRootStackView.push(cmpCalibrateDownload)
                            }
                        }
                    }
                }
            }

            // stack component - download
            Component {
                id: cmpCalibrateDownload

                // main and nav button containers
                ColumnLayout {

                    // container - top
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ColumnLayout {
                            id: conDownloads
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            spacing: 30

                            ColumnLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 5

                                Label {
                                    text: "DEA STAC Query Progress"
                                }

                                RowLayout {
                                    ProgressBar {
                                        id: prgStacQuery
                                        Layout.preferredWidth: conDownloads.width * 0.5
                                        Layout.preferredHeight: 15
                                        indeterminate: calibModel.stac_is_indeterminate
                                        enabled: calibModel.is_processing
                                        from: 0
                                        to: 100
                                        value: (calibModel.stac_query_progress).toFixed(0)
                                    }

                                    Label {
                                        Layout.preferredWidth: 25
                                        Layout.leftMargin: 10
                                        text: prgStacQuery.value
                                        opacity: 0
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 5

                                Label {
                                    text: "DEA Sentinel-2 Mask Download and Validation"
                                }

                                RowLayout {
                                    ProgressBar {
                                        id: prgMaskDownload
                                        Layout.preferredWidth: conDownloads.width * 0.5
                                        Layout.preferredHeight: 15
                                        indeterminate: false
                                        enabled: calibModel.is_processing
                                        from: 0
                                        to: 100
                                        value: (calibModel.cube_mask_progress).toFixed(0)
                                    }

                                    Label {
                                        Layout.preferredWidth: 25
                                        Layout.leftMargin: 10
                                        text: prgMaskDownload.value
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 5

                                Label {
                                    text: "DEA Sentinel-2 Satellite Download"
                                }

                                RowLayout {
                                    ProgressBar {
                                        id: prgSatDownload
                                        Layout.preferredWidth: conDownloads.width * 0.5
                                        Layout.preferredHeight: 15
                                        indeterminate: false
                                        enabled: calibModel.is_processing
                                        from: 0
                                        to: 100
                                        value: (calibModel.cube_band_progress).toFixed(0)
                                    }

                                    Label {
                                        Layout.preferredWidth: 25
                                        Layout.leftMargin: 10
                                        text: prgSatDownload.value
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 5

                                Label {
                                    text: "Process Status"
                                }

                                RowLayout {
                                    ScrollView {
                                        Layout.preferredWidth: (conDownloads.width * 0.5) + 35 // lbl + space
                                        Layout.preferredHeight: conDownloads.height * 0.5
                                        background: Rectangle {color: "white"}

                                        TextArea {
                                            id: txtProcessStatus
                                            hoverEnabled: false
                                            text: calibModel.progress_text
                                        }
                                    }
                                }
                            }

                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: conDownloads.width * 0.5

                                // start button
                                Button {
                                    id: btnStartDownloads
                                    width: 75
                                    anchors.right: parent.right
                                    anchors.rightMargin: 0
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: "Start"
                                    enabled: !calibModel.is_processing
                                    onClicked: {
                                        calibModel.run_dea_downloader()
                                    }
                                }

                                // cancel button
                                Button {
                                    id: btnCancelDownloads
                                    width: 75
                                    anchors.right: btnStartDownloads.left
                                    anchors.rightMargin: 10
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: "Cancel"
                                    enabled: calibModel.is_processing
                                    onClicked: {
                                        //stkRootStackView.push(cmpCalibrateOverview)
                                    }
                                }
                            }
                        }
                    }

                    // container - bottom nav buttons
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 60

                        // next button
                        Button {
                            id: btnNextToOverview
                            width: 75
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Next"
                            enabled: !calibModel.is_processing
                            onClicked: {
                                stkRootStackView.push(cmpCalibrateOverview)
                            }
                        }

                        // back button
                        Button {
                            id: btnBackToMap
                            width: 75
                            anchors.right: btnNextToOverview.left
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Back"
                            enabled: !calibModel.is_processing
                            onClicked: {
                                stkRootStackView.pop()
                            }
                        }
                    }
                }
            }

            // stack component - overview
            Component {
                id: cmpCalibrateOverview

                // main and nav button containers
                ColumnLayout {

                    // left and right containers
                    RowLayout {

                        // container - left
                        Rectangle {
                            Layout.preferredWidth: 200
                            Layout.fillHeight: true
                            color: "#464646"

                            // left container - controls
                            ColumnLayout {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.leftMargin: 5
                                anchors.rightMargin: 5
                                anchors.topMargin: 5
                                spacing: 15

                                // control - training start
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Training Start Year"
                                    slider.from: 2016
                                    slider.to: 2024
                                    slider.stepSize: 1
                                    slider.value: calibModel.train_start
                                    slider.onMoved: {
                                        calibModel.train_start = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - training end
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Training End Year"
                                    slider.from: 2016
                                    slider.to: 2024
                                    slider.stepSize: 1
                                    slider.value: calibModel.train_end
                                    slider.onMoved: {
                                        calibModel.train_end = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - testing end
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Testing End Year"
                                    slider.from: 2016
                                    slider.to: 2024
                                    slider.stepSize: 1
                                    slider.value: calibModel.test_end
                                    slider.onMoved: {
                                        calibModel.test_end = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - num harmonics
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Num. of Harmonics"
                                    slider.from: 1
                                    slider.to: 5
                                    slider.stepSize: 1
                                    slider.value: calibModel.num_harmonics
                                    slider.onMoved: {
                                        calibModel.num_harmonics = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - xbar limit 1
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "X-Bar Limit 1"
                                    slider.from: 0.5
                                    slider.to: 15.0
                                    slider.stepSize: 0.5
                                    slider.value: calibModel.xbar_limit_1
                                    roundingNum: 1
                                    slider.onMoved: {
                                        calibModel.xbar_limit_1 = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - xbar limit 2
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "X-Bar Limit 2"
                                    slider.from: 1
                                    slider.to: 30
                                    slider.stepSize: 1
                                    slider.value: calibModel.xbar_limit_2
                                    slider.onMoved: {
                                        calibModel.xbar_limit_2 = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - lambda value
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Lambda"
                                    slider.from: 0.1
                                    slider.to: 1.0
                                    slider.stepSize: 0.1
                                    slider.value: calibModel.lambda_value
                                    roundingNum: 1
                                    slider.onMoved: {
                                        calibModel.lambda_value = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - lambda stdvs
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Lambda Std. Devs."
                                    slider.from: 1
                                    slider.to: 25
                                    slider.stepSize: 1
                                    slider.value: calibModel.lambda_stdvs
                                    slider.onMoved: {
                                        calibModel.lambda_stdvs = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - low thresh
                                ColumnLayout {
                                    spacing: 5

                                    Label {
                                        Layout.fillWidth: true
                                        text: "Lower Threshold"
                                    }

                                    TextField {
                                        Layout.preferredWidth: 140
                                        text: calibModel.low_thresh
                                        validator: DoubleValidator {
                                            bottom: -10000
                                            top: 10000
                                        }
                                        onTextChanged: {
                                            calibModel.low_thresh = text
                                            calibModel.run_ewmacd()
                                            calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                        }
                                    }
                                }

                                // control - persistence
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    header.text: "Persistence"
                                    slider.from: 1
                                    slider.to: 30
                                    slider.stepSize: 1
                                    slider.value: calibModel.persistence
                                    slider.onMoved: {
                                        calibModel.persistence = slider.value
                                        calibModel.run_ewmacd()
                                        calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                    }
                                }

                                // control - rounding
                                ColumnLayout {
                                    spacing: 5

                                    CheckBox {
                                        Layout.fillWidth: true
                                        Layout.preferredWidth: 140
                                        topPadding: 0
                                        leftPadding: 0
                                        text: "Rounding"
                                        checked: calibModel.rounding
                                        onToggled: {
                                            calibModel.rounding = checked
                                            calibModel.run_ewmacd()
                                            calibModel.refresh_charts(srsRaw, srsHrm, srsChg)
                                        }
                                    }
                                }
                            }
                        }

                        // container - right
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            // right container - charts
                            ColumnLayout {
                                anchors.fill: parent

                                // chart container - top
                                Item {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    // chart top - veg (raw and harmonic)
                                    ChartView {
                                        id: chtRaw
                                        title: "Vegetation (Raw and Harmonic)"
                                        anchors.fill: parent
                                        anchors.margins: -8  // removes padding
                                        antialiasing: false
                                        backgroundRoundness: 0
                                        legend {visible: false}

                                        DateTimeAxis {
                                            id: axsTopX
                                            format: "yy-MM"
                                            labelsAngle: -90
                                        }

                                        ValueAxis {
                                            id: axsTopY
                                            //labelFormat: "%4.2f"

                                        }

                                        LineSeries {
                                            id: srsRaw
                                            name: "Vegetation Index"
                                            color: "darkgrey"
                                            axisX: axsTopX
                                            axisY: axsTopY
                                            pointsVisible: true
                                        }

                                        LineSeries {
                                            id: srsHrm
                                            name: "Harmonic"
                                            color: "green"
                                            axisX: axsTopX
                                            axisY: axsTopY
                                            pointsVisible: true
                                        }
                                    }
                                }

                                // chart container - bottom
                                Item {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    // chart bottom - veg change
                                    ChartView {
                                        id: chtChg
                                        title: "Change Deviations"
                                        anchors.fill: parent
                                        anchors.margins: -8  // removes padding
                                        antialiasing: false
                                        backgroundRoundness: 0
                                        legend {visible: false}
                                        plotAreaColor: "pink"

                                        DateTimeAxis {
                                            id: axsBottomX
                                            format: "yy-MM"
                                            labelsAngle: -90
                                        }

                                        ValueAxis {
                                            id: axsBottomY
                                            //labelFormat: "%09.2f"
                                            tickType: ValueAxis.TicksDynamic
                                            tickInterval: 2  // 1
                                            tickAnchor: 0
                                        }

                                        LineSeries {
                                            id: srsChg
                                            name: "Change"
                                            color: "red"
                                            axisX: axsBottomX
                                            axisY: axsBottomY
                                            pointsVisible: true
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // container - bottom nav buttons
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 60
                        color: "#464646"

                        // next button
                        MonControls.MonButton {
                            id: btnNextToOverview
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Next"
                            onClicked: {
                                stkRootStackView.push(cmpCalibrateDownload)
                            }
                        }

                        // back button
                        MonControls.MonButton {
                            id: btnBackToDownload
                            anchors.right: btnNextToOverview.left
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Back"
                            onClicked: {
                                stkRootStackView.pop()
                            }
                        }
                    }
                }
            }
        }
    }
}