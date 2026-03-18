import QtQuick
import QtQuick.Controls
import QtQuick3D

Rectangle {
    id: root

    required property QtObject theme
    required property var sourcePositions

    color: "#ffffff"
    border.color: "#ffffff"

    property real sphereYaw: -18
    property real spherePitch: 14
    property real sphereRadius: 118
    property var latitudeAngles: [-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75]
    property var longitudeAngles: [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345]

    function previewSources() {
        if (sourcePositions.length > 0) {
            return sourcePositions
        }
        return [{ id: 15, x: -0.42, y: 0.14, z: 0.60 }]
    }

    View3D {
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
                model: root.previewSources()

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
            font.pixelSize: theme.smallFont
        }

        Label {
            x: 36
            y: 22
            text: "X"
            color: "#ff6a2d"
            font.pixelSize: theme.smallFont
        }
    }
}
