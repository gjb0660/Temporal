# ODAS Source Analysis

## Core Architecture

Source level: direct source fact

ODAS 的 authoritative 参考来自 `Y:\workspace\ODAS\odas` 源码快照。
`CMakeLists.txt` 定义了一个共享库 `odas`，以及两个 demo
可执行：`odaslive` 和 `odasserver`。

- `odaslive` 入口位于 `demo/odaslive/main.c`
- 配置装配位于 `demo/odaslive/configs.c`
- 配置解析位于 `demo/odaslive/parameters.c`
- 处理对象与线程装配位于 `demo/odaslive/objects.c`
  和 `demo/odaslive/threads.c`

Source level: direct source fact

构建依赖由 `CMakeLists.txt` 明确声明：

- `fftw3f`
- `alsa`
- `libconfig`
- `libpulse-simple`
- `pthread`
- `m`

Source level: direct source fact

`odaslive` 命令行参数来自 `demo/odaslive/main.c`：

- `-c <cfg_file>`: 必填配置文件路径
- `-h`: 打印帮助
- `-s`: 单线程模式
- `-v`: verbose 输出

Source level: inference from source

从 `configs.c` 的装配顺序可以看出，`odaslive` 的主链路是：
`raw -> mapping -> resample -> STFT -> noise -> SSL -> target injector
-> SST -> SSS -> ISTFT -> resample -> volume -> sinks/classify`。
这不是 README 级摘要，而是当前 demo runtime 的实际拼装顺序。

## Runtime Direction

Source level: direct source fact

当配置里的 `interface.type = "socket"` 时，ODAS 侧不是监听端，
而是 TCP client。这个结论来自两类源码：

- `src/source/src_hops.c` 的 `src_hops_open_interface_socket`
  调用 `connect(...)`
- `src/sink/snk_pots.c`、`src/sink/snk_tracks.c`、
  `src/sink/snk_hops.c` 的 socket open 逻辑也都调用 `connect(...)`

Source level: inference from source

因此，只要 ODAS 配置把 raw 输入、JSON 输出、或 SSS/PF 输出
设成 socket，外部系统就必须先启动 server。
这直接解释了为什么 `odas_web` 要先监听 9000/9001/10000/10010，
再等待 ODAS 连接进来。

## Wire Contracts

### SSL Potential JSON

Source level: direct source fact

`src/sink/snk_pots.c` 的 `snk_pots_process_format_text_json`
定义了 SSL potential 的 JSON 形状：

```json
{
  "timeStamp": 123,
  "src": [
    { "x": 0.123, "y": -0.456, "z": 0.789, "E": 0.321 }
  ]
}
```

Source level: direct source fact

字段层面只有以下确定项：

- `timeStamp`: `unsigned long long`
- `src[*].x`: `float`
- `src[*].y`: `float`
- `src[*].z`: `float`
- `src[*].E`: `float`

文档里不应再写 `id`、`confidence`、`activity` 等未在该 sink
中输出的字段。

### SST Tracked JSON

Source level: direct source fact

`src/sink/snk_tracks.c` 的 `snk_tracks_process_format_text_json`
定义了 tracked JSON 形状：

```json
{
  "timeStamp": 123,
  "src": [
    {
      "id": 7,
      "tag": "",
      "x": 0.123,
      "y": -0.456,
      "z": 0.789,
      "activity": 0.912
    }
  ]
}
```

Source level: direct source fact

字段层面只有以下确定项：

- `timeStamp`: `unsigned long long`
- `src[*].id`: `unsigned long long`
- `src[*].tag`: `char[256]` 语义上的字符串
- `src[*].x`: `float`
- `src[*].y`: `float`
- `src[*].z`: `float`
- `src[*].activity`: `float`

文档里不应继续把 `vx`、`vy`、`vz` 或独立 `energy` 写成
tracked JSON 固定字段，因为当前 sink 实现没有输出这些值。

### SSS And PF PCM Framing

