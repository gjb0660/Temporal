import QtQuick
import QtQuick.Controls
import QtQuick3D

Rectangle {
    id: root

    required property QtObject theme
    required property var sourcePositions

    color: "#ffffff"
    border.color: "transparent"

    property real sphereYaw: -20
    property real spherePitch: 16
    property real sphereRadius: 132
    property var latitudeAngles: [-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75]
    property var longitudeAngles: [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345]
    property int ringSegments: 36

    function previewSources() {
        if (sourcePositions.length > 0) {
            return sourcePositions
        }
        return [
            {
                id: 15,
                x: -0.42,
                y: 0.14,
                z: 0.60
            }
        ]
    }

    View3D {
        anchors.fill: parent
        anchors.margins: 2
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
            position: Qt.vector3d(0, 0, 430)
            clipFar: 2000
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(-34, 28, 0)
            brightness: 0.95
        }

        DirectionalLight {
            eulerRotation: Qt.vector3d(40, -35, 0)
            brightness: 0.35
        }

        Node {
            id: sceneRoot
            y: -86
            eulerRotation: Qt.vector3d(root.spherePitch, root.sphereYaw, 0)

            Model {
                source: "#Sphere"
                scale: Qt.vector3d(2.32, 0.10, 2.32)
                position: Qt.vector3d(0, -24, 0)
                materials: DefaultMaterial {
                    diffuseColor: Qt.rgba(0.50, 0.69, 0.42, 0.52)
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Sphere"
                scale: Qt.vector3d(2.08, 0.06, 2.08)
                position: Qt.vector3d(0, -66, 0)
                materials: DefaultMaterial {
                    diffuseColor: Qt.rgba(0.66, 0.44, 0.27, 0.42)
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.020, 2.82, 0.020)
                materials: DefaultMaterial {
                    diffuseColor: root.theme.axisBlue
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.020, 1.72, 0.020)
                position: Qt.vector3d(86, 0, 0)
                eulerRotation: Qt.vector3d(0, 0, 90)
                materials: DefaultMaterial {
                    diffuseColor: root.theme.axisOrange
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cylinder"
                scale: Qt.vector3d(0.020, 1.72, 0.020)
                position: Qt.vector3d(0, 0, 86)
                eulerRotation: Qt.vector3d(90, 0, 0)
                materials: DefaultMaterial {
                    diffuseColor: root.theme.axisGreen
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cube"
                scale: Qt.vector3d(0.42, 0.24, 0.30)
                materials: DefaultMaterial {
                    diffuseColor: "#141414"
                    lighting: DefaultMaterial.NoLighting
                }
            }

            Model {
                source: "#Cube"
                scale: Qt.vector3d(0.20, 0.38, 0.20)
                materials: DefaultMaterial {
                    diffuseColor: "#141414"
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
                            scale: Qt.vector3d(0.012, Math.max(0.001, segmentLength / 100), 0.012)
                            materials: DefaultMaterial {
                                diffuseColor: "#5b6fff"
                                lighting: DefaultMaterial.NoLighting
                            }
                        }
                    }
                }
            }

            Repeater3D {
                model: root.longitudeAngles

                delegate: Node {
                    required property real modelData

                    eulerRotation: Qt.vector3d(0, modelData, 0)

                    Repeater3D {
                        model: root.ringSegments

                        delegate: Model {
                            property real midDeg: (index + 0.5) * 360 / root.ringSegments
                            property real midRad: midDeg * Math.PI / 180
                            property real segmentLength: 2 * Math.PI * root.sphereRadius / root.ringSegments

                            source: "#Cylinder"
                            position: Qt.vector3d(root.sphereRadius * Math.cos(midRad), root.sphereRadius * Math.sin(midRad), 0)
                            eulerRotation: Qt.vector3d(0, 0, midDeg)
                            scale: Qt.vector3d(0.012, Math.max(0.001, segmentLength / 100), 0.012)
                            materials: DefaultMaterial {
                                diffuseColor: "#5b6fff"
                                lighting: DefaultMaterial.NoLighting
                            }
                        }
                    }
                }
            }

            Repeater3D {
                model: root.previewSources()

                delegate: Model {
                    required property var modelData

                    source: "#Sphere"
                    position: Qt.vector3d(modelData.x * root.sphereRadius, -modelData.z * root.sphereRadius, modelData.y * root.sphereRadius)
                    scale: Qt.vector3d(0.080, 0.080, 0.080)
                    materials: DefaultMaterial {
                        diffuseColor: root.theme.accentPurple
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

    Canvas {
        id: axisOverlay
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: 20
        anchors.bottomMargin: 18
        width: 96
        height: 74

        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            ctx.lineCap = "round"
            ctx.lineWidth = 2

            const ox = 24
            const oy = 56

            ctx.strokeStyle = root.theme.axisOrange
            ctx.beginPath()
            ctx.moveTo(ox, oy)
            ctx.lineTo(74, oy)
            ctx.stroke()

            ctx.strokeStyle = root.theme.axisBlue
            ctx.beginPath()
            ctx.moveTo(ox, oy)
            ctx.lineTo(ox, 12)
            ctx.stroke()

            ctx.strokeStyle = root.theme.axisGreen
            ctx.beginPath()
            ctx.moveTo(ox, oy)
            ctx.lineTo(8, 26)
            ctx.stroke()
        }
    }

    Label {
        anchors.left: axisOverlay.left
        anchors.top: axisOverlay.top
        anchors.leftMargin: 0
        anchors.topMargin: 4
        text: "Y"
        color: theme.axisGreen
        font.pixelSize: theme.smallFont + 1
    }

    Label {
        anchors.left: axisOverlay.left
        anchors.top: axisOverlay.top
        anchors.leftMargin: 22
        anchors.topMargin: -4
        text: "Z"
        color: theme.axisBlue
        font.pixelSize: theme.smallFont + 1
    }

    Label {
        anchors.left: axisOverlay.left
        anchors.top: axisOverlay.top
        anchors.leftMargin: 74
        anchors.topMargin: 42
        text: "X"
        color: theme.axisOrange
        font.pixelSize: theme.smallFont + 1
    }
}
