import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts

Rectangle {
    id: root
    required property QtObject theme
    required property var sourceRows
    required property var recordingSessions

    Layout.preferredWidth: theme.rightPanelWidth
    Layout.fillHeight: true
    radius: 4
    color: theme.panelBackground

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: theme.panelInset
        anchors.rightMargin: theme.panelInset
        anchors.topMargin: Math.max(10, theme.panelInset + 2)
        anchors.bottomMargin: theme.panelInset
        spacing: Math.max(10, theme.sectionGap - 1)

        Label {
            text: "声源"
            color: theme.titleColor
            font.pixelSize: Math.max(26, theme.sideTitleFont + 3)
        }

        Repeater {
            model: sourceRows

            delegate: ColumnLayout {
                required property var modelData
                Layout.fillWidth: true
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 22

                    AppSideCheckBox {
                        theme: root.theme
                        checked: modelData.checked
                        enabled: modelData.enabled
                        text: modelData.label
                        Layout.alignment: Qt.AlignVCenter
                        onToggled: {
                            if (modelData.enabled) {
                                appBridge.setSourceSelected(modelData.sourceId, checked)
                            }
                        }
                    }

                    Rectangle {
                        visible: modelData.badge !== ""
                        radius: height / 2
                        color: theme.accentPurple
                        Layout.preferredHeight: 20
                        Layout.preferredWidth: Math.max(24, badgeText.implicitWidth + 12)
                        Layout.alignment: Qt.AlignVCenter

                        Label {
                            id: badgeText
                            anchors.centerIn: parent
                            text: modelData.badge
                            color: "white"
                            font.pixelSize: theme.smallFont
                            font.bold: true
                        }
                    }

                    Item {
                        Layout.fillWidth: true
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: "#c9d9d2"
                }
            }
        }

        Item {
            Layout.preferredHeight: 18
        }

        Label {
            text: "筛选器"
            color: theme.titleColor
            font.pixelSize: Math.max(26, theme.sideTitleFont + 3)
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: "#c9d9d2"
        }

        AppSideCheckBox {
            theme: root.theme
            text: "声源"
            checked: appBridge.sourcesEnabled
            onToggled: appBridge.setSourcesEnabled(checked)
        }

        AppSideCheckBox {
            theme: root.theme
            text: "候选点"
            checked: appBridge.potentialsEnabled
            onToggled: appBridge.setPotentialsEnabled(checked)
        }

        Item {
            Layout.preferredHeight: 16
        }

        Label {
            text: "候选声源\n能量范围:"
            color: "#55635d"
            font.pixelSize: theme.bodyFont
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 72

            Label {
                anchors.left: parent.left
                anchors.top: parent.top
                text: appBridge.potentialEnergyMin.toFixed(0)
                color: "#3f4743"
                font.pixelSize: theme.bodyFont
            }

            Basic.RangeSlider {
                id: energySlider
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.topMargin: 22
                from: 0
                to: 1
                first.value: appBridge.potentialEnergyMin
                second.value: appBridge.potentialEnergyMax

                first.onValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)
                second.onValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)

                background: Rectangle {
                    x: parent.leftPadding
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    width: parent.availableWidth
                    height: 4
                    radius: 2
                    color: "#d5d8d6"

                    Rectangle {
                        x: parent.parent.first.visualPosition * parent.width
                        width: parent.parent.second.visualPosition * parent.width - x
                        height: parent.height
                        radius: 2
                        color: "#2a95d6"
                    }
                }

                first.handle: Rectangle {
                    x: parent.leftPadding + parent.first.visualPosition * (parent.availableWidth - width)
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    implicitWidth: 16
                    implicitHeight: 22
                    radius: 4
                    color: "#1b92d5"
                }

                second.handle: Rectangle {
                    x: parent.leftPadding + parent.second.visualPosition * (parent.availableWidth - width)
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    implicitWidth: 16
                    implicitHeight: 22
                    radius: 4
                    color: "#1b92d5"
                }
            }

            Label {
                anchors.left: parent.left
                anchors.top: energySlider.bottom
                anchors.topMargin: 4
                text: appBridge.potentialEnergyMax.toFixed(0)
                color: "#3f4743"
                font.pixelSize: theme.bodyFont
            }
        }

        Item {
            Layout.fillHeight: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: "#c9d9d2"
        }

        Label {
            text: "录音会话"
            color: theme.titleColor
            font.pixelSize: Math.max(20, theme.sideTitleFont)
        }

        Repeater {
            model: root.recordingSessions

            delegate: Label {
                required property string modelData
                Layout.fillWidth: true
                text: modelData
                color: theme.mutedText
                font.pixelSize: theme.codeFont
                wrapMode: Text.WordWrap
            }
        }

        Label {
            visible: root.recordingSessions.length === 0
            text: "暂无活跃录音会话"
            color: theme.mutedText
            font.pixelSize: theme.bodyFont
        }
    }
}
