import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts

Rectangle {
    id: root

    required property QtObject theme
    required property QtObject appBridge
    readonly property int sectionTitleFont: Math.max(20, theme.sideTitleFont)
    readonly property color sectionTitleColor: theme.titleColor

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
            color: root.sectionTitleColor
            font.pixelSize: root.sectionTitleFont
        }

        Repeater {
            model: root.appBridge.sourceRowsModel

            delegate: ColumnLayout {
                id: sourceRow
                required property int sourceId
                required property string label
                required property bool checked
                required property bool active
                required property string badge
                required property string badgeColor

                Layout.fillWidth: true
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 22
                    opacity: sourceRow.active ? 1.0 : 0.55

                    AppSideCheckBox {
                        theme: root.theme
                        checked: sourceRow.checked
                        enabled: sourceRow.enabled
                        text: sourceRow.label
                        Layout.alignment: Qt.AlignVCenter
                        onToggled: {
                            if (sourceRow.enabled) {
                                root.appBridge.setSourceSelected(sourceRow.sourceId, checked)
                            }
                        }
                    }

                    Rectangle {
                        visible: sourceRow.badge !== ""
                        radius: height / 2
                        color: sourceRow.badgeColor || theme.accentPurple
                        Layout.preferredHeight: 20
                        Layout.preferredWidth: Math.max(24, badgeText.implicitWidth + 12)
                        Layout.alignment: Qt.AlignVCenter

                        Label {
                            id: badgeText
                            anchors.centerIn: parent
                            text: sourceRow.badge
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

        Label {
            visible: root.appBridge.sourceRowsModel.count === 0
            text: "暂无活动声源"
            color: theme.mutedText
            font.pixelSize: theme.bodyFont
            Layout.fillWidth: true
        }

        Item {
            Layout.fillHeight: true
        }

        Label {
            text: "筛选器"
            color: root.sectionTitleColor
            font.pixelSize: root.sectionTitleFont
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: "#c9d9d2"
        }

        AppSideCheckBox {
            theme: root.theme
            text: "声源"
            checked: root.appBridge.sourcesEnabled
            onToggled: root.appBridge.setSourcesEnabled(checked)
        }

        AppSideCheckBox {
            theme: root.theme
            text: "候选点"
            checked: root.appBridge.potentialsEnabled
            onToggled: root.appBridge.setPotentialsEnabled(checked)
        }

        Label {
            text: "候选声源能量范围"
            color: "#55635d"
            font.pixelSize: theme.bodyFont
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 48

            Label {
                anchors.top: parent.top
                anchors.left: parent.left
                text: root.appBridge.potentialEnergyMin.toFixed(2)
                color: "#3f4743"
                font.pixelSize: theme.bodyFont
            }

            Label {
                anchors.top: parent.top
                anchors.right: parent.right
                text: root.appBridge.potentialEnergyMax.toFixed(2)
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
                first.value: root.appBridge.potentialEnergyMin
                second.value: root.appBridge.potentialEnergyMax

                first.onValueChanged: root.appBridge.setPotentialEnergyRange(first.value, second.value)
                second.onValueChanged: root.appBridge.setPotentialEnergyRange(first.value, second.value)

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
                    implicitHeight: implicitWidth
                    radius: implicitWidth / 2
                    color: "#1b92d5"
                }

                second.handle: Rectangle {
                    x: parent.leftPadding + parent.second.visualPosition * (parent.availableWidth - width)
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    implicitWidth: 16
                    implicitHeight: implicitWidth
                    radius: implicitWidth / 2
                    color: "#1b92d5"
                }
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
            color: root.sectionTitleColor
            font.pixelSize: root.sectionTitleFont
        }

        Repeater {
            model: root.appBridge.recordingSessionsModel

            delegate: Item {
                id: sessionItem
                required property int targetId
                required property string summary
                required property string details
                required property bool hasActive
                Layout.fillWidth: true

                implicitHeight: summaryLabel.implicitHeight

                Label {
                    id: summaryLabel
                    anchors.left: parent.left
                    anchors.right: parent.right
                    text: sessionItem.summary
                    color: theme.mutedText
                    font.pixelSize: theme.codeFont
                    wrapMode: Text.WordWrap
                }

                HoverHandler {
                    id: sessionHover
                }

                ToolTip.visible: sessionHover.hovered && sessionItem.details.length > 0
                ToolTip.text: sessionItem.details
                ToolTip.delay: 200
            }
        }

        Label {
            visible: root.appBridge.recordingSessionsModel.count === 0
            text: "暂无活跃录音会话"
            color: theme.mutedText
            font.pixelSize: theme.bodyFont
        }
    }
}
