# PRD: App Footer View

## Goal

定义 `src/temporal/qml/AppFooter.qml` 的底栏需求。
底栏用于承载状态类辅助信息，需要与头部品牌条形成统一的绿色品牌收边效果。

## Component Responsibility

- 渲染底部绿色信息条。
- 展示左侧产品说明文字。
- 展示右侧法律声明入口或占位文案。

## Data Contract

### Inputs

- `theme.footerHeightValue`
- `theme.accentGreen`
- `theme.smallFont`

### Rules

- 文案长度需要适配不同窗口宽度，避免截断主要信息。

## Visual Requirements

- 底栏高度固定且紧凑。
- 背景色与品牌条保持同系绿色。
- 文字颜色使用高对比浅色。

## Interaction Requirements

- 右侧法律声明支持点击反馈。

## Technical Constraints

- 底栏不承担业务控制逻辑。

## Non-Goals

- 不在底栏中展示复杂状态面板。

## Acceptance Criteria

1. 底栏在默认尺寸下完整可见。
2. 左右文案对齐稳定，不因窗口缩放产生重叠。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppFooter.qml`
