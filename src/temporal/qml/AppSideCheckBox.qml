import QtQuick
import QtQuick.Controls.Basic as Basic

Basic.CheckBox {
    id: control

    required property QtObject theme

    spacing: 8

    indicator: Rectangle {
        implicitWidth: 13
        implicitHeight: 13
        radius: 2
        border.color: "#7f8a85"
        color: "#ffffff"
        opacity: control.enabled ? 1.0 : 0.55

        Rectangle {
            anchors.centerIn: parent
            width: 7
            height: 7
            radius: 1
            color: "#6e7773"
            visible: control.checked
        }
    }

    contentItem: Text {
        text: control.text
        color: control.enabled ? "#4f5854" : "#7a8480"
        font.pixelSize: control.theme.bodyFont
        verticalAlignment: Text.AlignVCenter
    }
}
