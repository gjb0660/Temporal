// qmllint disable unqualified
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1150
    height: 768
    visible: true
    title: "Temporal Live Data"
    color: "#d9e8e3"

    readonly property int headerHeightValue: Math.max(48, Math.round(height * 0.073))
    readonly property int footerHeightValue: Math.max(34, Math.round(height * 0.052))
    readonly property int pageMargin: Math.max(14, Math.round(width * 0.012))
    readonly property int panelGap: Math.max(10, Math.round(width * 0.010))
    readonly property int panelInset: Math.max(12, Math.round(width * 0.010))
    readonly property int sectionGap: Math.max(8, Math.round(height * 0.014))
    readonly property int leftPanelWidth: Math.max(250, Math.round(width * 0.235))
    readonly property int rightPanelWidth: Math.max(170, Math.round(width * 0.155))
    readonly property int cardRadius: 6
    readonly property int brandFont: Math.max(24, Math.round(height * 0.046))
    readonly property int navFont: Math.max(14, Math.round(height * 0.020))
    readonly property int heroTitleFont: Math.max(28, Math.round(height * 0.040))
    readonly property int panelTitleFont: Math.max(14, Math.round(height * 0.024))
    readonly property int sectionTitleFont: Math.max(14, Math.round(height * 0.024))
    readonly property int bodyFont: Math.max(12, Math.round(height * 0.018))
    readonly property int smallFont: Math.max(12, Math.round(height * 0.017))
    readonly property int captionFont: Math.max(11, Math.round(height * 0.015))
    readonly property int monitorCardHeight: Math.max(270, Math.round(height * 0.43))
    readonly property int controlCardHeight: Math.max(150, Math.round(height * 0.19))
    readonly property int chartCardHeight: Math.max(135, Math.round(height * 0.205))

    header: Rectangle {
        height: root.headerHeightValue
        color: "#039a49"

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: root.pageMargin + 2
            anchors.rightMargin: root.pageMargin + 2

            Label {
                text: "Temporal Studio"
                color: "white"
                font.pixelSize: root.brandFont
                font.bold: true
            }

            Item {
                Layout.fillWidth: true
            }

            Repeater {
                model: ["Configure", "Record", "Camera"]
                delegate: Label {
                    text: modelData
                    color: "white"
                    font.pixelSize: root.navFont
                    Layout.leftMargin: root.panelGap
                }
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        anchors.topMargin: root.headerHeightValue
        color: "#d9e8e3"

        RowLayout {
            anchors.fill: parent
            anchors.margins: root.pageMargin
            spacing: root.panelGap

            Rectangle {
                Layout.preferredWidth: root.leftPanelWidth
                Layout.fillHeight: true
                color: "#c8d9d2"
                radius: root.cardRadius

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.panelInset
                    spacing: root.sectionGap

                    Label {
                        text: "ODAS Data"
                        font.pixelSize: root.heroTitleFont
                        color: "#222"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.monitorCardHeight
                        color: "#e9efec"
                        radius: root.cardRadius
                        border.color: "#c6d2cc"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: Math.max(10, root.sectionGap - 2)

                            Label {
                                text: "Local System Monitor"
                                font.pixelSize: root.bodyFont
                                color: "#3e3e3e"
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: Math.max(38, Math.round(root.height * 0.052))
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: root.panelInset
                                    anchors.rightMargin: root.panelInset
                                    Label {
                                        text: "CPU Usage"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "26.1 %"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: Math.max(38, Math.round(root.height * 0.052))
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: root.panelInset
                                    anchors.rightMargin: root.panelInset
                                    Label {
                                        text: "CPU Temp."
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "-1.0 °C"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: Math.max(38, Math.round(root.height * 0.052))
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: root.panelInset
                                    anchors.rightMargin: root.panelInset
                                    Label {
                                        text: "Memory Usage"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "82 %"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: Math.max(38, Math.round(root.height * 0.052))
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: root.panelInset
                                    anchors.rightMargin: root.panelInset
                                    Label {
                                        text: "IP"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "198.18.0.1"
                                        font.pixelSize: root.bodyFont
                                        color: "#666"
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.controlCardHeight
                        color: "#e9efec"
                        radius: root.cardRadius
                        border.color: "#c6d2cc"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: Math.max(8, root.captionFont)

                            Label {
                                text: "ODAS Control"
                                font.pixelSize: root.bodyFont
                                color: "#4a4a4a"
                            }
                            Label {
                                text: "Status: " + appBridge.status
                                font.pixelSize: root.captionFont
                                color: "#5d6762"
                                wrapMode: Text.WordWrap
                            }
                            RowLayout {
                                spacing: Math.max(6, root.captionFont - 4)
                                Button {
                                    text: "Connect"
                                    font.pixelSize: root.captionFont
                                    onClicked: appBridge.connectRemote()
                                }
                                Button {
                                    text: "Start"
                                    font.pixelSize: root.captionFont
                                    onClicked: appBridge.startRemoteOdas()
                                }
                                Button {
                                    text: "Stop"
                                    font.pixelSize: root.captionFont
                                    onClicked: appBridge.stopRemoteOdas()
                                }
                            }
                            RowLayout {
                                spacing: Math.max(6, root.captionFont - 4)
                                Button {
                                    text: "Listen"
                                    font.pixelSize: root.captionFont
                                    onClicked: appBridge.startStreams()
                                }
                                Button {
                                    text: "Close Streams"
                                    font.pixelSize: root.captionFont
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

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#f2f5f3"
                radius: root.cardRadius
                border.color: "#c7d2cc"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.panelInset
                    spacing: Math.max(8, root.captionFont)

                    Label {
                        text: "Source Elevation"
                        font.pixelSize: root.sectionTitleFont
                        color: "#3f3f3f"
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartCardHeight
                        color: "#ffffff"
                        border.color: "#d2dad6"
                        radius: 4
                        Label {
                            anchors.centerIn: parent
                            text: "Elevation chart placeholder"
                            font.pixelSize: root.bodyFont
                            color: "#919191"
                        }
                    }

                    Label {
                        text: "Source Azimut"
                        font.pixelSize: root.sectionTitleFont
                        color: "#3f3f3f"
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartCardHeight
                        color: "#ffffff"
                        border.color: "#d2dad6"
                        radius: 4
                        Label {
                            anchors.centerIn: parent
                            text: "Azimut chart placeholder"
                            font.pixelSize: root.bodyFont
                            color: "#919191"
                        }
                    }

                    Label {
                        text: "Active sources locations"
                        font.pixelSize: root.sectionTitleFont
                        color: "#3f3f3f"
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#ffffff"
                        border.color: "#d2dad6"
                        radius: 4
                        Label {
                            anchors.centerIn: parent
                            text: "3D sphere placeholder"
                            font.pixelSize: root.bodyFont
                            color: "#919191"
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: root.rightPanelWidth
                Layout.fillHeight: true
                color: "#c8d9d2"
                radius: root.cardRadius

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.panelInset
                    spacing: root.sectionGap

                    Label {
                        text: "Sources"
                        font.pixelSize: root.heroTitleFont - 4
                        color: "#2e2e2e"
                    }

                    Repeater {
                        model: appBridge.sourceIds
                        delegate: CheckBox {
                            required property int modelData
                            text: "Source " + modelData
                            checked: appBridge.isSourceSelected(modelData)
                            onToggled: appBridge.setSourceSelected(modelData, checked)
                            font.pixelSize: root.bodyFont
                        }
                    }

                    Label {
                        visible: appBridge.sourceCount === 0
                        text: "No active source"
                        font.pixelSize: root.panelTitleFont
                        color: "#6a746f"
                        wrapMode: Text.WordWrap
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#b9cac2"
                    }

                    Label {
                        text: "Filters"
                        font.pixelSize: root.heroTitleFont - 4
                        color: "#2e2e2e"
                    }
                    CheckBox {
                        text: "Sources (" + appBridge.sourceCount + ")"
                        checked: appBridge.sourcesEnabled
                        font.pixelSize: root.bodyFont
                        onToggled: appBridge.setSourcesEnabled(checked)
                    }
                    CheckBox {
                        text: "Potentials (" + appBridge.potentialCount + ")"
                        checked: appBridge.potentialsEnabled
                        font.pixelSize: root.bodyFont
                        onToggled: appBridge.setPotentialsEnabled(checked)
                    }
                    Label {
                        text: "Potential sources\nenergy range:"
                        font.pixelSize: root.smallFont
                        color: "#4d5651"
                    }
                    Label {
                        text: appBridge.potentialEnergyMin.toFixed(2) + " - " + appBridge.potentialEnergyMax.toFixed(2)
                        font.pixelSize: root.bodyFont
                        color: "#5f6863"
                    }
                    RangeSlider {
                        from: 0
                        to: 1
                        first.value: appBridge.potentialEnergyMin
                        second.value: appBridge.potentialEnergyMax
                        first.onValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)
                        second.onValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)
                    }

                    Item {
                        Layout.fillHeight: true
                    }
                }
            }
        }
    }

    footer: Rectangle {
        height: root.footerHeightValue
        color: "#039a49"
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: root.pageMargin
            anchors.rightMargin: root.pageMargin
            Label {
                text: "Temporal interface for ODAS"
                color: "white"
                font.pixelSize: root.bodyFont
            }
            Item {
                Layout.fillWidth: true
            }
            Label {
                text: "Legal"
                color: "white"
                font.pixelSize: root.bodyFont
            }
        }
    }
}
