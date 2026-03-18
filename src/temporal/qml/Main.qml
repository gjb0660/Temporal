// qmllint disable unqualified
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1360
    height: 820
    visible: true
    title: "Temporal Live Data"
    color: "#d9e8e3"

    header: Rectangle {
        height: 56
        color: "#039a49"

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 20
            anchors.rightMargin: 20

            Label {
                text: "Temporal Studio"
                color: "white"
                font.pixelSize: 30
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
                    font.pixelSize: 18
                    Layout.leftMargin: 18
                }
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        anchors.topMargin: 56
        color: "#d9e8e3"

        RowLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16

            Rectangle {
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                color: "#c8d9d2"
                radius: 6

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 16

                    Label {
                        text: "ODAS Data"
                        font.pixelSize: 42
                        color: "#222"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 300
                        color: "#e9efec"
                        radius: 6
                        border.color: "#c6d2cc"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            Label {
                                text: "Local System Monitor"
                                font.pixelSize: 32
                                color: "#3e3e3e"
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    Label {
                                        text: "CPU Usage"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "26.1 %"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    Label {
                                        text: "CPU Temp."
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "-1.0 °C"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    Label {
                                        text: "Memory Usage"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "82 %"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48
                                color: "#f4f7f5"
                                border.color: "#d1dbd6"
                                radius: 4
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    Label {
                                        text: "IP"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                    Item {
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: "198.18.0.1"
                                        font.pixelSize: 24
                                        color: "#666"
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        color: "#e9efec"
                        radius: 6
                        border.color: "#c6d2cc"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            Label {
                                text: "ODAS Control"
                                font.pixelSize: 34
                                color: "#4a4a4a"
                            }
                            Label {
                                text: "Status: " + appBridge.status
                                font.pixelSize: 22
                                color: "#5d6762"
                            }
                            RowLayout {
                                spacing: 8
                                Button {
                                    text: "Connect"
                                    onClicked: appBridge.connectRemote()
                                }
                                Button {
                                    text: "Start"
                                    onClicked: appBridge.startRemoteOdas()
                                }
                                Button {
                                    text: "Stop"
                                    onClicked: appBridge.stopRemoteOdas()
                                }
                            }
                            RowLayout {
                                spacing: 8
                                Button {
                                    text: "Listen"
                                    onClicked: appBridge.startStreams()
                                }
                                Button {
                                    text: "Close Streams"
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
                radius: 6
                border.color: "#c7d2cc"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    Label {
                        text: "Source Elevation"
                        font.pixelSize: 36
                        color: "#3f3f3f"
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180
                        color: "#ffffff"
                        border.color: "#d2dad6"
                        radius: 4
                        Label {
                            anchors.centerIn: parent
                            text: "Elevation chart placeholder"
                            font.pixelSize: 24
                            color: "#919191"
                        }
                    }

                    Label {
                        text: "Source Azimut"
                        font.pixelSize: 36
                        color: "#3f3f3f"
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180
                        color: "#ffffff"
                        border.color: "#d2dad6"
                        radius: 4
                        Label {
                            anchors.centerIn: parent
                            text: "Azimut chart placeholder"
                            font.pixelSize: 24
                            color: "#919191"
                        }
                    }

                    Label {
                        text: "Active sources locations"
                        font.pixelSize: 36
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
                            font.pixelSize: 28
                            color: "#919191"
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: 230
                Layout.fillHeight: true
                color: "#c8d9d2"
                radius: 6

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 16

                    Label {
                        text: "Sources"
                        font.pixelSize: 50
                        color: "#2e2e2e"
                    }

                    Repeater {
                        model: appBridge.sourceItems
                        delegate: CheckBox {
                            text: modelData
                            checked: true
                            font.pixelSize: 28
                        }
                    }

                    Label {
                        visible: appBridge.sourceCount === 0
                        text: "No active source"
                        font.pixelSize: 22
                        color: "#6a746f"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#b9cac2"
                    }

                    Label {
                        text: "Filters"
                        font.pixelSize: 50
                        color: "#2e2e2e"
                    }
                    CheckBox {
                        text: "Sources (" + appBridge.sourceCount + ")"
                        checked: appBridge.sourcesEnabled
                        font.pixelSize: 28
                        onToggled: appBridge.setSourcesEnabled(checked)
                    }
                    CheckBox {
                        text: "Potentials (" + appBridge.potentialCount + ")"
                        checked: appBridge.potentialsEnabled
                        font.pixelSize: 28
                        onToggled: appBridge.setPotentialsEnabled(checked)
                    }
                    Label {
                        text: "Potential sources\nenergy range:"
                        font.pixelSize: 28
                        color: "#4d5651"
                    }
                    Label {
                        text: appBridge.potentialEnergyMin.toFixed(2) + " - "
                            + appBridge.potentialEnergyMax.toFixed(2)
                        font.pixelSize: 22
                        color: "#5f6863"
                    }
                    RangeSlider {
                        from: 0
                        to: 1
                        first.value: appBridge.potentialEnergyMin
                        second.value: appBridge.potentialEnergyMax
                        onFirstValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)
                        onSecondValueChanged: appBridge.setPotentialEnergyRange(first.value, second.value)
                    }

                    Item {
                        Layout.fillHeight: true
                    }
                }
            }
        }
    }

    footer: Rectangle {
        height: 40
        color: "#039a49"
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 14
            anchors.rightMargin: 14
            Label {
                text: "Temporal interface for ODAS"
                color: "white"
                font.pixelSize: 24
            }
            Item {
                Layout.fillWidth: true
            }
            Label {
                text: "Legal"
                color: "white"
                font.pixelSize: 24
            }
        }
    }
}
