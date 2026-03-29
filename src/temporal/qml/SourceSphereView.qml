import QtQuick
import QtQuick3D

Rectangle {
    id: root

    required property QtObject theme
    property var sourcePositionsModel: null
    property int sourceModelRevision: 0

    color: "#ffffff"
    border.color: "transparent"
    clip: true

    property real sphereYaw: 0
    property real spherePitch: 0
    property real sphereRadius: 150
    property int latitudeBandCount: 3
    property int meridianBandCount: 12
    property int diagonalBandCount: 6
    readonly property var latitudeAngles: buildLatitudeAngles()
    readonly property var meridianAngles: buildMeridianAngles()
    readonly property var diagonalAngles: buildDiagonalAngles()
    property int ringSegments: 44
    property real diagonalTilt: 52
    readonly property real gridLineOpacity: 0.76
    readonly property real equatorDiskOpacity: 0.34
    readonly property real sourceMarkerOpacity: 0.88
    readonly property real primitiveRadius: 50
    readonly property real primitiveHeight: 100
    readonly property real equatorRadius: sphereRadius
    readonly property real equatorDiskScale: equatorRadius / primitiveRadius
    readonly property real equatorDiskThicknessScale: 0.040
    readonly property real coreCylinderRadiusScale: (sphereRadius * 0.115) / primitiveRadius
    readonly property real coreCylinderHeightScale: (sphereRadius * 0.22) / primitiveHeight
    readonly property real coreCubeWidthScale: (sphereRadius * 0.36) / primitiveHeight
    readonly property real coreCubeHeightScale: (sphereRadius * 0.18) / primitiveHeight
    readonly property real coreCubeDepthScale: (sphereRadius * 0.24) / primitiveHeight
    readonly property real axisRadiusScale: 0.016
    readonly property real axisLengthScale: (sphereRadius * 2.22) / primitiveHeight
    readonly property real sourceMarkerScale: sphereRadius / 1425
    readonly property real sourceHighlightScale: sphereRadius / 3570
    readonly property real sourceHighlightOffset: sphereRadius / 500
    readonly property real cameraDistance: Math.max(sphereRadius * 4.55, sphereRadius * 4.05 + Math.max(0, 320 - sphereView.height) * 0.42)
    readonly property real sceneCenterYOffset: -Math.min(28, Math.max(12, sphereRadius * 0.10 + Math.max(0, 300 - sphereView.height) * 0.06))
    readonly property var visibleSources: normalizedSourceEntries()

    function colorForSource(sourceId) {
        const palette = [theme.accentPurple, theme.accentCyan, "#ff9c47", "#5ac97c", "#6a88ff", "#f16f7d"]
        const base = Math.abs(Number(sourceId) || 0)
        return palette[base % palette.length]
    }

    function normalizedSourceEntries() {
        const revision = sourceModelRevision
        const entries = []
        const model = sourcePositionsModel
        const count = model && typeof model.count === "number" ? model.count : 0
        for (let index = 0; index < count; index += 1) {
            const item = model.get(index)
            if (!item) {
                continue
            }

            const x = Number(item.x)
            const y = Number(item.y)
            const z = Number(item.z)
            if (!isFinite(x) || !isFinite(y) || !isFinite(z)) {
                continue
            }

            const sourceId = Number(item.id) || index + 1
            const length = Math.sqrt(x * x + y * y + z * z)
            const scale = length > 1 ? 1 / length : 1
            entries.push({
                id: sourceId,
                color: item.color || colorForSource(sourceId),
                x: x * scale,
                y: y * scale,
                z: z * scale,
                revision: revision
            })
        }

        return entries
    }

    function buildLatitudeAngles() {
        const angles = []
        const step = 90 / (latitudeBandCount + 1)
        for (let index = latitudeBandCount; index >= 1; index -= 1) {
            angles.push(-step * index)
        }
        angles.push(0)
        for (let index = 1; index <= latitudeBandCount; index += 1) {
            angles.push(step * index)
        }
        return angles
    }

    function buildMeridianAngles() {
        const angles = []
        const step = 180 / meridianBandCount
        for (let index = 0; index < meridianBandCount; index += 1) {
            angles.push(index * step)
        }
        return angles
    }

    function buildDiagonalAngles() {
        const angles = []
        const step = 180 / diagonalBandCount
        for (let index = 0; index < diagonalBandCount; index += 1) {
            angles.push(index * step + step / 2)
        }
        return angles
    }

    function rotateVector(vector) {
        const pitchRad = spherePitch * Math.PI / 180
        const yawRad = sphereYaw * Math.PI / 180
        const cosPitch = Math.cos(pitchRad)
        const sinPitch = Math.sin(pitchRad)
        const cosYaw = Math.cos(yawRad)
        const sinYaw = Math.sin(yawRad)

        const yawedX = vector.x * cosYaw + vector.z * sinYaw
        const yawedZ = -vector.x * sinYaw + vector.z * cosYaw
        const pitchedY = vector.y * cosPitch - yawedZ * sinPitch
        const pitchedZ = vector.y * sinPitch + yawedZ * cosPitch

        return {
            x: yawedX,
            y: pitchedY,
            z: pitchedZ
        }
    }

    function sourcePositionVector(entry) {
        return Qt.vector3d(entry.x * sphereRadius, entry.z * sphereRadius, entry.y * sphereRadius)
    }

    function clampPitch(value) {
        return Math.max(-70, Math.min(70, value))
    }

    function applyDragDelta(deltaX, deltaY) {
        root.sphereYaw += deltaX * 0.42
        root.spherePitch = clampPitch(root.spherePitch + deltaY * 0.30)
    }

    function previewPitchAfterDrag(startYaw, startPitch, deltaY) {
        const previousYaw = root.sphereYaw
        const previousPitch = root.spherePitch
        root.sphereYaw = startYaw
        root.spherePitch = startPitch
        applyDragDelta(0, deltaY)
        const result = root.spherePitch
        root.sphereYaw = previousYaw
        root.spherePitch = previousPitch

        return result
    }

    function axisEndpoint(vector, scale) {
        const rotated = rotateVector(vector)
        return Qt.point(axisOverlay.originX + rotated.x * scale, axisOverlay.originY - rotated.y * scale)
    }

    function labelAnchor(point) {
        const rawX = point.x + (point.x >= axisOverlay.originX ? 6 : -12)
        const rawY = point.y + (point.y <= axisOverlay.originY ? -6 : 16)
        return Qt.point(Math.max(10, Math.min(axisOverlay.width - 10, rawX)), Math.max(10, Math.min(axisOverlay.height - 10, rawY)))
    }

    Connections {
        target: root.sourcePositionsModel

        function onModelReset() {
            root.sourceModelRevision += 1
            axisOverlay.requestPaint()
        }

        function onRowsInserted() {
            root.sourceModelRevision += 1
            axisOverlay.requestPaint()
        }

        function onRowsRemoved() {
            root.sourceModelRevision += 1
            axisOverlay.requestPaint()
        }

        function onDataChanged() {
            root.sourceModelRevision += 1
            axisOverlay.requestPaint()
        }
    }

    onSphereYawChanged: axisOverlay.requestPaint()
    onSpherePitchChanged: axisOverlay.requestPaint()
    onVisibleSourcesChanged: axisOverlay.requestPaint()

    View3D {
        id: sphereView
        anchors.fill: parent
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        anchors.topMargin: 6
        anchors.bottomMargin: 18
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
            position: Qt.vector3d(0, 12, root.cameraDistance)
            clipFar: 2400
            fieldOfView: 32
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, 32, 0)
            brightness: 1.0
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(44, -38, 0)
            brightness: 0.30
        }

        Node {
            id: sceneFrame
            y: root.sceneCenterYOffset

            Node {
                id: pitchRoot
                eulerRotation.x: root.spherePitch

                Node {
                    id: yawRoot
                    eulerRotation.y: root.sphereYaw

                    Model {
                        source: "#Cylinder"
                        scale: Qt.vector3d(root.equatorDiskScale, root.equatorDiskThicknessScale, root.equatorDiskScale)
                        materials: DefaultMaterial {
                            diffuseColor: Qt.rgba(0.52, 0.69, 0.42, 0.56)
                            lighting: DefaultMaterial.NoLighting
                            opacity: root.equatorDiskOpacity
                            depthDrawMode: Material.NeverDepthDraw
                        }
                    }

                    Model {
                        source: "#Cylinder"
                        scale: Qt.vector3d(root.coreCylinderRadiusScale, root.coreCylinderHeightScale, root.coreCylinderRadiusScale)
                        materials: DefaultMaterial {
                            diffuseColor: "#111111"
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Model {
                        source: "#Cube"
                        scale: Qt.vector3d(root.coreCubeWidthScale, root.coreCubeHeightScale, root.coreCubeDepthScale)
                        materials: DefaultMaterial {
                            diffuseColor: "#111111"
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Model {
                        source: "#Cylinder"
                        scale: Qt.vector3d(root.axisRadiusScale, root.axisLengthScale, root.axisRadiusScale)
                        eulerRotation: Qt.vector3d(0, 0, 90)
                        materials: DefaultMaterial {
                            diffuseColor: root.theme.axisOrange
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Model {
                        source: "#Cylinder"
                        scale: Qt.vector3d(root.axisRadiusScale, root.axisLengthScale, root.axisRadiusScale)
                        eulerRotation: Qt.vector3d(90, 0, 0)
                        materials: DefaultMaterial {
                            diffuseColor: root.theme.axisGreen
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Model {
                        source: "#Cylinder"
                        scale: Qt.vector3d(root.axisRadiusScale, root.axisLengthScale, root.axisRadiusScale)
                        materials: DefaultMaterial {
                            diffuseColor: root.theme.axisBlue
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Repeater3D {
                        model: root.latitudeAngles

                        delegate: Node {
                            required property real modelData

                            property real latRad: modelData * Math.PI / 180
                            property real ringRadiusValue: root.sphereRadius * Math.cos(latRad)

                            y: root.sphereRadius * Math.sin(latRad)
                            eulerRotation: Qt.vector3d(90, 0, 0)

                            Repeater3D {
                                model: root.ringSegments

                                delegate: Model {
                                    property real midDeg: (index + 0.5) * 360 / root.ringSegments
                                    property real midRad: midDeg * Math.PI / 180
                                    property real segmentLength: 2 * Math.PI * parent.parent.ringRadiusValue / root.ringSegments

                                    source: "#Cylinder"
                                    position: Qt.vector3d(parent.parent.ringRadiusValue * Math.cos(midRad), parent.parent.ringRadiusValue * Math.sin(midRad), 0)
                                    eulerRotation: Qt.vector3d(0, 0, midDeg)
                                    scale: Qt.vector3d(0.010, Math.max(0.001, segmentLength / 100), 0.010)
                                    materials: DefaultMaterial {
                                        diffuseColor: parent.parent.modelData >= 0 ? "#5b72ff" : "#a46b3c"
                                        lighting: DefaultMaterial.NoLighting
                                        opacity: root.gridLineOpacity
                                        depthDrawMode: Material.NeverDepthDraw
                                    }
                                }
                            }
                        }
                    }

                    Repeater3D {
                        model: root.meridianAngles

                        delegate: Node {
                            required property real modelData

                            eulerRotation: Qt.vector3d(0, modelData, 0)

                            Repeater3D {
                                model: root.ringSegments

                                delegate: Model {
                                    property real midDeg: (index + 0.5) * 360 / root.ringSegments
                                    property real midRad: midDeg * Math.PI / 180
                                    property real segmentLength: 2 * Math.PI * root.sphereRadius / root.ringSegments
                                    property real localY: root.sphereRadius * Math.sin(midRad)

                                    source: "#Cylinder"
                                    position: Qt.vector3d(root.sphereRadius * Math.cos(midRad), root.sphereRadius * Math.sin(midRad), 0)
                                    eulerRotation: Qt.vector3d(0, 0, midDeg)
                                    scale: Qt.vector3d(0.010, Math.max(0.001, segmentLength / 100), 0.010)
                                    materials: DefaultMaterial {
                                        diffuseColor: localY >= 0 ? "#5b72ff" : "#a46b3c"
                                        lighting: DefaultMaterial.NoLighting
                                        opacity: root.gridLineOpacity
                                        depthDrawMode: Material.NeverDepthDraw
                                    }
                                }
                            }
                        }
                    }

                    Repeater3D {
                        model: root.diagonalAngles

                        delegate: Node {
                            required property real modelData

                            property real tiltRad: root.diagonalTilt * Math.PI / 180

                            eulerRotation: Qt.vector3d(0, modelData, root.diagonalTilt)

                            Repeater3D {
                                model: root.ringSegments

                                delegate: Model {
                                    property real midDeg: (index + 0.5) * 360 / root.ringSegments
                                    property real midRad: midDeg * Math.PI / 180
                                    property real segmentLength: 2 * Math.PI * root.sphereRadius / root.ringSegments
                                    property real localX: root.sphereRadius * Math.cos(midRad)
                                    property real localY: root.sphereRadius * Math.sin(midRad)
                                    property real worldY: localX * Math.sin(parent.parent.tiltRad) + localY * Math.cos(parent.parent.tiltRad)

                                    source: "#Cylinder"
                                    position: Qt.vector3d(localX, localY, 0)
                                    eulerRotation: Qt.vector3d(0, 0, midDeg)
                                    scale: Qt.vector3d(0.009, Math.max(0.001, segmentLength / 100), 0.009)
                                    materials: DefaultMaterial {
                                        diffuseColor: worldY >= 0 ? "#6d83ff" : "#9c6a42"
                                        lighting: DefaultMaterial.NoLighting
                                        opacity: root.gridLineOpacity - 0.08
                                        depthDrawMode: Material.NeverDepthDraw
                                    }
                                }
                            }
                        }
                    }

                    Repeater3D {
                        model: root.visibleSources

                        delegate: Node {
                            required property var modelData

                            position: root.sourcePositionVector(modelData)

                            Model {
                                source: "#Sphere"
                                scale: Qt.vector3d(root.sourceMarkerScale, root.sourceMarkerScale, root.sourceMarkerScale)
                                materials: DefaultMaterial {
                                    diffuseColor: modelData.color
                                    lighting: DefaultMaterial.NoLighting
                                    opacity: root.sourceMarkerOpacity
                                    depthDrawMode: Material.NeverDepthDraw
                                }
                            }

                            Model {
                                source: "#Sphere"
                                scale: Qt.vector3d(root.sourceHighlightScale, root.sourceHighlightScale, root.sourceHighlightScale)
                                position: Qt.vector3d(0, 0, root.sourceHighlightOffset)
                                materials: DefaultMaterial {
                                    diffuseColor: Qt.rgba(1, 1, 1, 0.72)
                                    lighting: DefaultMaterial.NoLighting
                                    depthDrawMode: Material.NeverDepthDraw
                                }
                            }
                        }
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

        onPressed: function (mouse) {
            cursorShape = Qt.ClosedHandCursor
            lastX = mouse.x
            lastY = mouse.y
        }

        onReleased: function () {
            cursorShape = Qt.OpenHandCursor
        }

        onPositionChanged: function (mouse) {
            if (!(mouse.buttons & Qt.LeftButton)) {
                return
            }
            root.applyDragDelta(mouse.x - lastX, mouse.y - lastY)
            lastX = mouse.x
            lastY = mouse.y
        }
    }

    Canvas {
        id: axisOverlay
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: 14
        anchors.bottomMargin: 12
        width: 120
        height: 96

        readonly property real originX: 30
        readonly property real originY: 70
        readonly property real axisScale: 26

        onPaint: {
            const ctx = getContext("2d")
            const xPoint = root.axisEndpoint({
                x: 1,
                y: 0,
                z: 0
            }, axisScale)
            const yPoint = root.axisEndpoint({
                x: 0,
                y: 0,
                z: 1
            }, axisScale)
            const zPoint = root.axisEndpoint({
                x: 0,
                y: 1,
                z: 0
            }, axisScale)
            const xLabel = root.labelAnchor(xPoint)
            const yLabel = root.labelAnchor(yPoint)
            const zLabel = root.labelAnchor(zPoint)

            ctx.reset()
            ctx.lineCap = "round"
            ctx.lineWidth = 2
            ctx.font = "12px sans-serif"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"

            function drawAxis(point, labelPoint, label, color) {
                ctx.strokeStyle = color
                ctx.beginPath()
                ctx.moveTo(originX, originY)
                ctx.lineTo(point.x, point.y)
                ctx.stroke()
                ctx.fillStyle = color
                ctx.fillText(label, labelPoint.x, labelPoint.y)
            }

            drawAxis(xPoint, xLabel, "X", root.theme.axisOrange)
            drawAxis(yPoint, yLabel, "Y", root.theme.axisGreen)
            drawAxis(zPoint, zLabel, "Z", root.theme.axisBlue)

            ctx.fillStyle = "#141414"
            ctx.beginPath()
            ctx.arc(originX, originY, 2.4, 0, Math.PI * 2)
            ctx.fill()
        }
    }
}
