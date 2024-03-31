import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning

import "../controls" as MonControls
import "../components" as MonComponents

ApplicationWindow {
    id: rootContainer
    width: 1200
    height: 800
    minimumWidth: 960
    minimumHeight: 640
    title: "veMon"
    color: "#1E1F22"
    visible: true

    StackView {
        id: rootStack
        anchors.fill: parent
        initialItem: rootView
    }

    Component {
        id: rootView

        GridLayout {
            id: rootGrid
            anchors.fill: parent
            rows: 2
            columns: 2

            // top bar
            Rectangle {
                id: rootTopBar
                Layout.row: 0
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                Layout.columnSpan: 2
                color: "#2B2D30"

                RowLayout {
                    anchors.fill: parent

                    // top bar left side
                    Rectangle {
                        id: rootTopBarLeft
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "orange"

                        Button {
                            id: rootButtonNew
                            Layout.preferredWidth: 25
                            anchors.verticalCenter: parent.verticalCenter
                            text: "New"
                            onClicked: {
                                rootStack.push("NewSite.qml")
                            }
                        }
                    }

                    // top bar center
                    Rectangle {
                        id: rootTopBarCenter
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "green"

                        Button {
                            id: rootButtonMapDisplay
                            Layout.preferredWidth: 25
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Map"
                            onClicked: {centerStackLayout.currentIndex = 1}
                        }
                    }

                    // top bar right side
                    Rectangle {
                        id: rootTopBarRight
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "yellow"

                        Button {
                            id: rootButtonClose
                            Layout.preferredWidth: 25
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Close"
                            onClicked: {}
                        }
                    }
                }
            }

            // side bar
            Rectangle {
                id: rootSideBar
                Layout.row: 1
                Layout.column: 0
                Layout.preferredWidth: 200
                Layout.fillHeight: true
                color: "#2B2D30"

                ListView {
                    id: rootListView
                    anchors.fill: parent
                    spacing: 5
                    interactive: false
                    clip: true
                    model: sitesModel
                    delegate: siteDelegate
                }

                Component {
                    id: siteDelegate

                    Rectangle {
                        width: parent.width
                        height: 50
                        color: "#306844"

                        // site code
                        Text {
                            anchors {
                                top: parent.top
                                left: parent.left
                                topMargin: 2
                                leftMargin: 2
                            }
                            font.pointSize: 10
                            font.bold: true
                            color: "white"
                            elide: Text.ElideRight
                            text: code
                        }

                        // site zoom button
                        RoundButton {
                            id: siteZoomButton
                            width: 20
                            height: 20
                            anchors {
                                bottom: parent.bottom
                                right: parent.right
                                bottomMargin: 2
                                rightMargin: 2
                            }
                            text: "✜"
                            onClicked: sitesModel.zoomToClickedSiteItem(poly, centerMap.mapView.map)
                        }

                        // site remove button
                        RoundButton {
                            id: siteRemoveButton
                            width: 20
                            height: 20
                            anchors {
                                bottom: parent.bottom
                                right: siteZoomButton.left
                                bottomMargin: 2
                                rightMargin: 2
                            }
                            text: "🗑"
                            onClicked: sitesModel.remove(index)
                        }
                    }
                }
            }

            // center
            Rectangle {
                id: rootCenter
                Layout.row: 1
                Layout.column: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                //color: "red"

                StackLayout {
                    id: centerStackLayout
                    anchors.fill: parent
                    currentIndex: 0

                    Rectangle {
                        anchors.fill: parent

                        MonComponents.MonRootMap {
                            id: centerMap
                            anchors.fill: parent
                            mapView.map {
                                data: polyViewModel
                            }

                            MapItemView {
                                id: polyViewModel
                                model: sitesModel
                                delegate: MonComponents.MonRootPolygon {
                                    path: poly
                                }
                            }
                        }
                    }

                    Rectangle {color: 'teal'}
                    Rectangle {color: 'plum'}
                }
            }
        }
    }
}