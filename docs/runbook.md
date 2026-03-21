# Temporal 操作手册

## 目标

本文档面向运维和开发联调人员，提供可复现的运行步骤、检查点和常见故障排查方法。
本轮补充 preview 入口顺序、监听独立启停和主按钮的新状态机语义，作为 UI 联调与手工验收的统一操作手册。

## 1. 启动前检查

1. 确认 Python 环境和依赖已安装。
2. 确认配置文件 [config/odas.example.toml](config/odas.example.toml) 已填写远端主机、SSH 密钥路径和端口。
3. 确认远端 ODAS 主机可达，端口 `22/9000/9001/10000/10010` 可访问。
4. 运行 preview 前，确认本地 Qt 环境可创建 `QGuiApplication`，避免入口阶段出现 `QObject::startTimer` 告警。

## 2. 启动应用

1. 预览联调执行：`uv run temporal-preview`
2. 正式运行执行：`uv run temporal`
3. 界面出现后检查状态文本为“Temporal 就绪”。
4. preview 默认只渲染首帧静态结果，不自动滚动。
5. 若 preview 启动日志出现 Qt timer 相关告警，应优先检查入口是否在 `QGuiApplication` 创建前构造了 `PreviewBridge`。

## 3. 远端控制流程

1. 点击主按钮“启动”时，系统应先确保 SSH 已连接。
2. 若本地 listener 尚未开启，主按钮启动流程会先开启 listener，再启动远端 `odaslive`。
3. 主按钮启动完成后，应看到远端已启动状态，并进入 `SST/SSL/SSS` 监听态。
4. 点击主按钮“停止”时，系统应先停止本地监听，再停止远端 `odaslive`。
5. 主按钮停止后默认不断开 SSH，便于继续查看日志或再次启动。

## 4. 数据流与录制流程

1. 监听按钮可以在远端未运行时独立开启本地 listener。
2. preview 模式下，只有监听开启后，sample window、图表和 3D 点位才会推进。
3. 监听关闭后，preview 应停留在当前静态结果，不再继续滚动。
4. 再次开启监听时，preview 应从场景起点重新开始，保证复现稳定。
5. 正式运行时，检查 Sources 列表是否出现有效 source id（非 `0`）。
6. 检查 `recordingSourceCount` 是否与可映射 source 数一致。
7. 检查 `recordingSessions` 是否出现 `Source {id} [sp|pf] ...wav`。
8. 单独点击“停止监听”后，监听端口关闭，但不会自动停止远端 `odaslive`。

## 5. 录制文件检查

1. 打开 [recordings](recordings) 目录。
2. 检查文件名格式：`ODAS_{source_id}_{timestamp}_{sp|pf}.wav`。
3. 使用播放器或脚本确认文件可打开且非空。
4. 若存在多源场景，确认只有被通道映射接管的 source 会生成录音文件。

## 6. 常见问题排查

### 6.1 SSH 连接失败

1. 检查用户名和私钥路径。
2. 在终端手动验证 SSH：`ssh -i <key> <user>@<host>`。
3. 检查远端防火墙和安全组。

### 6.2 有源但不录制

1. 确认 source 在前 `4` 个映射通道内。
2. 确认 source 未被取消勾选。
3. 确认 `SSS` 端口无阻塞。

### 6.3 录制中断频繁

1. 检查网络抖动和 `SST` 更新间隔。
2. 检查 inactive timeout 是否过短。
3. 必要时先停止监听并重新开始。

## 7. 建议操作顺序

1. 预览联调时，先启动 `temporal-preview`，确认首帧静态画面正常。
2. 点击“监听”，确认图表和 3D 开始同步推进。
3. 如需联动远端，再点击主按钮“启动”，确认其自动补开监听并启动远端。
4. 验收结束时，优先测试“单独停止监听”路径。
5. 最后再测试主按钮“停止”路径，确认顺序为“先停监听，再停远端”。
