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

    function normalizedSeries() {
        const normalized = []
        const count = modelCount(seriesModel)
        for (let index = 0; index < count; index += 1) {
            const item = seriesModel.get(index)
            let values = []
            try {
                values = JSON.parse(String(item.valuesJson || "[]"))
            } catch (error) {
                values = []
            }
            if (!Array.isArray(values) || values.length === 0) {
                continue
            }
            normalized.push({
                color: item.color,
                values: values
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

        for (let index = 0; index < visibleSeries.length; index += 1) {
            const item = visibleSeries[index]
            plot(item.values, item.color || theme.accentPurple)
        }
    }
}
