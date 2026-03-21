import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property QtObject theme
    required property QtObject appBridge

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
                xTickModel: root.appBridge.chartXTicksModel
                seriesModel: root.appBridge.elevationSeriesModel
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
                xTickModel: root.appBridge.chartXTicksModel
                seriesModel: root.appBridge.azimuthSeriesModel
            }
        }

        Label {
            text: "活动声源位置"
            color: "#414952"
            font.pixelSize: theme.sideTitleFont
        }

        SourceSphereView {
            theme: root.theme
            sourcePositionsModel: root.appBridge.sourcePositionsModel
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: theme.sphereHeight
        }
    }
}
