import QtQuick
import QtQuick.Controls

import "../controls" as MonControls

Rectangle {
    implicitWidth: sliderControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsSlider: sliderControl
    property int propsRoundingNum: 0

    MonControls.MonLabel {
        id: headerControl
        anchors {
            left: parent.left
            top: parent.top
        }
        text: "Header"
    }

    MonControls.MonSlider {
        id: sliderControl
        anchors {
            left: parent.left
            right: parent.right
            top: headerControl.bottom
            bottom: parent.bottom
        }
        snapMode: Slider.SnapAlways

    }

    MonControls.MonLabel {
        anchors {
            right: parent.right
            top: parent.top
        }
        text: (sliderControl.value).toFixed(propsRoundingNum)  // rounding
    }
}
