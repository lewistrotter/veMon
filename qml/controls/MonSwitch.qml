import QtQuick
import QtQuick.Controls

Switch {
    id: control

    indicator: Rectangle{
        y: parent.height / 2 - height / 2
        implicitWidth: 35
        implicitHeight: 15
        radius: 13
        color: control.checked ? "#306844" : "#acc2b4"
        border.color: "#306844"

        Rectangle {
            x: control.checked ? parent.width - width : 0
            width: 20
            height: 15
            radius: 13
            color: control.pressed ? "#f0f0f0" : "#f6f6f6"
            border.color: "#306844"
        }
    }

    contentItem: Text {
        text: control.text
        font: control.font
        //opacity: enabled ? 1.0 : 0.3
        color: "#FFFFFF"
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}