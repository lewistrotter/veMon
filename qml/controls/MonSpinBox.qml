import QtQuick
import QtQuick.Controls

SpinBox {
    id: control
    editable: true

    property int decimals: 2
    property real realValue: value / 100

    validator: DoubleValidator {
        bottom: Math.min(control.from, control.to)
        top:  Math.max(control.from, control.to)
    }

    textFromValue: function(value, locale) {
        return Number(value / 100).toLocaleString(locale, 'f', control.decimals)
    }

    valueFromText: function(text, locale) {
        return Number.fromLocaleString(locale, text) * 100
    }

    contentItem: TextInput {
        id: controlTextInput
        anchors {
            top: parent.top
            bottom: parent.bottom
            left: parent.left
            right: controlUpIndicator.left
            leftMargin: 5
            rightMargin: 5
        }

        horizontalAlignment: Qt.AlignLeft
        verticalAlignment: Qt.AlignVCenter

        text: control.textFromValue(control.value, control.locale)
        color: "#306844"

        readOnly: !control.editable
        validator: control.validator
        inputMethodHints: Qt.ImhFormattedNumbersOnly
    }

    down.indicator: Rectangle {
        id: controlDownIndicator
        //x: control.mirrored ? 0 : parent.width - width - controlUpIndicator.width
        anchors {
            top: parent.top
            bottom: parent.bottom
            right: parent.right
            topMargin: 2
            bottomMargin: 2
            rightMargin: 2
        }
        width: height
        radius: 2
        color: control.up.pressed ? "#f0f0f0" : "#f6f6f6"
        border.color: enabled ? "#306844" : "pink"

        Text {
            text: "-"
            font.pixelSize: control.font.pixelSize * 2
            color: "#306844"
            anchors.fill: parent
            fontSizeMode: Text.Fit
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    up.indicator: Rectangle {
        id: controlUpIndicator
        //x: control.mirrored ? 0 : parent.width - width
        anchors {
            top: parent.top
            bottom: parent.bottom
            right: controlDownIndicator.left
            topMargin: 2
            bottomMargin: 2
            rightMargin: 2
        }
        width: height
        radius: 2
        color: control.up.pressed ? "#f0f0f0" : "#f6f6f6"
        border.color: enabled ? "#306844" : "pink"

        Text {
            text: "+"
            font.pixelSize: control.font.pixelSize * 2
            color: "#306844"
            anchors.fill: parent
            fontSizeMode: Text.Fit
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }


    background: Rectangle {
        color: "#acc2b4"
        radius:2
    }


}

