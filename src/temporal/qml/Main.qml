// qmllint disable unqualified
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1188
    height: 794
    minimumWidth: 940
    minimumHeight: 640
    visible: true
    title: "Temporal 实时数据"
    color: "#dce9e2"
    font.family: "Microsoft YaHei UI"

    readonly property QtObject theme: QtObject {
        readonly property color pageBackground: "#dce9e2"
        readonly property color panelBackground: "#d8e8e1"
        readonly property color cardBackground: "#f9fbfa"
        readonly property color borderColor: "#cadbd2"
        readonly property color accentGreen: "#079b49"
        readonly property color accentPurple: "#cf54ea"
        readonly property color accentCyan: "#47c8cf"
        readonly property color titleColor: "#333333"
        readonly property color mutedText: "#5f6d67"
        readonly property int menuHeight: 22
        readonly property int brandHeight: Math.max(46, Math.round(root.height * 0.064))
        readonly property int footerHeightValue: Math.max(28, Math.round(root.height * 0.040))
        readonly property int pageMargin: Math.max(14, Math.round(root.width * 0.013))
        readonly property int columnGap: Math.max(12, Math.round(root.width * 0.010))
        readonly property int panelInset: Math.max(14, Math.round(root.width * 0.012))
        readonly property int sectionGap: Math.max(12, Math.round(root.height * 0.016))
        readonly property int leftPanelWidth: Math.max(255, Math.min(305, Math.round(root.width * 0.245)))
        readonly property int rightPanelWidth: Math.max(170, Math.min(210, Math.round(root.width * 0.160)))
        readonly property int brandFont: Math.max(22, Math.round(root.height * 0.040))
        readonly property int sideTitleFont: Math.max(17, Math.round(root.height * 0.031))
        readonly property int sectionTitleFont: Math.max(14, Math.round(root.height * 0.024))
        readonly property int bodyFont: Math.max(12, Math.round(root.height * 0.019))
        readonly property int smallFont: Math.max(11, Math.round(root.height * 0.017))
        readonly property int codeFont: Math.max(11, Math.round(root.height * 0.016))
        readonly property int chartHeight: Math.max(165, Math.round(root.height * 0.194))
        readonly property int sphereHeight: Math.max(228, Math.round(root.height * 0.340))
    }

    function sourceRows() {
        const ids = appBridge.sourceIds
        const rows = []
        if (ids.length === 0) {
            for (let index = 0; index < 4; index += 1) {
                rows.push({
                    sourceId: -1,
                    label: "声源",
                    checked: true,
                    enabled: false,
                    badge: index === 1 ? "15" : ""
                })
            }
            return rows
        }

        for (let index = 0; index < ids.length; index += 1) {
            const sourceId = ids[index]
            rows.push({
                sourceId: sourceId,
                label: "声源",
                checked: appBridge.isSourceSelected(sourceId),
                enabled: true,
                badge: String(sourceId)
            })
        }
        return rows
    }

    header: AppHeader {
        theme: root.theme
    }

    footer: AppFooter {
        theme: root.theme
    }

    Rectangle {
        anchors.fill: parent
        color: root.theme.pageBackground

        RowLayout {
            anchors.fill: parent
            anchors.margins: root.theme.pageMargin
            spacing: root.theme.columnGap

            LeftSidebar {
                theme: root.theme
            }

            CenterPane {
                theme: root.theme
                sourcePositions: appBridge.sourcePositions
            }

            RightSidebar {
                theme: root.theme
                sourceRows: root.sourceRows()
            }
        }
    }
}