Source level: direct source fact

`src/sink/snk_hops.c` 对二进制音频的写法是：
外层按 sample 遍历，内层按 channel 遍历，然后把每个 sample
编码成整数 PCM 写入 buffer。

Source level: inference from source

因此 SSS separated 和 PF postfiltered 的 socket/file 输出都是：

- 二进制整型 PCM，不是 JSON
- sample-major
- channel-interleaved
- 每帧字节数为 `hopSize * nChannels * bytes_per_sample`

Source level: direct source fact

位深允许 `int08/int16/int24/int32`。
当前本地配置样例普遍使用 `16-bit`。

### Track Count And Audio Channel Count

Source level: direct source fact

`demo/odaslive/parameters.c` 明确把多个 runtime 容量都绑定到
`sst.N_inactive` 的数组长度：

- `parameters_msg_tracks_sst_config`:
  `nTracks = parameters_count(fileConfig, "sst.N_inactive")`
- `parameters_msg_hops_seps_rs_config`:
  `nChannels = parameters_count(fileConfig, "sst.N_inactive")`
- `parameters_msg_hops_pfs_rs_config`:
  `nChannels = parameters_count(fileConfig, "sst.N_inactive")`

Source level: inference from source

这意味着：

- tracked source 最大槽位数由配置驱动
- separated/postfiltered 输出通道数也由同一配置驱动
- “4 路 source / 4 路音频”只是某些配置实例的结果，
  不是 ODAS 协议本身的固定常量

## Local Config Profiles

### `config/odas.cfg`

Source level: config-specific fact

这是当前仓库内的一个本地配置实例，不应上升为 ODAS 通用常量。
它展示的组合为：

- `ssl.potential`: socket JSON -> `172.21.16.139:9001`
- `sst.tracked`: socket JSON -> `172.21.16.139:9000`
- `sss.separated`: socket PCM -> `172.21.16.139:10000`
- `sss.postfiltered`: socket PCM -> `172.21.16.139:10010`
- `sss.separated.fS = 16000`
- `sss.separated.hopSize = 128`
- `sss.postfiltered.fS = 16000`
- `sss.postfiltered.hopSize = 128`
- `sss.mode_sep = "dds"`
- `sss.mode_pf = "ss"`
- `sst.N_inactive = (150, 200, 250, 250)`，对应 4 track slot

### `re6_sockets.cfg`

Source level: config-specific fact

这个样例展示的是 raw 输入和 JSON 输出走 socket 的配置：

- raw input: socket -> `192.168.0.243:12346`
- `ssl.potential`: socket JSON -> `172.25.112.1:9001`
- `sst.tracked`: socket JSON -> `172.25.112.1:9000`

同一文件中的 `sss.separated` 与 `sss.postfiltered` 仍然是 file sink，
不是 socket sink。

### `re6_vr.cfg`

Source level: config-specific fact

这个样例展示的是 SSS separated 走 socket 的变体：

- `sss.separated`: socket PCM -> `172.24.48.1:10000`

从仓库内可检索内容看，它不是当前知识库里
`172.21.16.139:10000/10010` 这组地址的来源。

## Temporal Impact

Source level: inference from source

对 Temporal 最重要的上游约束有四项：

- JSON 协议只应按 `timeStamp` 和 `src` 数组解析，
  并严格使用 ODAS 当前 sink 实现中的字段集合
- socket 模式下，Temporal 必须把自己当成 server，
  由 ODAS 主动连入
- SSS/PF 音频必须按交错 PCM 读取，不能假设单路独占 socket
- 可视化和录音的 source/channel 槽位数应来自配置，
  不能把 `4` 写死成协议常量

Source level: inference from source

因此，知识库应把 `IP:port`、`hopSize`、`fS`、`nChannels`
分成两层记录：

- ODAS 通用协议形状
- 当前本地配置实例

只有这样，后续对接新阵列或新配置时，
Temporal 才不会把本地样例误当成上游不变量。
