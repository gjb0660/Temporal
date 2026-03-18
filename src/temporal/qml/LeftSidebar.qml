import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    required property QtObject theme

    Layout.preferredWidth: theme.leftPanelWidth
    Layout.fillHeight: true
    radius: 4
    color: theme.panelBackground

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme.panelInset
        spacing: theme.sectionGap

        Label {
            text: "ODAS 数据"
            color: theme.titleColor
            font.pixelSize: Math.max(30, theme.sideTitleFont + 8)
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(300, parent.height * 0.405)
            radius: 4
            color: theme.cardBackground
            border.color: theme.borderColor

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: theme.panelInset
                spacing: Math.max(10, theme.smallFont)

                Label {
                    text: "远程 odaslive 日志"
                    color: "#414141"
                    font.pixelSize: theme.sectionTitleFont
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 3
                    color: "#ffffff"
                    border.color: "#d1ddd7"

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 8
                        clip: true

                        TextArea {
                            width: parent.width
                            readOnly: true
                            wrapMode: TextArea.NoWrap
                            selectByMouse: true
                            text: appBridge.remoteLogLines.join("\n")
                            color: "#2e3532"
                            font.family: "Consolas"
                            font.pixelSize: theme.codeFont
                            padding: 0
                            background: null
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(168, parent.height * 0.220)
            radius: 4
            color: theme.cardBackground
            border.color: theme.borderColor

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: theme.panelInset
                spacing: 8

                Label {
                    text: "ODAS 控制"
                    color: "#414141"
                    font.pixelSize: theme.sectionTitleFont
                }

                Label {
                    text: appBridge.status
                    color: theme.mutedText
                    font.pixelSize: theme.bodyFont
                    wrapMode: Text.WordWrap
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 3
                    columnSpacing: 8
                    rowSpacing: 8

                    AppActionButton {
                        theme: root.theme
                        text: "连接"
                        Layout.fillWidth: true
                        onClicked: appBridge.connectRemote()
                    }

                    AppActionButton {
                        theme: root.theme
                        text: "启动"
                        Layout.fillWidth: true
                        onClicked: appBridge.startRemoteOdas()
                    }

                    AppActionButton {
                        theme: root.theme
                        text: "停止"
                        Layout.fillWidth: true
                        onClicked: appBridge.stopRemoteOdas()
                    }

                    AppActionButton {
                        theme: root.theme
                        text: "监听"
                        Layout.fillWidth: true
                        onClicked: appBridge.startStreams()
                    }

                    AppActionButton {
                        theme: root.theme
                        text: "关闭流"
                        Layout.fillWidth: true
                        Layout.columnSpan: 2
                        onClicked: appBridge.stopStreams()
                    }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
