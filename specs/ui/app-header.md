# Spec: App Header View

## Goal

定义 `src/temporal/qml/AppHeader.qml` 的头部区域需求。
该组件负责同时呈现菜单条与绿色品牌条，需要在保持品牌识别的同时，尽量贴近 Windows 原生菜单和标题区域的视觉观感。

## Component Responsibility

- 渲染顶部菜单条。
- 渲染绿色品牌头条。
- 显示产品名称 `Temporal Studio`。
- 显示右侧导航入口，如“配置”“录制”“相机”。

## Data Contract

### Inputs

- `theme.menuHeight`
- `theme.brandHeight`
- `theme.brandFont`
- `theme.accentGreen`
- `theme.titleColor`

### Rules

- 菜单项和品牌条文案由组件内定义，不在业务层拼接。
- 所有尺寸和颜色优先从 `theme` 读取。

## Visual Requirements

- 菜单条为白底，分隔线轻量。
- 品牌条为纯绿色主色带。
- `Temporal Studio` 字号需要比上一版更克制，不能压过页面主体。
- 字体优先使用 `Segoe UI` / `Microsoft YaHei UI`。

## Interaction Requirements

- 菜单项具备 hover 和按压反馈。
- 品牌区右侧导航项支持点击反馈。

## Technical Constraints

- 头部组件不直接触发后端逻辑。
- 菜单行为如未实现功能，可先保留为 UI 占位入口。

## Non-Goals

- 不在该组件内实现菜单实际命令分发。

## Acceptance Criteria

1. 头部在默认窗口尺寸下与参考图的信息层级一致。
2. `Temporal Studio` 标题明显小于前一版实现。
3. 菜单条和品牌条的分层清晰可辨。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppHeader.qml`
