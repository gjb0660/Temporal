import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property QtObject theme
    required property QtObject appBridge
    readonly property int contentLeftMargin: Math.max(12, theme.panelInset)
    readonly property int contentRightMargin: Math.max(10, theme.panelInset - 2)
    readonly property int contentTopMargin: Math.max(8, theme.smallFont)
    readonly property int contentBottomMargin: Math.max(10, theme.smallFont)
    readonly property int sectionSpacing: Math.max(10, theme.smallFont)

    Layout.fillWidth: true
    Layout.fillHeight: true
    radius: theme.cardRadius
    color: "#ffffff"
    border.color: theme.borderColor

    ColumnLayout {
        id: topContent
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: root.contentLeftMargin
        anchors.rightMargin: root.contentRightMargin
        anchors.topMargin: root.contentTopMargin
        spacing: root.sectionSpacing
        z: 1

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
                xAxisLabel: "时间 (0.01s)"
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
                xAxisLabel: "时间 (0.01s)"
            }
        }

        Label {
            id: sphereTitle
            text: "活动声源位置"
            color: "#414952"
            font.pixelSize: theme.sideTitleFont
        }
    }

    SourceSphereView {
        theme: root.theme
        sourcePositionsModel: root.appBridge.sourcePositionsModel
        anchors.top: topContent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: root.contentLeftMargin
        anchors.rightMargin: root.contentRightMargin
        anchors.bottomMargin: root.border.width
        anchors.topMargin: -root.height * 0.1
    }
}
