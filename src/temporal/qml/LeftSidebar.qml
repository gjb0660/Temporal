import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property QtObject theme
    required property QtObject appBridge

    Layout.preferredWidth: theme.leftPanelWidth
    Layout.fillHeight: true
    radius: theme.cardRadius
    color: theme.panelBackground
    border.color: theme.borderColor

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme.panelInset
        spacing: theme.sectionGap

        Label {
            text: "ODAS 数据"
            color: theme.titleColor
            font.pixelSize: Math.max(28, theme.sideTitleFont + 8)
        }

        Item {
            id: panelArea
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: theme.sectionGap

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredHeight: Math.max(300, panelArea.height * 0.60)
                    Layout.minimumHeight: 280
                    radius: theme.cardRadius
                    color: theme.cardBackground
                    border.color: theme.borderColor

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: theme.panelInset
                        spacing: Math.max(10, theme.smallFont)

                        Label {
                            text: "远程 odaslive 日志"
                            color: theme.titleColor
                            font.pixelSize: theme.sectionTitleFont + 1
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 2
                            color: "#ffffff"
                            border.color: theme.innerBorderColor

                            ScrollView {
                                anchors.fill: parent
                                anchors.margins: 8
                                clip: true

                                TextArea {
                                    width: parent.width
                                    readOnly: true
                                    wrapMode: TextArea.WrapAnywhere
                                    selectByMouse: true
                                    text: root.appBridge.remoteLogText
                                    color: "#24303a"
                                    font.family: "Consolas"
                                    font.pixelSize: theme.codeFont
                                    padding: 0
                                    background: null
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Item {
                                Layout.fillWidth: true
                            }

                            AppActionButton {
                                theme: root.theme
                                text: "清空日志"
                                onClicked: root.appBridge.clearRemoteLog()
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredHeight: Math.max(210, panelArea.height * 0.40)
                    Layout.minimumHeight: 188
                    radius: theme.cardRadius
                    color: theme.cardBackground
                    border.color: theme.borderColor

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: theme.panelInset
                        spacing: 10

                        Label {
                            text: "ODAS 控制"
                            color: theme.titleColor
                            font.pixelSize: theme.sectionTitleFont + 1
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 90
                            radius: 2
                            color: "#ffffff"
                            border.color: theme.innerBorderColor

                            ScrollView {
                                anchors.fill: parent
                                anchors.margins: 8
                                clip: true

                                TextArea {
                                    width: parent.width
                                    readOnly: true
                                    wrapMode: TextArea.Wrap
                                    selectByMouse: true
                                    text: root.appBridge.controlSummary
                                    color: theme.mutedText
                                    font.pixelSize: theme.bodyFont
                                    padding: 0
                                    background: null
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppActionButton {
                                theme: root.theme
                                text: root.appBridge.odasStarting ? "启动中" : (root.appBridge.odasRunning ? "停止" : "启动")
                                enabled: !root.appBridge.odasStarting
                                Layout.fillWidth: true
                                onClicked: root.appBridge.toggleRemoteOdas()
                            }

                            AppActionButton {
                                theme: root.theme
                                text: root.appBridge.streamsActive ? "停止监听" : "监听"
                                enabled: !!root.appBridge.canToggleStreams
                                Layout.fillWidth: true
                                onClicked: root.appBridge.toggleStreams()
                            }
                        }
                    }
                }
            }
        }
    }
}
