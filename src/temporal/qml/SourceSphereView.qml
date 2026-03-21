import QtQuick
import QtQuick3D

Rectangle {
    id: root

    required property QtObject theme
    property var sourcePositionsModel: null
    property int sourceModelRevision: 0

    color: "#ffffff"
    border.color: "transparent"

    property real sphereYaw: 0
    property real spherePitch: 0
    property real sphereRadius: 150
    property var latitudeAngles: [-60, -36, -18, 18, 36, 60]
    property var meridianAngles: [0, 30, 60, 90, 120, 150]
    property var diagonalAngles: [0, 40, 80, 120, 160]
    property int ringSegments: 44
    property real diagonalTilt: 52
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

    function rotateVector(vector) {
        const pitchRad = spherePitch * Math.PI / 180
        const yawRad = sphereYaw * Math.PI / 180
        const cosPitch = Math.cos(pitchRad)
        const sinPitch = Math.sin(pitchRad)
        const cosYaw = Math.cos(yawRad)
        const sinYaw = Math.sin(yawRad)

        const pitchedY = vector.y * cosPitch - vector.z * sinPitch
        const pitchedZ = vector.y * sinPitch + vector.z * cosPitch
        const yawedX = vector.x * cosYaw + pitchedZ * sinYaw
        const yawedZ = -vector.x * sinYaw + pitchedZ * cosYaw

        return {
            x: yawedX,
            y: pitchedY,
            z: yawedZ
        }
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
        anchors.fill: parent
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        anchors.topMargin: 4
        anchors.bottomMargin: 6
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
            position: Qt.vector3d(0, 18, 520)
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
            id: sceneRoot
            y: 4
            eulerRotation: Qt.vector3d(root.spherePitch, root.sphereYaw, 0)

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(1.92, 0.048, 1.92)
                materials: DefaultMaterial {
                    diffuseColor: Qt.rgba(0.52, 0.69, 0.42, 0.56)
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.34, 0.30, 0.34)
                materials: DefaultMaterial {
                    diffuseColor: "#111111"
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cube"
                scale: Qt.vector3d(0.56, 0.28, 0.38)
                materials: DefaultMaterial {
                    diffuseColor: "#111111"
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.016, 3.40, 0.016)
                eulerRotation: Qt.vector3d(0, 0, 90)
                materials: DefaultMaterial {
                    diffuseColor: root.theme.axisOrange
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.016, 3.40, 0.016)
                eulerRotation: Qt.vector3d(90, 0, 0)
                materials: DefaultMaterial {
                    diffuseColor: root.theme.axisGreen
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.016, 3.40, 0.016)
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
                                diffuseColor: parent.parent.modelData > 0 ? "#5b72ff" : "#a46b3c"
                                lighting: DefaultMaterial.NoLighting
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
                            }
                        }
                    }
                }
            }

            Repeater3D {
                model: root.visibleSources

                delegate: Node {
                    required property var modelData

                    position: Qt.vector3d(modelData.x * root.sphereRadius, modelData.z * root.sphereRadius, modelData.y * root.sphereRadius)

                    Model {
                        source: "#Sphere"
                        scale: Qt.vector3d(0.105, 0.105, 0.105)
                        materials: DefaultMaterial {
                            diffuseColor: modelData.color
                            lighting: DefaultMaterial.NoLighting
                        }
                    }

                    Model {
                        source: "#Sphere"
                        scale: Qt.vector3d(0.042, 0.042, 0.042)
                        position: Qt.vector3d(0, 0, 0.3)
                        materials: DefaultMaterial {
                            diffuseColor: Qt.rgba(1, 1, 1, 0.72)
                            lighting: DefaultMaterial.NoLighting
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
            root.sphereYaw += (mouse.x - lastX) * 0.42
            root.spherePitch = Math.max(-70, Math.min(70, root.spherePitch + (mouse.y - lastY) * 0.30))
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
