# Temporal

Temporal 是一个面向 ODAS 的阵列语音上位机客户端，采用 Python + QML 实现。

## 产品定位

- 连接并控制远端 odaslive 运行状态
- 实时查看 SST / SSL / SSS 数据联动
- 通过 Sources / Filters 面板进行快速筛选
- 按声源生命周期自动触发录制

## 一键启动

```powershell
uv run temporal
```

## 当前能力边界

- 已完成：项目骨架、远端控制、媒体链路、自动录音、SSS 路由、界面系统、preview 入口
- 进行中：展示运行时语义收口、远端集成风险收口、测试与可靠性加固

## 文档入口

- 实现规格：specs/
- 用户手册：docs/（由 specs 手动导出）

## 说明

README 面向使用者与协作者，不展开开发流程细节。
如需参与开发，请查看仓库规则与 `specs/index.md` 规范。
