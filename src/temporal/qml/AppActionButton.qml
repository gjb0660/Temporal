import QtQuick
import QtQuick.Controls.Basic as Basic

Basic.Button {
    id: control

    required property QtObject theme

    implicitHeight: 34
    implicitWidth: 96
    font.pixelSize: theme.bodyFont
    padding: 0

    contentItem: Text {
        text: control.text
        color: control.enabled ? control.theme.buttonText : control.theme.buttonDisabledText
        font.pixelSize: control.theme.bodyFont
        font.family: "Segoe UI"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: 2
        color: !control.enabled ? "#f6f8fa" : control.pressed ? control.theme.buttonPressed : control.hovered ? control.theme.buttonHover : control.theme.buttonFill
        border.color: control.theme.buttonBorder
        border.width: 1
    }
}
