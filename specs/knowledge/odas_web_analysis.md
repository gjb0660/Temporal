# ODAS Web Analysis

## Process Model

Source level: direct source fact

`D:\Workspace\odas_web` 是一个 Electron 应用。
`package.json` 指定 `main.js` 为主进程入口，启动命令是
`electron .`。

Source level: direct source fact

`main.js` 启动时加载的主进程模块包括：

- `servers.js`: 9000/9001 TCP server
- `record.js`: 录音窗口与录音子进程
- `share.js`: 共享/相机相关窗口
- `configure.js`: 设置窗口
- `odas.js`: 本地 ODAS 拉起与停止

Source level: direct source fact

主窗口默认加载 `views/live_data.html`。
因此，live data 页面是整个 UI 的中心视图，
其他页面通过新窗口打开。

## TCP Servers

### Tracking And Potential

Source level: direct source fact

`servers.js` 在主进程启动两个 TCP server：

- `startTrackingServer()` 监听 `9000`
- `startPotentialServer()` 监听 `9001`

Source level: direct source fact

收到数据后，主进程并不做协议级建模，只做文本分帧和转发：

- tracking socket -> `newTracking`
- potential socket -> `newPotential`

Source level: direct source fact

分帧策略依赖 `"}\n{"` 切分 JSON 文本，
并用 `remainingTrack` / `remainingPot`
拼接跨包残留数据。
这说明 `odas_web` 对 JSON framing 的假设是：
ODAS 输出为连续 JSON 对象流，中间通常以换行相邻。

Source level: inference from source

这里的容错是“基于文本边界修补”的轻量实现，
不是严格流式 JSON parser。
迁移时不能把这段实现误认为上游协议要求，
但可以把它当成旧 UI 的兼容行为参考。

### Separated And Postfiltered Audio

Source level: direct source fact

`record.js` 会额外拉起两个 Node 子进程：

- `recordings.js 10000 sp`
- `recordings.js 10010 pf`

这两个子进程各自创建 TCP server，
分别监听 10000 和 10010。

Source level: direct source fact

因此，`odas_web` 实际网络模型是：

- ODAS -> `odas_web` 主进程 TCP server: 9000 / 9001
- ODAS -> `odas_web` 录音子进程 TCP server: 10000 / 10010

知识库里不应再写成 “TCP/UDP 音频”，
因为当前实现只有 TCP stream。

## Renderer Data Model

### Current Frame Model

Source level: direct source fact

`resources/js/interface.js` 定义 renderer 的核心状态：

- `Source`
- `PotentialSource`
- `DataFrame`
- `currentFrame`

`currentFrame` 持有：

- `timestamp`
- `ptimestamp`
- `sources`
- `potentialSources`

### Source Slot Mapping

Source level: direct source fact

`resources/js/tcp_link.js` 使用 `indexMap`
把上游 `source id` 映射到 renderer 的固定 slot。
收到 tracked JSON 后会：

- 过滤 `id === 0`
- 复用旧 slot
- 给新 `id` 分配空闲 slot
- 失效 slot 触发清空和录音结束

Source level: inference from source

这说明 `odas_web` UI 不是直接按上游 `id`
动态渲染无限 source，而是先把 source id
投影到一组固定数量的 UI slot。

### Charts And Sphere

Source level: direct source fact

`resources/js/graph.js` 与 `resources/js/source_sphere.js`
共同完成可视化：

- elevation 折线图
- azimuth 折线图
- 3D sphere / axis
- potential heat-style point cloud
- tracked source trail

Source level: direct source fact

联动事件主要有：

- `tracking`
- `potential`
- `request-chart`
- `clearChart`
- `update-selection`
- `potential-visibility`

这些事件名应作为 odas_web 内部 UI contract 记录，
但不应写成 ODAS 协议的一部分。

### Fixed Slot Assumption

Source level: direct source fact

`resources/js/interface.js` 里 `rgbValueStrings`
只定义了 4 个 source 颜色槽位。
`DataFrame.sources` 也是按这组颜色初始化。

Source level: direct source fact

根目录 `recordings.js` 中 `nChannels = 4`，
录音进程按 4 路交错 PCM 拆流。

Source level: inference from source

因此，odas_web 当前实现隐含两个固定假设：

- UI 最多管理 4 个 tracked source slot
- 录音 socket 按 4 通道交错 PCM 处理

这两个假设来自 UI/录音实现，不是 ODAS upstream
协议常量。知识库里必须把它们和 ODAS
源码驱动的 `nTracks/nChannels` 区分开。

## Recording Pipeline

Source level: direct source fact

`record.js` 负责把 live 页面与录音子进程连接起来。
主进程接收以下 IPC：

- `new-recording`
- `end-recording`
- `start-recording`
- `stop-recording`
- `open-recordings-window`

然后把控制消息转发给两个 `recordings.js` 子进程。

Source level: direct source fact

`recordings.js` 的行为是：

- 监听指定端口的 TCP 音频流
- 按 16-bit、4-channel 交错 PCM 拆成单路
- 为每个 slot 驱动一个 `AudioRecorder`

Source level: direct source fact

`audio-recorder.js` 定义了录音命名规则：

```text
ODAS_{source_id}_{date}_{time}_{sp|pf}.wav
```

更准确地说，代码最终形式为：
`ODAS_${id}_${YYYY-M-D}_${H-M-S-ms}_${suffix}.wav`。

Source level: direct source fact

录音 workspace 管理由 `resources/js/recordings_model.js`
完成，目录中会维护：

- `.wav` 录音文件
- 同名 `.txt` 转写文件

Source level: direct source fact

recordings 页面还实现：

- 录音列表刷新
- 播放与停止
- 单文件删除
- 全量删除
- workspace 切换
- fuzzy transcript 与 final transcript 合并

## Migration Notes

Source level: inference from source

如果要把 odas_web 的经验迁移到 Temporal，
最值得保留的是行为，不是技术栈本身：

- 主动监听 ODAS 的 socket 连接
- tracked source 与 UI slot 的解耦
- tracked / potential / chart / 3D 的事件联动
- source 出现与消失驱动录音启停
- 录音 workspace 与转写文件共存

Source level: inference from source

最不应该照搬的是以下实现细节：

- 固定 4 slot / 4 通道
- 文本拼接式 JSON framing
- renderer 直接承担过多状态职责
- Electron renderer 中的 Node 直连模式

## Known Gaps

Source level: direct source fact

`views/live_data.html` 引用了
`resources/js/audio_stream.js`，
但当前仓库中不存在这个文件。

Source level: direct source fact

因此，这个引用应视为历史残留或未提交文件，
不能作为迁移依据，也不应被写进 Temporal 的
功能对等清单。

Source level: direct source fact

另一个需要明确记录的边界是：
`odas.js` 只负责本地进程 `spawn(core, ['-c', config])`
与 `SIGINT` 停止，并不覆盖 SSH、远端部署、
远端日志或 reconnect 编排。
这些能力不在 odas_web 的原始职责范围内。
