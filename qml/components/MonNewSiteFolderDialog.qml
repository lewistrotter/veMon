import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs

import "../controls" as MonControls

Rectangle {
    implicitWidth: sliderControl.Width
    implicitHeight: 40
    color: "transparent"

    property alias propsHeader: headerControl
    property alias propsTextField: textFieldControl
    property alias propsButton: buttonControl
    property alias propsFolderDialog: dialogControl

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
            right: buttonControl.left
            top: headerControl.bottom
            bottom: parent.bottom
            rightMargin: 5
        }
    }

    MonControls.MonButton {
        id: buttonControl
        implicitWidth: 30
        anchors {
            right: parent.right
            top: headerControl.bottom
            bottom: parent.bottom
        }
        text: "📁"
        onClicked: {
            dialogControl.open()
        }
    }

    FolderDialog {
        id: dialogControl

        onAccepted: {
            // remove file:/// from start of url
            // TODO: maybe make this pyside
            var path = dialogControl.currentFolder.toString();
            path= path.replace(/^(file:\/{3})|(qrc:\/{2})|(http:\/{2})/,"");
            path = decodeURIComponent(path);
            textFieldControl.text = path
        }
    }
}
