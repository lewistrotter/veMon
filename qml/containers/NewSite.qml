import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning
import QtCharts

import "../controls" as MonControls
import "../components" as MonComponents

import MonObjects

Item {
    implicitWidth: 300
    implicitHeight: 300

    NewSite {
        id: newSite
    }

    GridLayout {
        anchors.fill: parent
        rows: 2

        // center
        Rectangle {
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1E1F22"

            StackLayout {
                id: newSiteCenterStackLayout
                anchors.fill: parent

                // intro container
                Rectangle {
                    color: 'teal'
                }

                // map container
                Rectangle {
                    color: 'plum'

                    GridLayout {
                        anchors.fill: parent
                        rows: 1
                        columns: 2

                        // sidebar
                        Rectangle {
                            id: mapSideBar
                            Layout.row: 0
                            Layout.column: 0
                            Layout.preferredWidth: 200
                            Layout.fillHeight: true
                            color: "#2B2D30"

                            ColumnLayout {
                                anchors {
                                    left: parent.left
                                    right: parent.right
                                    top: parent.top
                                    leftMargin: 5
                                    rightMargin: 5
                                    topMargin: 5
                                }
                                spacing: 10

                                // control - project
                                MonComponents.MonNewSiteTextField {
                                    //id: projectTextField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Project Name"
                                    propsTextField.text: "YAN1"  //TODO: testing
                                    propsTextField.onTextEdited: {
                                        newSite.project = propsTextField.text

                                    }
                                }

                                // control - code
                                MonComponents.MonNewSiteTextField {
                                    //id: codeTextField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Site Code"
                                    propsTextField.text: "A001" //TODO: testing
                                    propsTextField.onTextEdited: {
                                        newSite.code = propsTextField.text
                                    }
                                }

                                // control - out folder
                                MonComponents.MonNewSiteFolderDialog {
                                    //id: outFolderDialog
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Output Folder"
                                    propsTextField.text: "C:\\Users\\Lewis\\Desktop\\mon" // TODO: testing
                                    propsTextField.onContentSizeChanged: {
                                        newSite.out_folder = propsTextField.text
                                    }
                                }

                                // control - progress bar for stac downloads
                                MonComponents.MonNewSiteProgressBar {
                                    //id: stacProgressBar
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 25
                                    propsHeader.text: "STAC Query Progress"
                                    propsProgressBar.from: 0
                                    propsProgressBar.to: 100
                                    propsProgressBar.value: newSite.stac_progress
                                    propsProgressBar.enabled: newSite.is_processing
                                    //propsProgressBar.indeterminate: (propsProgressBar.value == 0 | propsProgressBar.value == 100) ? false : true
                                }

                                // control - progress bar for mask downloads
                                MonComponents.MonNewSiteProgressBar {
                                    //id: maskProgressBar
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 25
                                    propsHeader.text: "Validation Progress"
                                    propsProgressBar.from: 0
                                    propsProgressBar.to: 100
                                    propsProgressBar.value: newSite.mask_progress
                                    propsProgressBar.enabled: newSite.is_processing
                                }

                                // control - progress bar for band downloads
                                MonComponents.MonNewSiteProgressBar {
                                    //id: bandProgressBar
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 25
                                    propsHeader.text: "Download Progress"
                                    propsProgressBar.from: 0
                                    propsProgressBar.to: 100
                                    propsProgressBar.value: newSite.band_progress
                                    propsProgressBar.enabled: newSite.is_processing
                                }

                                // control - start download
                                MonControls.MonButton {
                                    //id: startDownloadButton
                                    Layout.fillWidth: true
                                    text: "Start Download"
                                    enabled: !newSite.is_processing
                                    onClicked: {
                                        newSite.downloadCube()
                                        //newSite.downloadCubeTesting()
                                        newSite.runEwmacd()
                                    }
                                }

                                // control - cancel download
                                MonControls.MonButton {
                                    //id: cancelDownloadButton
                                    Layout.fillWidth: true
                                    text: "Cancel Download"
                                    enabled: newSite.is_processing
                                    onClicked: {}
                                }

                                // control - progress text
                                MonComponents.MonNewSiteTextArea {
                                    //id: textProgress
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 400
                                    propsHeader.text: "Progress Status"
                                    propsTextArea.text: newSite.progress_text
                                    enabled: newSite.is_processing
                                }
                            }
                        }

                        // center window
                        Rectangle {
                            id: mapViewCenterWindow
                            Layout.row: 0
                            Layout.column: 1
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "grey"

                            // control - new site map
                            MonComponents.MonNewSiteMap {
                                id: newSiteMap
                                anchors.fill: parent
                                mapView.map {
                                    data: newSitePolyModelView
                                }

                                // map interactivity - add/remove coordinates on click
                                MouseArea {
                                    anchors.fill: parent
                                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                                    onClicked: {
                                        if (mouse.button == Qt.LeftButton) {
                                            var point = Qt.point(mouseX, mouseY)
                                            var coordinate = newSiteMap.mapView.map.toCoordinate(point)
                                            newSite.appendCoordinateToPolygon(coordinate)
                                        }
                                        else if (mouse.button == Qt.RightButton) {
                                            newSite.removeCoordinateFromPolygon()
                                        }
                                    }
                                }

                                // map polygon model
                                MapItemView {
                                    id: newSitePolyModelView
                                    model: newSite
                                    delegate: MonComponents.MonNewSitePolygon {
                                        path: polygon
                                    }
                                }
                            }
                        }
                    }
                }

                // calibrate container
                Rectangle {
                    color: 'aqua'

                    GridLayout {
                        anchors.fill: parent
                        rows: 1
                        columns: 2

                        // sidebar
                        Rectangle {
                            id: calibrateSideBar
                            Layout.row: 0
                            Layout.column: 0
                            Layout.preferredWidth: 200
                            Layout.fillHeight: true
                            color: "#2B2D30"

                            ColumnLayout {
                                anchors {
                                    left: parent.left
                                    right: parent.right
                                    top: parent.top
                                    leftMargin: 5
                                    rightMargin: 5
                                    topMargin: 5
                                }
                                spacing: 10

                                // control - training start
                                MonComponents.MonNewSiteSlider {
                                    id: trainStartSlider
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Training Start Year"
                                    propsSlider.from: 2016
                                    propsSlider.to: 2024
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.train_start
                                    propsSlider.onMoved: {
                                        // ensure train start lower than train end
                                        if (propsSlider.value >= trainEndSlider.propsSlider.value) {
                                            propsSlider.value = trainEndSlider.propsSlider.value - 1
                                        }

                                        // only refresh qml value != backend
                                        if (propsSlider.value !== newSite.train_start) {
                                            newSite.train_start = propsSlider.value
                                            newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                        }
                                    }
                                }

                                // control - training end
                                MonComponents.MonNewSiteSlider {
                                    id: trainEndSlider
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Training End Year"
                                    propsSlider.from: 2016
                                    propsSlider.to: 2024
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.train_end
                                    propsSlider.onMoved: {
                                        // ensure train end greater train start
                                        if (propsSlider.value <= trainStartSlider.propsSlider.value) {
                                            propsSlider.value = trainStartSlider.propsSlider.value + 1
                                        }

                                        // ensure train end lower test end
                                        if (propsSlider.value >= testEndSlider.propsSlider.value) {
                                            propsSlider.value = testEndSlider.propsSlider.value - 1
                                        }

                                        // only refresh qml value != backend
                                        if (propsSlider.value !== newSite.train_end) {
                                            newSite.train_end = propsSlider.value
                                            newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                        }
                                    }
                                }

                                // control - testing end
                                MonComponents.MonNewSiteSlider {
                                    id: testEndSlider
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Testing End Year"
                                    propsSlider.from: 2016
                                    propsSlider.to: 2024
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.test_end
                                    propsSlider.onMoved: {
                                        // ensure test end higher than train end
                                        if (propsSlider.value <= trainEndSlider.propsSlider.value) {
                                            propsSlider.value = trainEndSlider.propsSlider.value + 1
                                        }

                                        // only refresh qml value != backend
                                        if (propsSlider.value !== newSite.test_end) {
                                            newSite.test_end = propsSlider.value
                                            newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                        }
                                    }
                                }

                                // control - num harmonics
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Num. of Harmonics"
                                    propsSlider.from: 1
                                    propsSlider.to: 5
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.num_harmonics
                                    propsSlider.onMoved: {
                                        newSite.num_harmonics = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - xbar limit 1
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "X-Bar Limit 1"
                                    propsSlider.from: 0.5
                                    propsSlider.to: 15.0
                                    propsSlider.stepSize: 0.5
                                    propsSlider.value: newSite.xbar_limit_1
                                    propsRoundingNum: 1
                                    propsSlider.onMoved: {
                                        newSite.xbar_limit_1 = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - xbar limit 2
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "X-Bar Limit 2"
                                    propsSlider.from: 1
                                    propsSlider.to: 30
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.xbar_limit_2
                                    propsSlider.onMoved: {
                                        newSite.xbar_limit_2 = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - lambda value
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Lambda"
                                    propsSlider.from: 0.1
                                    propsSlider.to: 1.0
                                    propsSlider.stepSize: 0.1
                                    propsSlider.value: newSite.lambda_value
                                    propsRoundingNum: 1
                                    propsSlider.onMoved: {
                                        newSite.lambda_value = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - lambda stdvs
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Lambda Std. Devs."
                                    propsSlider.from: 1
                                    propsSlider.to: 25
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.lambda_stdvs
                                    propsSlider.onMoved: {
                                        newSite.lambda_stdvs = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - lower threshold
                                MonComponents.MonNewSiteSpinBox {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Lower Threshold"
                                    propsSpinbox.from: -10000
                                    propsSpinbox.to: 10000
                                    propsSpinbox.stepSize: 10
                                    propsSpinbox.value: newSite.low_thresh
                                    propsSpinbox.onValueModified: {
                                        newSite.low_thresh = propsSpinbox.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - persistence
                                MonComponents.MonNewSiteSlider {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsHeader.text: "Persistence"
                                    propsSlider.from: 1
                                    propsSlider.to: 30
                                    propsSlider.stepSize: 1
                                    propsSlider.value: newSite.persistence
                                    propsSlider.onMoved: {
                                        newSite.persistence = propsSlider.value
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }

                                // control - rounding
                                MonComponents.MonNewSiteSwitch {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    propsSwitch.text: "Rounding"
                                    propsSwitch.checked: newSite.rounding
                                    propsSwitch.onToggled: {
                                        newSite.rounding = propsSwitch.checked
                                        newSite.refreshCharts(seriesVege, seriesHarm, seriesChng)
                                    }
                                }
                            }
                        }

                        // center window
                        Rectangle {
                            id: calibrateCenterWindow
                            Layout.row: 0
                            Layout.column: 1
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "orange"

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 0

                                // chart - top
                                ChartView {
                                    id: chartTop
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    anchors.margins: -7  // removes padding
                                    backgroundRoundness: 0
                                    backgroundColor: "#2B2D30"
                                    legend {visible: false}

                                    DateTimeAxis {
                                        id: axisTopX
                                        format: "yy-MM"
                                        labelsAngle: -90
                                        labelsColor: "#FFFFFF"
                                        gridLineColor: "#acc2b4D9"
                                    }

                                    ValueAxis {
                                        id: axisTopY
                                        labelsColor: "#FFFFFF"
                                        gridLineColor: "#acc2b4D9"
                                    }

                                    LineSeries {
                                        id: seriesVege
                                        axisX: axisTopX
                                        axisY: axisTopY
                                        pointsVisible: true
                                        width: 1.5
                                        color: "#808080"
                                    }

                                    LineSeries {
                                        id: seriesHarm
                                        axisX: axisTopX
                                        axisY: axisTopY
                                        pointsVisible: true
                                        width: 1.5
                                        color: "#48d71d"
                                    }
                                }

                                // chart - bottom
                                ChartView {
                                    id: chartBottom
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    anchors.margins: -7  // removes padding
                                    backgroundRoundness: 0
                                    backgroundColor: "#2B2D30"
                                    legend {visible: false}

                                    DateTimeAxis {
                                        id: axisBottomX
                                        format: "yy-MM"
                                        labelsAngle: -90
                                        labelsColor: "#FFFFFF"
                                        gridLineColor: "#acc2b4D9"
                                    }

                                    ValueAxis {
                                        id: axisBottomY
                                        labelsColor: "#FFFFFF"
                                        gridLineColor: "#acc2b4D9"
                                    }

                                    LineSeries {
                                        id: seriesChng
                                        axisX: axisBottomX
                                        axisY: axisBottomY
                                        pointsVisible: true
                                        color: "#E01919"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // bottom bar
        Rectangle {
            id: bottomBar
            Layout.row: 1
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            anchors.bottom: parent.bottom
            color: "#2B2D30"

            // control - next button
            MonControls.MonButton {
                id: newSiteButtonNext
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                text: newSiteCenterStackLayout.currentIndex < 2 ? "Next" : "Finish"
                enabled: !newSite.is_processing
                onClicked: {
                    newSiteCenterStackLayout.currentIndex += 1

                    if (newSiteCenterStackLayout.currentIndex == 3) {
                        sitesModel.ingestNewSite(newSite)  // insert into list model
                        rootStack.pop()  // back to main view
                    }
                }
            }

            // control - back button
            MonControls.MonButton {
                id: newSiteButtonBack
                anchors.right: newSiteButtonNext.left
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                text: "Back"
                visible: newSiteCenterStackLayout.currentIndex > 0 ? true : false
                enabled: !newSite.is_processing
                onClicked: {
                    newSiteCenterStackLayout.currentIndex -= 1
                }
            }
        }
    }
}