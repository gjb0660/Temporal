import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root

    required property QtObject appBridge

    width: 1188
    height: 794
    minimumWidth: 940
    minimumHeight: 640
    visible: true
    title: "Temporal 实时数据"
    color: "#eef2f6"
    font.family: "Segoe UI"

    readonly property QtObject theme: QtObject {
        readonly property color pageBackground: "#eef2f6"
        readonly property color panelBackground: "#edf4ef"
        readonly property color cardBackground: "#ffffff"
        readonly property color borderColor: "#c6d0db"
        readonly property color innerBorderColor: "#d6dde6"
        readonly property color dividerColor: "#d4dce5"
        readonly property color titleColor: "#2c333a"
        readonly property color mutedText: "#5f6771"
        readonly property color subtleText: "#727c87"
        readonly property color accentGreen: "#11a44b"
        readonly property color accentPurple: "#cf54ea"
        readonly property color accentCyan: "#4dc6d8"
        readonly property color axisBlue: "#4168ff"
        readonly property color axisOrange: "#ff7a29"
        readonly property color axisGreen: "#35b56f"
        readonly property color buttonFill: "#fbfcfd"
        readonly property color buttonHover: "#f3f6f9"
        readonly property color buttonPressed: "#e8edf3"
        readonly property color buttonBorder: "#b8c3cf"
        readonly property color buttonText: "#24303a"
        readonly property color buttonDisabledText: "#8a95a1"
        readonly property int menuHeight: 28
        readonly property int brandHeight: Math.max(50, Math.round(root.height * 0.065))
        readonly property int footerHeightValue: Math.max(30, Math.round(root.height * 0.040))
        readonly property int pageMargin: Math.max(14, Math.round(root.width * 0.013))
        readonly property int columnGap: Math.max(14, Math.round(root.width * 0.011))
        readonly property int panelInset: Math.max(14, Math.round(root.width * 0.012))
        readonly property int sectionGap: Math.max(12, Math.round(root.height * 0.016))
        readonly property int leftPanelWidth: Math.max(262, Math.min(310, Math.round(root.width * 0.248)))
        readonly property int rightPanelWidth: Math.max(178, Math.min(220, Math.round(root.width * 0.166)))
        readonly property int brandFont: Math.max(18, Math.round(root.height * 0.033))
        readonly property int sideTitleFont: Math.max(16, Math.round(root.height * 0.030))
        readonly property int sectionTitleFont: Math.max(14, Math.round(root.height * 0.024))
        readonly property int bodyFont: Math.max(12, Math.round(root.height * 0.019))
        readonly property int smallFont: Math.max(11, Math.round(root.height * 0.017))
        readonly property int codeFont: Math.max(11, Math.round(root.height * 0.016))
        readonly property int chartHeight: Math.max(132, Math.round(root.height * 0.162))
        readonly property int sphereHeight: Math.max(205, Math.round(root.height * 0.290))
        readonly property int cardRadius: 3
    }

    header: AppHeader {
        theme: root.theme
        appBridge: root.appBridge
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
                appBridge: root.appBridge
            }

            CenterPane {
                theme: root.theme
                appBridge: root.appBridge
            }

            RightSidebar {
                theme: root.theme
                appBridge: root.appBridge
            }
        }
    }
}
