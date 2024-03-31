import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: switchControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsSwitch: switchControl

    MonControls.MonSwitch {
        id: switchControl
    }
}
