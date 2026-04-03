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
- `src/temporal/app/bridge.py` 构造器把上述回调连接到
  `_on_sst/_on_ssl/_on_sep_audio/_on_pf_audio`。
- `src/temporal/app/bridge.py` 中 `_on_*` 在非 QObject 线程时通过
  `_sstIngressRequested/_sslIngressRequested/_sepAudioIngressRequested/_pfAudioIngressRequested`
  进入 `Qt.QueuedConnection`，再由 `_handle_*_ingress` 执行后续处理。

### Timer Path（Qt event loop）

- `src/temporal/app/bridge.py` 创建：
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
    `sourceCountChanged`, `potentialCountChanged`,
    `_sstIngressRequested`, `_sslIngressRequested`,
    `_sepAudioIngressRequested`, `_pfAudioIngressRequested`
- `QmlListModel.replace()` 触发点：
  - 初始化时：`_source_rows_model`, `_source_positions_model`,
    `_elevation_chart_series_model`, `_azimuth_chart_series_model`,
    `_preview_scenario_options_model`, `_chart_window_model`,
    `_header_nav_labels_model`, `_recording_sessions_model`
  - 运行时：`_recording_sessions_model`, `_source_positions_model`,
    `_source_rows_model`, `_chart_window_model`,
    `_elevation_chart_series_model`, `_azimuth_chart_series_model`

## 4. State Variables And Transition Triggers

当前状态字段与触发入口事实：

- 控制态字段：`_remote_connected`, `_odas_starting`, `_odas_running`,
  `_streams_active`
  - 触发入口：`connectRemote`, `startRemoteOdas`, `stopRemoteOdas`,
    `toggleRemoteOdas`, `startStreams`, `stopStreams`,
    `_sync_remote_odas_state`, `_verify_odas_startup`, `_poll_remote_log`
- 数据态字段：`_last_sst`, `_last_ssl`, `_source_ids`,
  `_selected_source_ids`, `_source_channel_map`, `_channel_source_map`,
  `_runtime_chart_messages`, `_runtime_chart_frame_sources`
  - 触发入口：`_on_sst`, `_on_ssl`, `_on_sep_audio`, `_on_pf_audio`,
    `_handle_sst_ingress`, `_handle_ssl_ingress`,
    `_handle_sep_audio_ingress`, `_handle_pf_audio_ingress`,
    `_refresh_sources`, `_refresh_chart_models`, `_append_runtime_chart_frame`

## 5. Public Interface Usage Snapshot

统计范围：`src/temporal/qml/*.qml` 与 `tests/*.py`。

### 已移除候选接口（当前静态引用）

- `sourceItems`: `src=0`, `qml=0`, `tests=0`
- `sourcePositions`: `src=0`, `qml=0`, `tests=0`
- `recordingSessions`: `src=0`, `qml=0`, `tests=0`
- `isSourceSelected(...)`: `src=0`, `qml=0`, `tests=0`

### 仍被引用的公开面（当前快照）

- `sourceRowsModel`: `qml=2`, `tests=15`
- `sourcePositionsModel`: `qml=4`, `tests=16`
- `chartWindowModel`: `qml=2`, `tests=8`
- `elevationChartSeriesModel`: `qml=1`, `tests=8`
- `azimuthChartSeriesModel`: `qml=1`, `tests=7`
- `previewScenarioOptionsModel`: `qml=3`, `tests=3`
- `recordingSessionsModel`: `qml=2`, `tests=1`
- `toggleRemoteOdas(...)`: `qml=1`, `tests=8`
- `toggleStreams(...)`: `qml=1`, `tests=9`

### 仍保留但未被 QML/tests 直接引用的接口（当前快照）

- `sourceCount`: `qml=0`, `tests=0`（`src` 内部状态/文案链路仍引用）
- `setStatus(...)`: `qml=0`, `tests=0`（`src` 内部状态写入链路仍引用）

## 6. References

- `src/temporal/app/bridge.py`
- `src/temporal/app/preview_runtime.py`
- `src/temporal/core/network/odas_client.py`
- `src/temporal/core/network/odas_stream_client.py`
- `src/temporal/preview_bridge.py`
- `src/temporal/qml/*.qml`
- `tests/*.py`
