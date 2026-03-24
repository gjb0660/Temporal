# ODAS Protocol Knowledge

## 1. Overview

本文件汇总当前项目依赖的 ODAS 流类型、端口事实与解析现实。
其作用是为 feature 的 Facts / Decision 提供可复用背景材料。

## 2. Stream Facts

- SST tracked JSON stream 使用端口 `9000`
- SSL potential JSON stream 使用端口 `9001`
- SSS separated PCM stream 使用端口 `10000`
- SSS post-filtered PCM stream 使用端口 `10010`

## 3. Parsing Realities

- JSON TCP 输入存在 chunk boundary 现实，单次读取不保证消息边界完整。
- 输入流中可能出现 malformed line 或 junk line。
- reconnect 是常见现实，不应被视为异常边缘路径。
- audio consumer 若阻塞 socket thread，会放大丢包、延迟与状态漂移风险。

## 4. Remote Control Realities

- non-interactive `sh` 控制会话中的 helper bootstrap 不是永久性的。
- shell 丢失后，helper bootstrap 需要重新建立。
- `remote.host` 不应被复用为 SST / SSL / SSS listener address 的隐式语义来源。
- stream direction 必须在 spec 与代码中显式表达。

## 5. Summary

- ODAS 流的端口语义是稳定背景事实。
- 协议解析必须接受 chunk boundary、junk line 与 reconnect 的现实。
- 远程 shell 会话具有可失效性，bootstrap 需要按 live session 语义处理。
- 流方向必须显式，而不能从无关字段偷推导。

## References

[ODAS Source Analysis](./references/odas-analysis.md)
[ODAS Web Source Analysis](./references/odas_web-analysis.md)
