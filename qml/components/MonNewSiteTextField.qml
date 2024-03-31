import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: propsTextField.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsTextField: textFieldControl

    MonControls.MonLabel {
        id: headerControl
        anchors {
            left: parent.left
            top: parent.top
        }
        text: "Header"
    }

    MonControls.MonTextField {
        id: textFieldControl
        anchors {
            left: parent.left
            right: parent.right
            top: headerControl.bottom
            bottom: parent.bottom
        }
    }
}
