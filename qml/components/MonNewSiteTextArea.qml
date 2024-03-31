import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: textAreaControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsTextArea: textAreaControl

    MonControls.MonLabel {
        id: headerControl
        anchors {
            left: parent.left
            top: parent.top
        }
        text: "Header"
    }

    MonControls.MonTextArea {
        id: textAreaControl
        anchors {
            left: parent.left
            right: parent.right
            top: headerControl.bottom
            bottom: parent.bottom
        }
    }
}
