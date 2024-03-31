import QtQuick
import QtQuick.Controls

Button {
    id: control

    contentItem: Text {
        text: control.text
        font: control.font
        color: control.down ? "#BDBDBD" : "#FFFFFF"
        opacity: enabled ? 1.0 : 0.3
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        id: controlBackground
        implicitWidth: 75
        implicitHeight: 25
        border.width: 0
        color: control.down ? "#2B5D3D" : (control.hovered ? "#447756" : "#306844")
        opacity: enabled ? 1 : 0.3
        radius: 3
    }

    HoverHandler {
        id: mouse
        acceptedDevices: PointerDevice.Mouse
        cursorShape: Qt.PointingHandCursor
    }
}