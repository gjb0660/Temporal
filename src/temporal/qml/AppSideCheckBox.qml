import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic

Basic.CheckBox {
    id: control

    required property QtObject theme

    implicitHeight: Math.max(20, contentItem.implicitHeight)
    spacing: 8
    leftPadding: 0
    topPadding: 0
    bottomPadding: 0

    indicator: Rectangle {
        implicitWidth: 13
        implicitHeight: 13
        y: control.topPadding + (control.availableHeight - height) / 2
        radius: 2
        border.color: "#7e8a96"
        color: "#ffffff"
        opacity: control.enabled ? 1.0 : 0.55

        Rectangle {
            anchors.centerIn: parent
            width: 7
            height: 7
            radius: 1
            color: "#5d6a77"
            visible: control.checked
        }
    }

    contentItem: Label {
        text: control.text
        color: control.enabled ? "#4a5560" : "#7d8792"
        font.pixelSize: control.theme.bodyFont
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
        height: control.availableHeight
    }
}
