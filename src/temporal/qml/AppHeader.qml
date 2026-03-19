import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Column {
    required property QtObject theme

    width: parent ? parent.width : 0
    spacing: 0

    Rectangle {
        width: parent.width
        height: theme.menuHeight
        color: "#ffffff"
        border.color: theme.dividerColor
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            spacing: 16

            Repeater {
                model: ["文件", "编辑", "视图", "窗口", "帮助"]

                delegate: Label {
                    text: modelData
                    color: "#1d1d1d"
                    font.pixelSize: theme.smallFont + 1
                    Layout.alignment: Qt.AlignVCenter
                }
            }

            Item {
                Layout.fillWidth: true
            }
        }
    }

    Rectangle {
        width: parent.width
        height: theme.brandHeight
        color: theme.accentGreen

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: theme.pageMargin
            anchors.rightMargin: theme.pageMargin
            spacing: Math.max(12, theme.columnGap)

            Rectangle {
                Layout.preferredWidth: 26
                Layout.preferredHeight: 26
                radius: 3
                color: "transparent"
                border.color: "white"
                border.width: 2

                Repeater {
                    model: 4

                    delegate: Rectangle {
                        width: 6
                        height: 6
                        radius: 1
                        color: "white"
                        x: 4 + (index % 2) * 10
                        y: 4 + Math.floor(index / 2) * 10
                    }
                }
            }

            Label {
                text: "Temporal Studio"
                color: "white"
                font.pixelSize: theme.brandFont
                font.bold: true
                Layout.alignment: Qt.AlignVCenter
            }

            Item {
                Layout.fillWidth: true
            }

            Repeater {
                model: ["配置", "录制", "相机"]

                delegate: Label {
                    text: modelData
                    color: "white"
                    font.pixelSize: theme.bodyFont
                    Layout.leftMargin: Math.max(10, theme.columnGap - 2)
                    Layout.alignment: Qt.AlignVCenter
                }
            }
        }
    }
}
