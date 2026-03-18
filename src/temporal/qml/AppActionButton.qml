import QtQuick
import QtQuick.Controls.Basic as Basic

Basic.Button {
    id: control

    required property QtObject theme

    implicitHeight: 32
    implicitWidth: 84
    font.pixelSize: theme.bodyFont
    padding: 0

    contentItem: Text {
        text: control.text
        color: control.enabled ? "#2f3a36" : "#89948f"
        font.pixelSize: control.theme.bodyFont
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: 3
        color: control.pressed ? "#d8e4de" : "#f7faf8"
        border.color: control.enabled ? "#b9cbc2" : "#d7dfdb"
    }
}
