import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: spinBoxControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsSpinbox: spinBoxControl
    //property int roundingNum: 0

    MonControls.MonLabel {
        id: headerControl
        anchors {
            left: parent.left
            top: parent.top
        }
        text: "Header"
    }

    MonControls.MonSpinBox {
        id: spinBoxControl
        anchors {
            left: parent.left
            right: parent.right
            top: headerControl.bottom
            bottom: parent.bottom
        }
    }
}
