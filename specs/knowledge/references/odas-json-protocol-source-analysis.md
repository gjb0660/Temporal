# ODAS JSON Protocol Source Analysis

## Scope

Source level: direct source fact

本报告仅基于 `Y:\workspace\ODAS\odas` 源码事实，范围限定为 JSON sink 协议。
不包含下游系统行为、兼容策略或实现建议。

## JSON Sink Inventory

Source level: direct source fact

ODAS sink 层包含 3 个 `format_text_json` 实现：

- `src/sink/snk_tracks.c:245-247,341-377`
- `src/sink/snk_pots.c:249-251,352-382`
- `src/sink/snk_categories.c:240-242,336-385`

## Shared Transport Behavior

Source level: direct source fact

三类 JSON sink 的 socket 接口都以 TCP client 方式连接配置中的 `ip:port`：

- `snk_tracks_open_interface_socket` 使用 `connect(...)`：`src/sink/snk_tracks.c:150-166`
- `snk_pots_open_interface_socket` 使用 `connect(...)`：`src/sink/snk_pots.c:148-164`
- `snk_categories_open_interface_socket` 使用 `connect(...)`：`src/sink/snk_categories.c:147-161`

Source level: direct source fact

三类 sink 在 `timeStamp != 0` 时才进入 format + interface process：

- tracks: `src/sink/snk_tracks.c:241-283`
- pots: `src/sink/snk_pots.c:239-286`
- categories: `src/sink/snk_categories.c:236-277`

Source level: direct source fact

三类 sink 通过 `send(obj->sid, obj->buffer, obj->bufferSize, 0)` 发送完整缓冲区：

- tracks: `src/sink/snk_tracks.c:326-331`
- pots: `src/sink/snk_pots.c:330-335`
- categories: `src/sink/snk_categories.c:321-326`

## Shared JSON Framing

Source level: direct source fact

三类 JSON formatter 都按以下顺序拼接文本缓冲区：

1. `"{\n"`
2. `"    \"timeStamp\": ...,\n"`
3. `"    \"src\": [\n"`
4. 循环拼接 `src` 数组项，每项后可带 `,`，并追加 `\n`
5. `"    ]\n"`
6. `"}\n"`
7. `obj->bufferSize = strlen(obj->buffer)`

对应实现位置：

- tracks: `src/sink/snk_tracks.c:347-375`
- pots: `src/sink/snk_pots.c:358-380`
- categories: `src/sink/snk_categories.c:342-383`

## Tracks JSON Shape

Source level: direct source fact

`snk_tracks_process_format_text_json` 逐条输出字段：

- `timeStamp`（顶层）
- `src[*].id`
- `src[*].tag`
- `src[*].x`
- `src[*].y`
- `src[*].z`
- `src[*].activity`

证据：`src/sink/snk_tracks.c:348-360`。

Source level: direct source fact

`src` 数组循环上限为 `obj->nTracks`，每条记录由 `obj->in->tracks` 读取。
证据：`src/sink/snk_tracks.c:351-365`。

## Pots JSON Shape

Source level: direct source fact

`snk_pots_process_format_text_json` 逐条输出字段：

- `timeStamp`（顶层）
- `src[*].x`
- `src[*].y`
- `src[*].z`
- `src[*].E`

证据：`src/sink/snk_pots.c:359-366`。

Source level: direct source fact

`src` 数组循环上限为 `obj->nPots`，每条记录从 `obj->in->pots->array` 按 4 元组读取。
证据：`src/sink/snk_pots.c:362-365`。

## Categories JSON Shape

Source level: direct source fact

`snk_categories_process_format_text_json` 逐条输出字段：

- `timeStamp`（顶层）
- `src[*].category`

证据：`src/sink/snk_categories.c:343-365`。

Source level: direct source fact

`category` 值在 formatter 内由 switch 直接映射为：

- `"speech"`（case `0x01`）
- `"nonspeech"`（case `0x00`）
- `"undefined"`（default）

证据：`src/sink/snk_categories.c:348-365`。
