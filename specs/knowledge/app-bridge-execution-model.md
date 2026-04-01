# AppBridge Execution Model

## 1. Overview

本文件记录 `AppBridge` 当前执行模型的可验证事实，
用于描述事件来源、线程归属、Qt 写入点与接口引用面。

## 2. Event Sources And Thread Ownership

### Listener Path（ODAS stream）

- `src/temporal/core/network/odas_stream_client.py` 在 `start()` 中创建
  `threading.Thread(target=self._run, ...)`。
- 同文件 `_run()` 在 listener 线程中调用 `_handle_client()`。
- `TcpJsonListener._handle_client()` 在 listener 线程调用 `self._handler(msg)`。
- `TcpAudioListener._handle_client()` 在 listener 线程调用 `self._handler(chunk)`。

### Callback Binding（OdasClient -> AppBridge）

- `src/temporal/core/network/odas_client.py` 中：
  - `on_sst` 绑定 `TcpJsonListener(config.sst, on_sst, "sst")`
  - `on_ssl` 绑定 `TcpJsonListener(config.ssl, on_ssl, "ssl")`
  - `on_sep_audio` 绑定 `TcpAudioListener(config.sss_sep, on_sep_audio, "sep")`
  - `on_pf_audio` 绑定 `TcpAudioListener(config.sss_pf, on_pf_audio, "pf")`
- `src/temporal/app.py` 构造器把上述回调连接到
  `_on_sst/_on_ssl/_on_sep_audio/_on_pf_audio`。

### Timer Path（Qt event loop）

- `src/temporal/app.py` 创建：
  - `_log_timer = QTimer(self)`，`timeout.connect(self._poll_remote_log)`
  - `_startup_timer = QTimer(self)`，`timeout.connect(self._verify_odas_startup)`

## 3. Qt Write Points

`AppBridge` 当前存在以下 Qt 写入行为事实：

- `Signal.emit()` 触发点：
  - `statusChanged`, `remoteConnectedChanged`, `odasStartingChanged`,
    `odasRunningChanged`, `streamsActiveChanged`, `canToggleStreamsChanged`,
    `recordingSourceCountChanged`, `remoteLogLinesChanged`,
    `remoteLogTextChanged`, `recordingSessionsChanged`,
    `sourcePositionsChanged`, `sourceIdsChanged`, `sourceItemsChanged`,
    `sourceCountChanged`, `potentialCountChanged`
- `QmlListModel.replace()` 触发点：
  - 初始化时：`_source_rows_model`, `_source_positions_model`,
    `_elevation_series_model`, `_azimuth_series_model`,
    `_preview_scenario_options_model`, `_chart_x_ticks_model`,
    `_header_nav_labels_model`, `_recording_sessions_model`
  - 运行时：`_recording_sessions_model`, `_source_positions_model`,
    `_source_rows_model`, `_chart_x_ticks_model`,
    `_elevation_series_model`, `_azimuth_series_model`

## 4. State Variables And Transition Triggers

当前状态字段与触发入口事实：

- 控制态字段：`_remote_connected`, `_odas_starting`, `_odas_running`,
  `_streams_active`
  - 触发入口：`connectRemote`, `startRemoteOdas`, `stopRemoteOdas`,
    `toggleRemoteOdas`, `startStreams`, `stopStreams`,
    `_sync_remote_odas_state`, `_verify_odas_startup`, `_poll_remote_log`
- 数据态字段：`_last_sst`, `_last_ssl`, `_source_ids`,
  `_selected_source_ids`, `_source_channel_map`, `_channel_source_map`,
  `_runtime_chart_frames`
  - 触发入口：`_on_sst`, `_on_ssl`, `_on_sep_audio`, `_on_pf_audio`,
    `_refresh_sources`, `_refresh_chart_models`, `_append_runtime_chart_frame`

## 5. Public Interface Usage Snapshot

统计范围：`src/temporal/qml/*.qml` 与 `tests/*.py`。

### Property / Slot 初始瘦身候选（当前直接引用计数）

- `sourceItems`: `qml=0`, `tests=0`
- `sourcePositions`: `qml=0`, `tests=0`
- `sourceCount`: `qml=0`, `tests=0`
- `recordingSessions`: `qml=0`, `tests=0`
- `setStatus(...)`: `qml=0`, `tests=0`
- `isSourceSelected(...)`: `qml=0`, `tests=0`

### 仍被引用的典型公开面（样例）

- `sourceRowsModel`: `qml=2`, `tests=29`
- `sourcePositionsModel`: `qml=1`, `tests=14`
- `elevationSeriesModel`: `qml=1`, `tests=16`
- `azimuthSeriesModel`: `qml=1`, `tests=13`
- `toggleRemoteOdas(...)`: `qml=1`, `tests=8`
- `toggleStreams(...)`: `qml=1`, `tests=6`

## 6. References

- `src/temporal/app.py`
- `src/temporal/core/network/odas_client.py`
- `src/temporal/core/network/odas_stream_client.py`
- `src/temporal/preview_bridge.py`
- `src/temporal/qml/*.qml`
- `tests/*.py`
