# Temporal 操作手册

## 目标

本文档面向运维和联调人员，说明 Temporal 与远端 ODAS 的正确协作方式。

- 数据流方向固定为 `ODAS -> Temporal`
- Temporal 通过 SSH 远程启动 `odaslive`
- `odaslive` 主动连接 Temporal 本地监听端口推送 SST、SSL、SSS 数据

## 启动前检查

1. 确认 Python 环境和依赖已安装。
2. 检查配置文件 [config/odas.example.toml](../config/odas.example.toml)。
3. 确认 `[streams].listen_host` 是远端 ODAS 可访问到的 Temporal 本机地址。
4. 确认 `sst_port`、`ssl_port`、`sss_sep_port`、`sss_pf_port` 未被本机占用。
5. 确认远端 SSH 可达，且 `odas.cwd`、`odas.command`、ODAS cfg 路径配置正确。

## 推荐操作顺序

1. 启动 Temporal：`uv run temporal`
2. 在界面中连接 SSH。
3. 启动监听。
4. 启动远端 `odaslive`。
5. 观察日志、声源和录音状态。
6. 结束时先停监听，再停远端 `odaslive`。

## 远端配置要求

- `odas.cwd` 为相对路径时，按远端 `$HOME/<cwd>` 解析。
- `odas.command` 必须是可执行命令或脚本。
- `odas.args` 中必须能定位到 ODAS cfg 文件，或 wrapper 脚本中能解析出 cfg 路径。
- ODAS cfg 中 `tracks`、`hops`、音频 sink 的目标地址必须指向 Temporal 的
  `streams.listen_host` 和对应端口。

## 启动语义

- Temporal 不再主动连接 `remote.host:9000/9001/10000/10010`。
- 启动远端 `odaslive` 前，Temporal 会先启动本地监听端并执行远端 preflight。
- preflight 失败时，界面状态显示摘要原因，原始错误保留在日志区。
- 只有远端实例通过 PID 校验后，状态才会变为“运行中”。

## 常见问题

### `Sink tracks/hops: Cannot connect to server`

这通常不是 Temporal 本地解析故障，而是远端 ODAS 无法连接到 Temporal 监听端。

排查顺序：

1. 检查 `[streams].listen_host` 是否填写为远端 ODAS 可访问的 Temporal 地址。
2. 检查远端 ODAS cfg 中 sink 的 host/port 是否与 Temporal 配置完全一致。
3. 检查 Temporal 是否已经启动监听。
4. 检查本机防火墙是否放通 `9000/9001/10000/10010`。

### 远端工作目录不存在

若状态显示“远程工作目录不存在或不可访问”：

1. 检查 `odas.cwd` 是否写错。
2. 若为相对路径，确认其相对的是远端 `$HOME`，不是登录 shell 的当前目录。

### 远端命令不存在或不可执行

若状态显示“远程命令不存在或未安装”或“远程命令或目录权限不足”：

1. 检查 `odas.command` 是否存在。
2. 检查 wrapper 脚本是否有执行权限。
3. 检查 wrapper 内部引用的 cfg 和二进制路径是否仍有效。
