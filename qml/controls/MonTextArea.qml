import QtQuick
import QtQuick.Controls

TextArea {
    id: control
    color: "#306844"

    background: Rectangle {
        id: controlBackground
        implicitWidth: 75
        implicitHeight: 25
        border.width: 0
        color: "#acc2b4"
        opacity: enabled ? 1 : 0.3
        radius: 2
    }
}