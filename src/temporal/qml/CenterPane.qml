import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property QtObject theme
    required property QtObject appBridge
    property var sourcePositions: []
    property bool previewMode: false
    property string previewScenarioKey: ""
    readonly property var previewXTicks: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
    readonly property var runtimeXTicks: ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600"]
    readonly property var displayedSourcePositions: Array.isArray(sourcePositions) ? sourcePositions : []
    readonly property var displayedElevationSeries: previewMode ? root.appBridge.elevationSeries : []
    readonly property var displayedAzimuthSeries: previewMode ? root.appBridge.azimuthSeries : []
    readonly property var displayedXTicks: previewMode ? previewXTicks : runtimeXTicks

    Layout.fillWidth: true
    Layout.fillHeight: true
    radius: theme.cardRadius
    color: "#ffffff"
    border.color: theme.borderColor

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: Math.max(12, theme.panelInset)
        anchors.rightMargin: Math.max(10, theme.panelInset - 2)
        anchors.topMargin: Math.max(8, theme.smallFont)
        anchors.bottomMargin: Math.max(10, theme.smallFont)
        spacing: Math.max(10, theme.smallFont)

        Label {
            text: "声源俯仰角"
            color: "#414952"
            font.pixelSize: theme.sideTitleFont
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: theme.chartHeight
            color: "#ffffff"
            border.color: theme.innerBorderColor

            ChartCanvas {
                theme: root.theme
                anchors.fill: parent
                anchors.margins: 6
                yTicks: ["90", "60", "30", "0", "-30", "-60", "-90"]
                xTicks: root.displayedXTicks
                seriesList: root.displayedElevationSeries
            }
        }

        Label {
            text: "声源方位角"
            color: "#414952"
            font.pixelSize: theme.sideTitleFont
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: theme.chartHeight
            color: "#ffffff"
            border.color: theme.innerBorderColor

            ChartCanvas {
                theme: root.theme
                anchors.fill: parent
                anchors.margins: 6
                yTicks: ["180", "120", "60", "0", "-60", "-120", "-180"]
                xTicks: root.displayedXTicks
                seriesList: root.displayedAzimuthSeries
            }
        }

        Label {
            text: "活动声源位置"
            color: "#414952"
            font.pixelSize: theme.sideTitleFont
        }

        SourceSphereView {
            theme: root.theme
            sourcePositions: root.displayedSourcePositions
            sourceColors: ({})
            previewScenarioKey: root.previewMode ? root.previewScenarioKey : ""
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: theme.sphereHeight
        }
    }
}
