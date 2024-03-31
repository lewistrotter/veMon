import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: progressControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsProgressBar: progressBarControl
    property int propsRoundingNum: 0

    MonControls.MonLabel {
        id: headerControl
        anchors {
            left: parent.left
            top: parent.top
        }
        text: "Header"
    }

    MonControls.MonProgressBar {
        id: progressBarControl
        anchors {
            left: parent.left
            right: parent.right
            top: headerControl.bottom
        }
    }

    MonControls.MonLabel {
        anchors {
            right: parent.right
            top: parent.top
        }
        text: qsTr((progressBarControl.value).toFixed(propsRoundingNum)) + qsTr("%")  // rounding
    }
}
