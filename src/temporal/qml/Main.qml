// qmllint disable unqualified
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts
import QtQuick3D

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
    readonly property int brandHeight: Math.max(46, Math.round(height * 0.064))
    readonly property int footerHeightValue: Math.max(28, Math.round(height * 0.040))
    readonly property int pageMargin: Math.max(14, Math.round(width * 0.013))
    readonly property int columnGap: Math.max(12, Math.round(width * 0.010))
    readonly property int panelInset: Math.max(14, Math.round(width * 0.012))
    readonly property int sectionGap: Math.max(12, Math.round(height * 0.016))
    readonly property int leftPanelWidth: Math.max(255, Math.min(305, Math.round(width * 0.245)))
    readonly property int rightPanelWidth: Math.max(170, Math.min(210, Math.round(width * 0.160)))
    readonly property int brandFont: Math.max(22, Math.round(height * 0.040))
    readonly property int sideTitleFont: Math.max(17, Math.round(height * 0.031))
    readonly property int sectionTitleFont: Math.max(14, Math.round(height * 0.024))
    readonly property int bodyFont: Math.max(12, Math.round(height * 0.019))
    readonly property int smallFont: Math.max(11, Math.round(height * 0.017))
    readonly property int codeFont: Math.max(11, Math.round(height * 0.016))
    readonly property int chartHeight: Math.max(165, Math.round(height * 0.194))
    readonly property int sphereHeight: Math.max(228, Math.round(height * 0.340))
    readonly property real sphereRadius: 118

    property real sphereYaw: -18
    property real spherePitch: 14
    property var latitudeAngles: [-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75]
    property var longitudeAngles: [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345]

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

    function spherePreviewSources() {
        if (appBridge.sourcePositions.length > 0) {
            return appBridge.sourcePositions
        }
        return [{ id: 15, x: -0.42, y: 0.14, z: 0.60 }]
    }

    component ActionButton: Basic.Button {
        id: control
        implicitHeight: 32
        implicitWidth: 84
        font.pixelSize: root.bodyFont
        padding: 0

        contentItem: Text {
            text: control.text
            color: control.enabled ? "#2f3a36" : "#89948f"
            font.pixelSize: root.bodyFont
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        background: Rectangle {
            radius: 3
            color: control.pressed ? "#d8e4de" : "#f7faf8"
            border.color: control.enabled ? "#b9cbc2" : "#d7dfdb"
        }
    }

    component SideCheckBox: Basic.CheckBox {
        id: control
        spacing: 8

        indicator: Rectangle {
            implicitWidth: 13
            implicitHeight: 13
            radius: 2
            border.color: "#7f8a85"
            color: "#ffffff"
            opacity: control.enabled ? 1.0 : 0.55

            Rectangle {
                anchors.centerIn: parent
                width: 7
                height: 7
                radius: 1
                color: "#6e7773"
                visible: control.checked
            }
        }

        contentItem: Text {
            text: control.text
            color: control.enabled ? "#4f5854" : "#7a8480"
            font.pixelSize: root.bodyFont
            verticalAlignment: Text.AlignVCenter
        }
    }

    component ChartCanvas: Canvas {
        property var yTicks: []
        property var xTicks: []
        property var firstSeries: []
        property var secondSeries: []
        property color firstColor: root.accentCyan
        property color secondColor: root.accentPurple
        property string xAxisLabel: "样本"

        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()

        onPaint: {
            const ctx = getContext("2d")
            const w = width
            const h = height
            const leftPad = 44
            const rightPad = 10
            const topPad = 8
            const bottomPad = 34
            const plotW = w - leftPad - rightPad
            const plotH = h - topPad - bottomPad

            ctx.reset()
            ctx.fillStyle = "#ffffff"
            ctx.fillRect(0, 0, w, h)
            ctx.font = "12px sans-serif"
            ctx.textBaseline = "middle"
            ctx.textAlign = "left"

            ctx.strokeStyle = "#d7dede"
            ctx.lineWidth = 1
            for (let row = 0; row <= 6; row += 1) {
                const y = topPad + row * plotH / 6
                ctx.beginPath()
                ctx.moveTo(leftPad, y)
                ctx.lineTo(leftPad + plotW, y)
                ctx.stroke()
            }
            for (let col = 0; col <= 8; col += 1) {
                const x = leftPad + col * plotW / 8
                ctx.beginPath()
                ctx.moveTo(x, topPad)
                ctx.lineTo(x, topPad + plotH)
                ctx.stroke()
            }

            ctx.fillStyle = "#747b78"
            for (let index = 0; index < yTicks.length; index += 1) {
                const y = topPad + index * plotH / Math.max(1, yTicks.length - 1)
                ctx.fillText(String(yTicks[index]), 8, y)
            }

            ctx.textAlign = "center"
            for (let index = 0; index < xTicks.length; index += 1) {
                const x = leftPad + index * plotW / Math.max(1, xTicks.length - 1)
                ctx.fillText(String(xTicks[index]), x, topPad + plotH + 16)
            }
            ctx.fillText(xAxisLabel, leftPad + plotW / 2, h - 4)

            function plot(points, color) {
                if (points.length === 0) {
                    return
                }
                ctx.strokeStyle = color
                ctx.lineWidth = 2
                ctx.beginPath()
                for (let index = 0; index < points.length; index += 1) {
                    const px = leftPad + index * plotW / Math.max(1, points.length - 1)
                    const py = topPad + plotH * (1 - points[index])
                    if (index === 0) {
                        ctx.moveTo(px, py)
                    } else {
                        ctx.lineTo(px, py)
                    }
                }
                ctx.stroke()
            }

            plot(firstSeries, firstColor)
            plot(secondSeries, secondColor)
        }
    }

    header: Column {
        width: root.width
        spacing: 0

        Rectangle {
            width: parent.width
            height: root.menuHeight
            color: "#ffffff"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 6
                spacing: 16

                Repeater {
                    model: ["文件", "编辑", "视图", "窗口", "帮助"]
                    delegate: Label {
                        text: modelData
                        color: "#111111"
                        font.pixelSize: root.smallFont + 1
                        Layout.alignment: Qt.AlignVCenter
                    }
                }

                Item {
                    Layout.fillWidth: true
                }
            }
        }

        Rectangle {
            width: parent.width
            height: root.brandHeight
            color: root.accentGreen

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: root.pageMargin
                anchors.rightMargin: root.pageMargin
                spacing: Math.max(14, root.columnGap)

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
                    font.pixelSize: root.brandFont
                    font.bold: true
                    Layout.alignment: Qt.AlignVCenter
                }

                Item {
                    Layout.fillWidth: true
                }

                Repeater {
                    model: ["配置", "录制", "相机"]
                    delegate: Label {
                        text: modelData
                        color: "white"
                        font.pixelSize: root.bodyFont + 1
                        Layout.leftMargin: Math.max(12, root.columnGap)
                        Layout.alignment: Qt.AlignVCenter
                    }
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
                text: "ODAS 图形界面客户端"
                color: "white"
                font.pixelSize: root.bodyFont
            }

            Item {
                Layout.fillWidth: true
            }

            Label {
                text: "法律声明"
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
                radius: 4
                color: root.panelBackground

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.panelInset
                    spacing: root.sectionGap

                    Label {
                        text: "ODAS 数据"
                        color: root.titleColor
                        font.pixelSize: Math.max(30, root.sideTitleFont + 8)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(300, root.height * 0.405)
                        radius: 4
                        color: root.cardBackground
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: Math.max(10, root.smallFont)

                            Label {
                                text: "远程 odaslive 日志"
                                color: "#414141"
                                font.pixelSize: root.sectionTitleFont
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: 3
                                color: "#ffffff"
                                border.color: "#d1ddd7"

                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    clip: true

                                    TextArea {
                                        width: parent.width
                                        readOnly: true
                                        wrapMode: TextArea.NoWrap
                                        selectByMouse: true
                                        text: appBridge.remoteLogLines.join("\n")
                                        color: "#2e3532"
                                        font.family: "Consolas"
                                        font.pixelSize: root.codeFont
                                        padding: 0
                                        background: null
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(168, root.height * 0.220)
                        radius: 4
                        color: root.cardBackground
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: root.panelInset
                            spacing: 8

                            Label {
                                text: "ODAS 控制"
                                color: "#414141"
                                font.pixelSize: root.sectionTitleFont
                            }

                            Label {
                                text: appBridge.status
                                color: root.mutedText
                                font.pixelSize: root.bodyFont
                                wrapMode: Text.WordWrap
                            }

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 8
                                rowSpacing: 8

                                ActionButton {
                                    text: "连接"
                                    Layout.fillWidth: true
                                    onClicked: appBridge.connectRemote()
                                }

                                ActionButton {
                                    text: "启动"
                                    Layout.fillWidth: true
                                    onClicked: appBridge.startRemoteOdas()
                                }

                                ActionButton {
                                    text: "停止"
                                    Layout.fillWidth: true
                                    onClicked: appBridge.stopRemoteOdas()
                                }

                                ActionButton {
                                    text: "监听"
                                    Layout.fillWidth: true
                                    onClicked: appBridge.startStreams()
                                }

                                ActionButton {
                                    text: "关闭流"
                                    Layout.fillWidth: true
                                    Layout.columnSpan: 2
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
                        text: "声源俯仰角"
                        color: "#4a4a4a"
                        font.pixelSize: root.sideTitleFont
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartHeight
                        color: "#ffffff"
                        border.color: "#d9e1dd"

                        ChartCanvas {
                            anchors.fill: parent
                            anchors.margins: 6
                            yTicks: ["90", "60", "30", "0", "-30", "-60", "-90"]
                            xTicks: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
                            firstSeries: [0.58, 0.57, 0.56, 0.54, 0.53, 0.52, 0.52, 0.52, 0.52]
                            secondSeries: [0.42, 0.45, 0.50, 0.56, 0.61, 0.63, 0.62, 0.60, 0.59]
                        }
                    }

                    Label {
                        text: "声源方位角"
                        color: "#4a4a4a"
                        font.pixelSize: root.sideTitleFont
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.chartHeight
                        color: "#ffffff"
                        border.color: "#d9e1dd"

                        ChartCanvas {
                            anchors.fill: parent
                            anchors.margins: 6
                            yTicks: ["180", "120", "60", "0", "-60", "-120", "-180"]
                            xTicks: ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]
                            firstSeries: [0.10, 0.10, 0.11, 0.11, 0.12, 0.12, 0.12, 0.12, 0.12]
                            secondSeries: [0.72, 0.72, 0.73, 0.71, 0.69, 0.66, 0.63, 0.64, 0.68]
                        }
                    }

                    Label {
                        text: "活跃声源位置"
                        color: "#4a4a4a"
                        font.pixelSize: root.sideTitleFont
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: root.sphereHeight
                        color: "#ffffff"
                        border.color: "#ffffff"

                        View3D {
                            id: sphereView
                            anchors.fill: parent
                            anchors.margins: 6
                            renderMode: View3D.Offscreen
                            camera: sphereCamera

                            environment: SceneEnvironment {
                                backgroundMode: SceneEnvironment.Color
                                clearColor: "#ffffff"
                                antialiasingMode: SceneEnvironment.MSAA
                                antialiasingQuality: SceneEnvironment.VeryHigh
                            }

                            PerspectiveCamera {
                                id: sphereCamera
                                position: Qt.vector3d(0, 0, 520)
                                clipFar: 2000
                            }

                            DirectionalLight {
                                eulerRotation: Qt.vector3d(-30, 35, 0)
                                brightness: 0.8
                            }

                            Node {
                                id: globeRoot
                                eulerRotation: Qt.vector3d(root.spherePitch, root.sphereYaw, 0)

                                Model {
                                    source: "#Sphere"
                                    scale: Qt.vector3d(2.15, 0.10, 2.15)
                                    position: Qt.vector3d(0, -18, 0)
                                    materials: DefaultMaterial {
                                        diffuseColor: Qt.rgba(0.49, 0.68, 0.39, 0.50)
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Model {
                                    source: "#Sphere"
                                    scale: Qt.vector3d(1.95, 0.06, 1.95)
                                    position: Qt.vector3d(0, -54, 0)
                                    materials: DefaultMaterial {
                                        diffuseColor: Qt.rgba(0.66, 0.42, 0.24, 0.40)
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Model {
                                    source: "#Cylinder"
                                    scale: Qt.vector3d(0.018, 2.45, 0.018)
                                    position: Qt.vector3d(0, 0, 0)
                                    materials: DefaultMaterial {
                                        diffuseColor: "#3f5fff"
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Model {
                                    source: "#Cylinder"
                                    scale: Qt.vector3d(0.018, 1.35, 0.018)
                                    position: Qt.vector3d(68, 0, 0)
                                    eulerRotation: Qt.vector3d(0, 0, 90)
                                    materials: DefaultMaterial {
                                        diffuseColor: "#ff6a2d"
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Model {
                                    source: "#Cube"
                                    scale: Qt.vector3d(0.36, 0.22, 0.26)
                                    materials: DefaultMaterial {
                                        diffuseColor: "#111111"
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Model {
                                    source: "#Cube"
                                    scale: Qt.vector3d(0.18, 0.34, 0.18)
                                    materials: DefaultMaterial {
                                        diffuseColor: "#111111"
                                        lighting: DefaultMaterial.NoLighting
                                    }
                                }

                                Repeater3D {
                                    model: root.latitudeAngles.length * root.longitudeAngles.length

                                    delegate: Model {
                                        property int latIndex: Math.floor(index / root.longitudeAngles.length)
                                        property int lonIndex: index % root.longitudeAngles.length
                                        property real latRad: root.latitudeAngles[latIndex] * Math.PI / 180
                                        property real lonRad: root.longitudeAngles[lonIndex] * Math.PI / 180

                                        source: "#Sphere"
                                        position: Qt.vector3d(
                                            root.sphereRadius * Math.cos(latRad) * Math.cos(lonRad),
                                            root.sphereRadius * Math.sin(latRad),
                                            root.sphereRadius * Math.cos(latRad) * Math.sin(lonRad)
                                        )
                                        scale: Qt.vector3d(0.012, 0.012, 0.012)
                                        materials: DefaultMaterial {
                                            diffuseColor: "#5b6fff"
                                            lighting: DefaultMaterial.NoLighting
                                        }
                                    }
                                }

                                Repeater3D {
                                    model: root.spherePreviewSources()

                                    delegate: Model {
                                        required property var modelData
                                        source: "#Sphere"
                                        position: Qt.vector3d(
                                            modelData.x * root.sphereRadius,
                                            -modelData.z * root.sphereRadius,
                                            modelData.y * root.sphereRadius
                                        )
                                        scale: Qt.vector3d(0.055, 0.055, 0.055)
                                        materials: DefaultMaterial {
                                            diffuseColor: root.accentPurple
                                            lighting: DefaultMaterial.NoLighting
                                        }
                                    }
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.LeftButton
                            cursorShape: Qt.OpenHandCursor
                            property real lastX: 0
                            property real lastY: 0

                            onPressed: {
                                cursorShape = Qt.ClosedHandCursor
                                lastX = mouse.x
                                lastY = mouse.y
                            }

                            onReleased: cursorShape = Qt.OpenHandCursor

                            onPositionChanged: {
                                if (!(mouse.buttons & Qt.LeftButton)) {
                                    return
                                }
                                root.sphereYaw += (mouse.x - lastX) * 0.45
                                root.spherePitch = Math.max(-80, Math.min(80, root.spherePitch + (mouse.y - lastY) * 0.35))
                                lastX = mouse.x
                                lastY = mouse.y
                            }
                        }

                        Item {
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.leftMargin: 18
                            anchors.bottomMargin: 16
                            width: 54
                            height: 42

                            Rectangle {
                                x: 12
                                y: 26
                                width: 22
                                height: 2
                                color: "#ff6a2d"
                            }

                            Rectangle {
                                x: 12
                                y: 6
                                width: 2
                                height: 22
                                color: "#3f5fff"
                            }

                            Label {
                                x: 10
                                y: 0
                                text: "Z"
                                color: "#3f5fff"
                                font.pixelSize: root.smallFont
                            }

                            Label {
                                x: 36
                                y: 22
                                text: "X"
                                color: "#ff6a2d"
                                font.pixelSize: root.smallFont
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.preferredWidth: root.rightPanelWidth
                Layout.fillHeight: true
                radius: 4
                color: root.panelBackground

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: root.panelInset
                    anchors.rightMargin: root.panelInset
                    anchors.topMargin: Math.max(10, root.panelInset + 2)
                    anchors.bottomMargin: root.panelInset
                    spacing: Math.max(10, root.sectionGap - 1)

                    Label {
                        text: "声源"
                        color: root.titleColor
                        font.pixelSize: Math.max(26, root.sideTitleFont + 3)
                    }

                    Repeater {
                        model: root.sourceRows()

                        delegate: ColumnLayout {
                            required property var modelData
                            Layout.fillWidth: true
                            spacing: 8

                            RowLayout {
                                Layout.fillWidth: true

                                SideCheckBox {
                                    checked: modelData.checked
                                    enabled: modelData.enabled
                                    text: modelData.label
                                    onToggled: {
                                        if (modelData.enabled) {
                                            appBridge.setSourceSelected(modelData.sourceId, checked)
                                        }
                                    }
                                }

                                Rectangle {
                                    visible: modelData.badge !== ""
                                    radius: height / 2
                                    color: root.accentPurple
                                    Layout.preferredHeight: 20
                                    Layout.preferredWidth: Math.max(24, badgeText.implicitWidth + 12)

                                    Label {
                                        id: badgeText
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
                                color: "#c9d9d2"
                            }
                        }
                    }

                    Item {
                        Layout.preferredHeight: 18
                    }

                    Label {
                        text: "筛选器"
                        color: root.titleColor
                        font.pixelSize: Math.max(26, root.sideTitleFont + 3)
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#c9d9d2"
                    }

                    SideCheckBox {
                        text: "声源"
                        checked: appBridge.sourcesEnabled
                        onToggled: appBridge.setSourcesEnabled(checked)
                    }

                    SideCheckBox {
                        text: "候选点"
                        checked: appBridge.potentialsEnabled
                        onToggled: appBridge.setPotentialsEnabled(checked)
                    }

                    Item {
                        Layout.preferredHeight: 16
                    }

                    Label {
                        text: "候选声源\n能量范围:"
                        color: "#55635d"
                        font.pixelSize: root.bodyFont
                    }

                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 72

                        Label {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            text: appBridge.potentialEnergyMin.toFixed(0)
                            color: "#3f4743"
                            font.pixelSize: root.bodyFont
                        }

                        Basic.RangeSlider {
                            id: energySlider
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.topMargin: 22
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
                                radius: 4
                                color: "#1b92d5"
                            }

                            second.handle: Rectangle {
                                x: parent.leftPadding + parent.second.visualPosition * (parent.availableWidth - width)
                                y: parent.topPadding + parent.availableHeight / 2 - height / 2
                                implicitWidth: 16
                                implicitHeight: 22
                                radius: 4
                                color: "#1b92d5"
                            }
                        }

                        Label {
                            anchors.left: parent.left
                            anchors.top: energySlider.bottom
                            anchors.topMargin: 4
                            text: appBridge.potentialEnergyMax.toFixed(0)
                            color: "#3f4743"
                            font.pixelSize: root.bodyFont
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
