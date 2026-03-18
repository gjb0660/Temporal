// qmllint disable unqualified
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1188
    height: 794
    minimumWidth: 920
    minimumHeight: 620
    visible: true
    title: "Temporal Live Data"
    color: "#dce9e2"

    readonly property color pageBackground: "#dce9e2"
    readonly property color panelBackground: "#d6e7df"
    readonly property color cardBackground: "#f9fbfa"
    readonly property color borderColor: "#c8d9d0"
    readonly property color accentGreen: "#069a47"
    readonly property color accentPurple: "#c955e0"
    readonly property color accentCyan: "#44c7cf"
    readonly property color titleColor: "#2d2d2d"

    readonly property int pageMargin: Math.max(14, Math.round(width * 0.013))
    readonly property int columnGap: Math.max(12, Math.round(width * 0.010))
    readonly property int panelInset: Math.max(14, Math.round(width * 0.012))
    readonly property int sectionGap: Math.max(12, Math.round(height * 0.016))
    readonly property int headerHeightValue: Math.max(50, Math.round(height * 0.064))
    readonly property int footerHeightValue: Math.max(30, Math.round(height * 0.040))
    readonly property int leftPanelWidth: Math.max(255, Math.min(305, Math.round(width * 0.245)))
    readonly property int rightPanelWidth: Math.max(160, Math.min(210, Math.round(width * 0.160)))
    readonly property int heroFont: Math.max(30, Math.round(height * 0.048))
    readonly property int panelHeaderFont: Math.max(21, Math.round(height * 0.029))
    readonly property int majorSectionFont: Math.max(14, Math.round(height * 0.022))
    readonly property int bodyFont: Math.max(12, Math.round(height * 0.020))
    readonly property int smallFont: Math.max(11, Math.round(height * 0.017))
    readonly property int cardRadius: 4
    readonly property int chartHeight: Math.max(165, Math.round(height * 0.190))
    readonly property int sphereHeight: Math.max(210, Math.round(height * 0.330))
    readonly property int sourceRowHeight: Math.max(44, Math.round(height * 0.072))

    property var monitorRows: [
        { label: "CPU Usage", value: "26.1 %" },
        { label: "CPU Temp.", value: "-1.00 deg C" },
        { label: "Memory Usage", value: "82 %" },
        { label: "IP", value: "198.18.0.1" }
    ]

    function previewSourceRows() {
        const ids = appBridge.sourceIds
        const rows = []
        if (ids.length === 0) {
            for (let index = 0; index < 4; index += 1) {
                rows.push({
                    sourceId: -1,
                    label: "Source",
                    checked: false,
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
                label: "Source",
                checked: appBridge.isSourceSelected(sourceId),
                enabled: true,
                badge: index === 1 ? String(sourceId) : ""
            })
        }
        return rows
    }

    menuBar: MenuBar {
        Menu {
            title: "File"
        }
        Menu {
            title: "Edit"
        }
        Menu {
            title: "View"
        }
        Menu {
            title: "Window"
        }
        Menu {
            title: "Help"
        }
    }

    header: Rectangle {
        height: root.headerHeightValue
        color: root.accentGreen

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: root.pageMargin
            anchors.rightMargin: root.pageMargin
            spacing: Math.max(18, root.columnGap)

            Rectangle {
                Layout.preferredWidth: 26
                Layout.preferredHeight: 26
                radius: 3
                color: "transparent"
                border.color: "white"
                border.width: 2

                Repeater {
                    model: 4
                    delegate: Rectangle {
                        width: 6
                        height: 6
                        radius: 1
                        color: "white"
                        x: 4 + (index % 2) * 10
                        y: 4 + Math.floor(index / 2) * 10
                    }
                }
            }

            Label {
                text: "Temporal Studio"
                color: "white"
                font.pixelSize: root.heroFont
                font.bold: true
                Layout.alignment: Qt.AlignVCenter
            }

            Item {
                Layout.fillWidth: true
            }

            Repeater {
                model: ["Configure", "Record", "Camera"]
                delegate: Label {
                    text: modelData
                    color: "white"
                    font.pixelSize: Math.max(12, root.bodyFont + 1)
                    Layout.leftMargin: Math.max(14, root.columnGap)
                    Layout.alignment: Qt.AlignVCenter
                }
            }
        }
    }

    footer: Rectangle {
        height: root.footerHeightValue
        color: root.accentGreen

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

    Rectangle {
        anchors.fill: parent
        color: root.pageBackground

        RowLayout {
            anchors.fill: parent
            anchors.margins: root.pageMargin
            spacing: root.columnGap

            Rectangle {
                Layout.preferredWidth: root.leftPanelWidth
                Layout.fillHeight: true
                radius: root.cardRadius
                color: root.panelBackground

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.panelInset
                    spacing: root.sectionGap

                    Label {
                        text: "ODAS Data"
                        color: root.titleColor
                        font.pixelSize: Math.max(32, root.heroFont - 2)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(280, root.height * 0.375)
                        radius: root.cardRadius
                        color: root.cardBackground
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: Math.max(12, root.sectionGap - 2)

                            Label {
                                text: "Local System Monitor"
                                color: "#414141"
                                font.pixelSize: Math.max(14, root.bodyFont + 1)
                            }

                            Repeater {
                                model: root.monitorRows
                                delegate: Rectangle {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: Math.max(34, root.height * 0.045)
                                    radius: 3
                                    color: "#ffffff"
                                    border.color: "#ccd9d2"

                                    RowLayout {
                                        anchors.fill: parent
                                        spacing: 0

                                        Rectangle {
                                            Layout.fillHeight: true
                                            Layout.preferredWidth: Math.max(88, parent.width * 0.43)
                                            color: "#eef1ef"
                                            border.color: "transparent"
                                            radius: 3

                                            Label {
                                                anchors.verticalCenter: parent.verticalCenter
                                                anchors.left: parent.left
                                                anchors.leftMargin: 12
                                                text: modelData.label
                                                color: "#666666"
                                                font.pixelSize: root.bodyFont
                                            }
                                        }

                                        Item {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true

                                            Label {
                                                anchors.centerIn: parent
                                                text: modelData.value
                                                color: "#666666"
                                                font.pixelSize: root.bodyFont
                                            }
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
                        Layout.preferredHeight: Math.max(128, root.height * 0.178)
                        radius: root.cardRadius
                        color: root.cardBackground
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: Math.max(8, root.smallFont)

                            Label {
                                text: "ODAS Control"
                                color: "#414141"
                                font.pixelSize: Math.max(14, root.bodyFont + 1)
                            }

                            Label {
                                text: "ODAS Remote is connected"
                                color: "#4f5b56"
                                font.pixelSize: root.bodyFont
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
                color: "#ffffff"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Math.max(12, root.panelInset)
                    anchors.rightMargin: Math.max(10, root.panelInset - 2)
                    anchors.topMargin: Math.max(6, root.smallFont)
                    anchors.bottomMargin: Math.max(8, root.smallFont)
                    spacing: Math.max(8, root.smallFont)

                    Label {
                        text: "Source Elevation"
                        color: "#4a4a4a"
                        font.pixelSize: Math.max(16, root.majorSectionFont + 2)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartHeight
                        color: "#ffffff"
                        border.color: "#d9e1dd"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            anchors.topMargin: 6
                            anchors.bottomMargin: 6
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 6

                                ColumnLayout {
                                    Layout.preferredWidth: 32
                                    Layout.fillHeight: true
                                    spacing: 0

                                    Repeater {
                                        model: ["90", "60", "30", "0", "-30", "-60", "-90"]
                                        delegate: Label {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            text: modelData
                                            color: "#747b78"
                                            font.pixelSize: root.smallFont
                                            horizontalAlignment: Text.AlignRight
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }
                                }

                                Canvas {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    onPaint: {
                                        const ctx = getContext("2d")
                                        const w = width
                                        const h = height
                                        ctx.reset()
                                        ctx.fillStyle = "#ffffff"
                                        ctx.fillRect(0, 0, w, h)

                                        ctx.strokeStyle = "#d7dede"
                                        ctx.lineWidth = 1
                                        for (let row = 0; row <= 6; row += 1) {
                                            const y = row * h / 6
                                            ctx.beginPath()
                                            ctx.moveTo(0, y)
                                            ctx.lineTo(w, y)
                                            ctx.stroke()
                                        }
                                        for (let col = 0; col <= 8; col += 1) {
                                            const x = col * w / 8
                                            ctx.beginPath()
                                            ctx.moveTo(x, 0)
                                            ctx.lineTo(x, h)
                                            ctx.stroke()
                                        }

                                        function plot(points, color) {
                                            ctx.strokeStyle = color
                                            ctx.lineWidth = 2
                                            ctx.beginPath()
                                            for (let index = 0; index < points.length; index += 1) {
                                                const px = index * w / (points.length - 1)
                                                const py = h * (1 - points[index])
                                                if (index === 0) {
                                                    ctx.moveTo(px, py)
                                                } else {
                                                    ctx.lineTo(px, py)
                                                }
                                            }
                                            ctx.stroke()
                                        }

                                        plot([0.58, 0.57, 0.56, 0.54, 0.53, 0.52, 0.52, 0.52, 0.52], root.accentCyan)
                                        plot([0.42, 0.45, 0.50, 0.56, 0.61, 0.63, 0.62, 0.60, 0.59], root.accentPurple)
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6

                                Item {
                                    Layout.preferredWidth: 32
                                }

                                Repeater {
                                    model: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
                                    delegate: Label {
                                        Layout.fillWidth: true
                                        text: modelData
                                        color: "#747b78"
                                        font.pixelSize: root.smallFont
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                            }

                            Label {
                                Layout.fillWidth: true
                                text: "Sample"
                                color: "#6e7472"
                                font.pixelSize: root.smallFont
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }

                    Label {
                        text: "Source Azimut"
                        color: "#4a4a4a"
                        font.pixelSize: Math.max(16, root.majorSectionFont + 2)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartHeight
                        color: "#ffffff"
                        border.color: "#d9e1dd"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            anchors.topMargin: 6
                            anchors.bottomMargin: 6
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 6

                                ColumnLayout {
                                    Layout.preferredWidth: 32
                                    Layout.fillHeight: true
                                    spacing: 0

                                    Repeater {
                                        model: ["180", "120", "60", "0", "-60", "-120", "-180"]
                                        delegate: Label {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            text: modelData
                                            color: "#747b78"
                                            font.pixelSize: root.smallFont
                                            horizontalAlignment: Text.AlignRight
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }
                                }

                                Canvas {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    onPaint: {
                                        const ctx = getContext("2d")
                                        const w = width
                                        const h = height
                                        ctx.reset()
                                        ctx.fillStyle = "#ffffff"
                                        ctx.fillRect(0, 0, w, h)

                                        ctx.strokeStyle = "#d7dede"
                                        ctx.lineWidth = 1
                                        for (let row = 0; row <= 6; row += 1) {
                                            const y = row * h / 6
                                            ctx.beginPath()
                                            ctx.moveTo(0, y)
                                            ctx.lineTo(w, y)
                                            ctx.stroke()
                                        }
                                        for (let col = 0; col <= 8; col += 1) {
                                            const x = col * w / 8
                                            ctx.beginPath()
                                            ctx.moveTo(x, 0)
                                            ctx.lineTo(x, h)
                                            ctx.stroke()
                                        }

                                        function plot(points, color) {
                                            ctx.strokeStyle = color
                                            ctx.lineWidth = 2
                                            ctx.beginPath()
                                            for (let index = 0; index < points.length; index += 1) {
                                                const px = index * w / (points.length - 1)
                                                const py = h * (1 - points[index])
                                                if (index === 0) {
                                                    ctx.moveTo(px, py)
                                                } else {
                                                    ctx.lineTo(px, py)
                                                }
                                            }
                                            ctx.stroke()
                                        }

                                        plot([0.10, 0.10, 0.11, 0.11, 0.12, 0.12, 0.12, 0.12, 0.12], root.accentCyan)
                                        plot([0.72, 0.72, 0.73, 0.71, 0.69, 0.66, 0.63, 0.64, 0.68], root.accentPurple)
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6

                                Item {
                                    Layout.preferredWidth: 32
                                }

                                Repeater {
                                    model: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
                                    delegate: Label {
                                        Layout.fillWidth: true
                                        text: modelData
                                        color: "#747b78"
                                        font.pixelSize: root.smallFont
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                            }

                            Label {
                                Layout.fillWidth: true
                                text: "Sample"
                                color: "#6e7472"
                                font.pixelSize: root.smallFont
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }

                    Label {
                        text: "Active sources locations"
                        color: "#4a4a4a"
                        font.pixelSize: Math.max(16, root.majorSectionFont + 2)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: root.sphereHeight
                        color: "#ffffff"
                        border.color: "#ffffff"

                        Canvas {
                            anchors.fill: parent
                            anchors.margins: 6

                            onPaint: {
                                const ctx = getContext("2d")
                                const w = width
                                const h = height
                                const cx = w * 0.51
                                const cy = h * 0.53
                                const radius = Math.min(w, h) * 0.34

                                ctx.reset()
                                ctx.fillStyle = "#ffffff"
                                ctx.fillRect(0, 0, w, h)

                                ctx.strokeStyle = "#4d63ff"
                                ctx.lineWidth = 1.3
                                for (let index = -3; index <= 3; index += 1) {
                                    const scale = 1 - Math.abs(index) * 0.12
                                    ctx.beginPath()
                                    ctx.ellipse(cx, cy, radius, radius * scale, 0, 0, Math.PI * 2)
                                    ctx.stroke()
                                }
                                for (let index = 0; index < 10; index += 1) {
                                    const angle = index * Math.PI / 10
                                    ctx.beginPath()
                                    ctx.ellipse(cx, cy, radius * Math.cos(angle), radius, 0, 0, Math.PI * 2)
                                    ctx.stroke()
                                }

                                ctx.fillStyle = "rgba(125, 173, 96, 0.45)"
                                ctx.beginPath()
                                ctx.ellipse(cx, cy + radius * 0.18, radius * 0.95, radius * 0.38, 0, 0, Math.PI * 2)
                                ctx.fill()

                                ctx.strokeStyle = "#a06a37"
                                for (let index = 0; index < 6; index += 1) {
                                    const ry = radius * (0.20 + index * 0.08)
                                    ctx.beginPath()
                                    ctx.ellipse(cx, cy + radius * 0.35, radius * 0.70, ry * 0.38, 0, 0, Math.PI * 2)
                                    ctx.stroke()
                                }

                                ctx.fillStyle = "#111111"
                                ctx.fillRect(cx - 26, cy - 10, 52, 24)
                                ctx.fillRect(cx - 12, cy - 18, 24, 36)

                                ctx.fillStyle = root.accentPurple
                                ctx.beginPath()
                                ctx.arc(cx - radius * 0.55, cy - radius * 0.64, 7, 0, Math.PI * 2)
                                ctx.fill()

                                ctx.strokeStyle = "#2d4cff"
                                ctx.beginPath()
                                ctx.moveTo(cx, cy - radius * 1.25)
                                ctx.lineTo(cx, cy + radius * 1.10)
                                ctx.stroke()

                                ctx.strokeStyle = "#ff5d2a"
                                ctx.beginPath()
                                ctx.moveTo(40, h - 32)
                                ctx.lineTo(66, h - 32)
                                ctx.stroke()
                                ctx.strokeStyle = "#2d4cff"
                                ctx.beginPath()
                                ctx.moveTo(40, h - 32)
                                ctx.lineTo(40, h - 58)
                                ctx.stroke()

                                ctx.fillStyle = "#2d4cff"
                                ctx.font = "12px sans-serif"
                                ctx.fillText("Z", 36, h - 60)
                                ctx.fillStyle = "#ff5d2a"
                                ctx.fillText("X", 68, h - 30)
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: root.rightPanelWidth
                Layout.fillHeight: true
                radius: root.cardRadius
                color: root.panelBackground

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: root.panelInset
                    anchors.rightMargin: root.panelInset
                    anchors.topMargin: Math.max(10, root.panelInset + 2)
                    anchors.bottomMargin: root.panelInset
                    spacing: Math.max(10, root.sectionGap - 1)

                    Label {
                        text: "Sources"
                        color: root.titleColor
                        font.pixelSize: root.panelHeaderFont
                    }

                    Repeater {
                        model: root.previewSourceRows()
                        delegate: ColumnLayout {
                            required property var modelData
                            Layout.fillWidth: true
                            spacing: 8

                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.sourceRowHeight

                                CheckBox {
                                    enabled: modelData.enabled
                                    checked: modelData.checked
                                    opacity: modelData.enabled ? 1.0 : 0.55
                                    onToggled: {
                                        if (modelData.enabled) {
                                            appBridge.setSourceSelected(modelData.sourceId, checked)
                                        }
                                    }
                                }

                                Label {
                                    text: modelData.label
                                    color: modelData.enabled ? "#505854" : "#7d8783"
                                    font.pixelSize: root.bodyFont
                                }

                                Rectangle {
                                    visible: modelData.badge !== ""
                                    radius: height / 2
                                    color: root.accentPurple
                                    Layout.preferredHeight: 20
                                    Layout.preferredWidth: Math.max(24, badgeLabel.implicitWidth + 12)

                                    Label {
                                        id: badgeLabel
                                        anchors.centerIn: parent
                                        text: modelData.badge
                                        color: "white"
                                        font.pixelSize: root.smallFont
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
                                color: "#cbd9d3"
                            }
                        }
                    }

                    Item {
                        Layout.preferredHeight: 16
                    }

                    Label {
                        text: "Filters"
                        color: root.titleColor
                        font.pixelSize: root.panelHeaderFont
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#cbd9d3"
                    }

                    CheckBox {
                        text: "Sources"
                        checked: appBridge.sourcesEnabled
                        font.pixelSize: root.bodyFont
                        onToggled: appBridge.setSourcesEnabled(checked)
                    }

                    CheckBox {
                        text: "Potentials"
                        checked: appBridge.potentialsEnabled
                        font.pixelSize: root.bodyFont
                        onToggled: appBridge.setPotentialsEnabled(checked)
                    }

                    Item {
                        Layout.preferredHeight: 18
                    }

                    Label {
                        text: "Potential sources\nenergy range:"
                        color: "#54625d"
                        font.pixelSize: root.bodyFont
                    }

                    Label {
                        text: appBridge.potentialEnergyMin.toFixed(0) + "\n" + appBridge.potentialEnergyMax.toFixed(0)
                        color: "#454d49"
                        font.pixelSize: root.bodyFont
                    }

                    RangeSlider {
                        Layout.fillWidth: true
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
                            radius: 2
                            color: "#1b92d5"
                        }

                        second.handle: Rectangle {
                            x: parent.leftPadding + parent.second.visualPosition * (parent.availableWidth - width)
                            y: parent.topPadding + parent.availableHeight / 2 - height / 2
                            implicitWidth: 16
                            implicitHeight: 22
                            radius: 2
                            color: "#1b92d5"
                        }
                    }

                    Item {
                        Layout.fillHeight: true
                    }
                }
            }
        }
    }
}
