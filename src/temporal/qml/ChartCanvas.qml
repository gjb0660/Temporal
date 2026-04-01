import QtQuick

Canvas {
    id: root

    required property QtObject theme
    property var yTicks: []
    property var xTickModel: null
    property var seriesModel: null
    property string xAxisLabel: "时间 (0.01s)"

    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onYTicksChanged: requestPaint()
    onXTickModelChanged: requestPaint()
    onSeriesModelChanged: requestPaint()
    onXAxisLabelChanged: requestPaint()

    Connections {
        target: root.xTickModel

        function onModelReset() {
            root.requestPaint()
        }

        function onRowsInserted() {
            root.requestPaint()
        }

        function onRowsRemoved() {
            root.requestPaint()
        }

        function onDataChanged() {
            root.requestPaint()
        }
    }

    Connections {
        target: root.seriesModel

        function onModelReset() {
            root.requestPaint()
        }

        function onRowsInserted() {
            root.requestPaint()
        }

        function onRowsRemoved() {
            root.requestPaint()
        }

        function onDataChanged() {
            root.requestPaint()
        }
    }

    function modelCount(model) {
        return model && typeof model.count === "number" ? model.count : 0
    }

    function readTicks() {
        const ticks = []
        const count = modelCount(xTickModel)
        for (let index = 0; index < count; index += 1) {
            ticks.push(String(xTickModel.get(index).value))
        }
        return ticks
    }

    function parseTickValues(ticks) {
        const values = []
        for (let index = 0; index < ticks.length; index += 1) {
            const value = Number(ticks[index])
            if (Number.isFinite(value)) {
                values.push(value)
            }
        }
        return values
    }

    function rangeBounds(values) {
        if (values.length === 0) {
            return {
                min: 0,
                max: 1
            }
        }
        let minValue = values[0]
        let maxValue = values[0]
        for (let index = 1; index < values.length; index += 1) {
            minValue = Math.min(minValue, values[index])
            maxValue = Math.max(maxValue, values[index])
        }
        return {
            min: minValue,
            max: maxValue
        }
    }

    function normalizeValue(value, minValue, maxValue) {
        if (maxValue === minValue) {
            return 0.5
        }
        return (value - minValue) / (maxValue - minValue)
    }

    function normalizePoint(point, xMin, xMax, yMin, yMax) {
        if (!point || point.y === null || point.y === undefined) {
            return null
        }
        const xValue = Number(point.x)
        const yValue = Number(point.y)
        if (!Number.isFinite(xValue) || !Number.isFinite(yValue)) {
            return null
        }
        return {
            x: normalizeValue(xValue, xMin, xMax),
            y: normalizeValue(yValue, yMin, yMax)
        }
    }

    function toPointList(rawPoints) {
        if (rawPoints === null || rawPoints === undefined) {
            return []
        }
        if (Array.isArray(rawPoints)) {
            return rawPoints
        }
        if (typeof rawPoints.length === "number") {
            const converted = []
            for (let index = 0; index < rawPoints.length; index += 1) {
                converted.push(rawPoints[index])
            }
            return converted
        }
        return []
    }

    function normalizedSeries() {
        const normalized = []
        const count = modelCount(seriesModel)
        const xValues = parseTickValues(readTicks())
        const xBounds = rangeBounds(xValues)
        const yValues = parseTickValues(yTicks)
        const yBounds = rangeBounds(yValues)
        for (let index = 0; index < count; index += 1) {
            const item = seriesModel.get(index)
            const points = toPointList(item.points)
            if (points.length === 0) {
                continue
            }
            const normalizedPoints = []
            for (let pointIndex = 0; pointIndex < points.length; pointIndex += 1) {
                normalizedPoints.push(normalizePoint(points[pointIndex], xBounds.min, xBounds.max, yBounds.min, yBounds.max))
            }
            normalized.push({
                color: item.color,
                points: normalizedPoints
            })
        }
        return normalized
    }

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
        const xTicks = readTicks()
        const visibleSeries = normalizedSeries()

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
            ctx.strokeStyle = color
            ctx.lineWidth = 2
            let drawing = false
            for (let index = 0; index < points.length; index += 1) {
                const point = points[index]
                if (!point) {
                    if (drawing) {
                        ctx.stroke()
                        drawing = false
                    }
                    continue
                }
                const px = leftPad + point.x * plotW
                const py = topPad + plotH * (1 - point.y)
                if (!drawing) {
                    ctx.beginPath()
                    ctx.moveTo(px, py)
                    drawing = true
                } else {
                    ctx.lineTo(px, py)
                }
            }
            if (drawing) {
                ctx.stroke()
            }
        }

        for (let index = 0; index < visibleSeries.length; index += 1) {
            const item = visibleSeries[index]
            plot(item.points, item.color || theme.accentPurple)
        }
    }
}
