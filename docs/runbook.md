# Temporal 操作手册

## 目标

本文档面向运维和开发联调人员，提供可复现的运行步骤、
检查点和常见故障排查方法。

## 1. 启动前检查

1. 确认 Python 环境和依赖已安装。
2. 确认配置文件 [config/odas.example.toml](config/odas.example.toml)
   已填写远端主机、SSH 密钥路径和端口。
3. 确认远端 ODAS 主机可达，端口 22/9000/9001/10000/10010 可访问。

## 2. 启动应用

1. 在仓库根目录执行：`uv run temporal`
2. 界面出现后检查状态文本为“Temporal 就绪”。

## 3. 远端控制流程

1. 点击“连接 SSH”，状态应变为“SSH 已连接”。
2. 点击“启动 odaslive”，状态应变为“远程 odaslive 已启动”。
3. 观察日志面板是否持续刷新。
4. 结束时点击“停止 odaslive”。

## 4. 数据流与录制流程

1. 点击“开始监听”启动 SST/SSL/SSS。
2. 检查 Sources 列表是否出现有效 source id（非 0）。
3. 检查 recordingSourceCount 是否与可映射 source 数一致。
4. 检查 recordingSessions 是否出现 `Source {id} [sp|pf] ...wav`。
5. 点击“停止监听”后，录制计数和会话列表应清空。

## 5. 录制文件检查

1. 打开 [recordings](recordings) 目录。
2. 检查文件名格式：`ODAS_{source_id}_{timestamp}_{sp|pf}.wav`。
3. 使用播放器或脚本确认文件可打开且非空。

## 6. 常见问题排查

### 6.1 SSH 连接失败

1. 检查用户名和私钥路径。
2. 在终端手动验证 SSH：
   `ssh -i <key> <user>@<host>`。
3. 检查远端防火墙和安全组。

### 6.2 有源但不录制

1. 确认 source 在前 4 个映射通道内。
2. 确认 source 未被取消勾选。
3. 确认 SSS 端口无阻塞。

### 6.3 录制中断频繁

1. 检查网络抖动和 SST 更新间隔。
2. 检查 inactive timeout 是否过短。
3. 必要时先停止监听并重新开始。

## 7. 建议操作顺序

1. 连接 SSH。
2. 启动 odaslive。
3. 开始监听。
4. 观察录制状态。
5. 停止监听。
6. 停止 odaslive。
