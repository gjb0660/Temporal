import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    required property QtObject theme

    height: theme.footerHeightValue
    color: theme.accentGreen

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: theme.pageMargin
        anchors.rightMargin: theme.pageMargin

        Label {
            text: "ODAS 图形界面客户端"
            color: "white"
            font.pixelSize: theme.bodyFont
        }

        Item {
            Layout.fillWidth: true
        }

        Label {
            text: "法律声明"
            color: "white"
            font.pixelSize: theme.bodyFont
        }
    }
}
