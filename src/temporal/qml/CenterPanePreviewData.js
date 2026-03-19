.pragma library

function palette(theme) {
    return {
        7: theme.accentCyan,
        12: "#ff9c47",
        15: theme.accentPurple,
        21: "#5ac97c",
        27: "#f16f7d",
        31: "#6a88ff"
    }
}

function cloneSeries(points) {
    return points.slice(0)
}

function buildSeries(sourceId, color, values) {
    return {
        sourceId: sourceId,
        color: color,
        values: cloneSeries(values)
    }
}

function buildPosition(sourceId, color, x, y, z) {
    return {
        id: sourceId,
        color: color,
        x: x,
        y: y,
        z: z
    }
}

function buildCatalog(theme) {
    const colors = palette(theme)

    return {
        referenceSingle: {
            key: "referenceSingle",
            sourceColors: colors,
            sourcePositions: [
                buildPosition(15, colors[15], -0.42, 0.18, 0.64)
            ],
            elevationSeries: [
                buildSeries(15, colors[15], [0.40, 0.44, 0.49, 0.54, 0.58, 0.60, 0.61, 0.60, 0.59, 0.58])
            ],
            azimuthSeries: [
                buildSeries(15, colors[15], [0.88, 0.88, 0.87, 0.86, 0.85, 0.84, 0.82, 0.81, 0.82, 0.83])
            ]
        },
        hemisphereSpread: {
            key: "hemisphereSpread",
            sourceColors: colors,
            sourcePositions: [
                buildPosition(7, colors[7], -0.56, 0.28, 0.58),
                buildPosition(15, colors[15], 0.46, 0.18, 0.62),
                buildPosition(21, colors[21], -0.18, -0.42, -0.50),
                buildPosition(31, colors[31], 0.54, -0.36, 0.10)
            ],
            elevationSeries: [
                buildSeries(7, colors[7], [0.56, 0.57, 0.57, 0.56, 0.55, 0.54, 0.54, 0.54, 0.53, 0.53]),
                buildSeries(15, colors[15], [0.34, 0.36, 0.40, 0.45, 0.50, 0.55, 0.57, 0.58, 0.59, 0.60]),
                buildSeries(21, colors[21], [0.18, 0.17, 0.16, 0.14, 0.13, 0.11, 0.10, 0.10, 0.09, 0.08]),
                buildSeries(31, colors[31], [0.48, 0.47, 0.46, 0.44, 0.42, 0.41, 0.39, 0.38, 0.37, 0.36])
            ],
            azimuthSeries: [
                buildSeries(7, colors[7], [0.12, 0.12, 0.13, 0.14, 0.14, 0.14, 0.15, 0.15, 0.15, 0.16]),
                buildSeries(15, colors[15], [0.84, 0.84, 0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.78, 0.77]),
                buildSeries(21, colors[21], [0.62, 0.61, 0.60, 0.58, 0.57, 0.55, 0.54, 0.53, 0.52, 0.50]),
                buildSeries(31, colors[31], [0.34, 0.35, 0.37, 0.39, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46])
            ]
        },
        equatorBoundary: {
            key: "equatorBoundary",
            sourceColors: colors,
            sourcePositions: [
                buildPosition(12, colors[12], 0.98, 0.00, 0.02),
                buildPosition(15, colors[15], -0.96, 0.02, -0.01),
                buildPosition(27, colors[27], 0.02, 0.00, 0.98),
                buildPosition(31, colors[31], 0.04, -0.02, -0.96)
            ],
            elevationSeries: [
                buildSeries(12, colors[12], [0.51, 0.50, 0.50, 0.49, 0.49, 0.48, 0.48, 0.48, 0.47, 0.47]),
                buildSeries(15, colors[15], [0.49, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.53]),
                buildSeries(27, colors[27], [0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.89, 0.90, 0.90]),
                buildSeries(31, colors[31], [0.17, 0.16, 0.16, 0.15, 0.14, 0.14, 0.13, 0.12, 0.11, 0.10])
            ],
            azimuthSeries: [
                buildSeries(12, colors[12], [0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55, 0.55, 0.56]),
                buildSeries(15, colors[15], [0.49, 0.48, 0.48, 0.47, 0.47, 0.46, 0.46, 0.45, 0.45, 0.44]),
                buildSeries(27, colors[27], [0.74, 0.74, 0.74, 0.75, 0.75, 0.76, 0.76, 0.77, 0.77, 0.78]),
                buildSeries(31, colors[31], [0.24, 0.24, 0.23, 0.23, 0.22, 0.22, 0.21, 0.21, 0.20, 0.20])
            ]
        },
        emptyState: {
            key: "emptyState",
            sourceColors: colors,
            sourcePositions: [],
            elevationSeries: [],
            azimuthSeries: []
        }
    }
}
