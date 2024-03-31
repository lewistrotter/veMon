import QtQuick
import QtQuick.Controls

ProgressBar {
    id: control

    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 3
        color: "#acc2b4"
        radius: 2
    }

    contentItem: Item {
        implicitWidth: 200
        implicitHeight: 3

        // Progress indicator for determinate state.
        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            radius: 2
            color: "#306844"
            visible: !control.indeterminate
        }

        // Scrolling animation for indeterminate state.
        Item {
            anchors.fill: parent
            visible: control.indeterminate
            clip: true

            Row {
                spacing: 20

                Repeater {
                    model: control.width / 40 + 1

                    Rectangle {
                        color: "#306844"
                        width: 20
                        height: control.height
                    }
                }
                XAnimator on x {
                    from: 0
                    to: -40
                    loops: Animation.Infinite
                    running: control.indeterminate
                }
            }
        }
    }
}