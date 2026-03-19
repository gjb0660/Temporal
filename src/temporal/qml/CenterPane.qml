import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "CenterPanePreviewData.js" as PreviewData

Rectangle {
    id: root

    required property QtObject theme
    property var sourcePositions: []
    property bool previewMode: false
    property string previewScenarioKey: "referenceSingle"

    readonly property var previewCatalog: PreviewData.buildCatalog(theme)
    readonly property var activePreview: previewCatalog[previewScenarioKey] || previewCatalog.referenceSingle
    readonly property var runtimeElevationSeries: [
        {
            sourceId: 7,
            color: theme.accentCyan,
            values: [0.58, 0.57, 0.56, 0.54, 0.53, 0.52, 0.52, 0.52, 0.52]
        },
        {
            sourceId: 15,
            color: theme.accentPurple,
            values: [0.42, 0.45, 0.50, 0.56, 0.61, 0.63, 0.62, 0.60, 0.59]
        }
    ]
    readonly property var runtimeAzimuthSeries: [
        {
            sourceId: 7,
            color: theme.accentCyan,
            values: [0.10, 0.10, 0.11, 0.11, 0.12, 0.12, 0.12, 0.12, 0.12]
        },
        {
            sourceId: 15,
            color: theme.accentPurple,
            values: [0.72, 0.72, 0.73, 0.71, 0.69, 0.66, 0.63, 0.64, 0.68]
        }
    ]
    readonly property var displayedSourcePositions: {
        if (previewMode) {
            return activePreview.sourcePositions
        }
        return Array.isArray(sourcePositions) ? sourcePositions : []
    }
    readonly property var displayedElevationSeries: previewMode ? activePreview.elevationSeries : runtimeElevationSeries
    readonly property var displayedAzimuthSeries: previewMode ? activePreview.azimuthSeries : runtimeAzimuthSeries
    readonly property var displayedSourceColors: previewMode ? activePreview.sourceColors : ({})

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
                xTicks: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
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
                xTicks: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
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
            sourceColors: root.displayedSourceColors
            previewScenarioKey: root.previewMode ? root.activePreview.key : ""
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: theme.sphereHeight
        }
    }
}
