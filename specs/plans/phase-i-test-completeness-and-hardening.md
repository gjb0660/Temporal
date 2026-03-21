# Spec: Phase I Test Completeness and Reliability Hardening

## Goal

收敛当前测试体系中的逻辑完备性缺口，使核心运行时行为由
behavior-level tests 保护，而不是停留在局部 happy-path coverage。

## Scope

- 审视现有 unittest 对 AppBridge、ODAS listener startup、
  remote SSH lifecycle、config parsing、recorder flow 的契约覆盖。
- 为高风险状态迁移和 negative paths 补充缺失测试。
- 在 shell 与 asynchronous runtime 行为才是真正契约时，
  优先使用 behavior-level tests，而不是 script substring checks。
- 保持现有 `unittest`、deterministic fixtures、network-free fakes 风格；
  仅在证明 shell 语义或本地运行时缺陷时使用局部可执行检查。

## Non-Goals

- 不重构应用运行时架构，也不重设计 ODAS operator workflow。
- 不引入 CI 平台治理或 coverage-percentage gates。
- 不替换 `unittest` 为其他测试框架。
- 不因风格原因重写已稳定且低风险的既有测试。

## Problem Statement

当前测试对 pure parsing helpers 与 recorder basics 的覆盖相对充分，
但从第一性原理看，整套测试尚未形成逻辑闭环：

- pure parsing 与 recorder helpers 覆盖较好；
- AppBridge state-machine transitions 覆盖仍然不完整；
- remote SSH shell behavior 主要依赖 generated-script substring checks，
  尚未充分验证 executable behavior；
- listener failure 与 async startup failure 路径此前缺少直接保护；
- QML-facing acceptance behavior 尚未形成自动断言。

这意味着在最关键的运行路径上，仍可能出现以下回归而不被测试发现：
Temporal 错误汇报 listener 已启动、remote odaslive 启动状态不真实、
failure reason 选择退化、以及 UI 状态与 backend 事实不一致。

## Functional Requirements

1. 为 AppBridge 的 connect、start、stop、toggle、filter、selection
   等 public slot 行为补齐 success 和 failure 测试。
2. 保护 listener startup truthfulness：
   一旦 local listener bind 失败，`streamsActive` 必须保持 false，
   remote start flow 不得继续假定监听已就绪。
3. 保护 remote startup truthfulness：
   startup 状态必须保持为 `starting`，直到 process existence 被验证；
   failure reason 选择顺序必须稳定且受测试保护。
4. 用可执行测试保护 remote shell preflight semantics，
   包括 cfg path、sink target validation、pid identity validation、
   stop/status behavior。
5. 为 config parsing 的 invalid types、blank required values、
   invalid integer fields、missing files 补齐 negative cases。
6. 为 audio routing edge cases 补齐测试，避免 truncated frames、
   empty mappings、invalid channel states 静默破坏 recorder 行为。
7. 为 AppBridge 对 source/potential filtering 的公开行为补齐测试，
   确保 UI-visible derived state 与 backend state 一致。
8. 至少在 bridge-contract 层保护 QML-visible control semantics，
   使按钮文案与 enable/disable 规则始终反映真实运行时状态。

## Test Additions

### AppBridge state-machine coverage

- 为 `connectRemote()` 增加 SSH failure path 测试：
  `remoteConnected` false、`odasRunning` false、startup cancel 生效，
  且 status / log 更新一致。
- 为 `stopRemoteOdas()` 增加 exception path 与 non-zero stop result 测试。
- 为 `_poll_remote_log()` 增加以下场景：
  SSH disconnect、generic log-read failure、non-zero stderr、
  empty log output、以及 health-sync 从 running 变为 stopped。
- 为 `_verify_odas_startup()` 增加以下场景：
  `status()` exception、timeout exhaustion、log-priority failure reason、
  stderr/stdout fallback、以及成功转为 running。
- 为 `_pick_startup_failure_reason()` 和
  `_humanize_startup_failure_reason()` 建立显式 mapping contract tests。
- 为 `setSourcesEnabled()`、`setSourceSelected()`、
  `setPotentialsEnabled()`、`setPotentialEnergyRange()` 增加测试，
  验证 `sourceItems`、`sourcePositions`、`potentialCount`、
  `status` 的联动结果。

### Listener and transport coverage

- 保留新加入的 red test，证明 async bind failure 不能把 streams
  错报为 active。
- 补充 listener start/stop 幂等性，以及 server 从未成功 bind 时的
  safe shutdown 测试。
- 为 handler exception 行为补测试；若设计上允许线程终止，
  则将该策略文档化并冻结。
- 保持现有 reconnect 与 malformed JSON 覆盖。

### Remote SSH behavior coverage

- 保留新加入的 red test，证明 cfg validation 不能因 comments 或
  unrelated text 恰好匹配 host/ports 而错误通过。
- 补充 executable shell-behavior tests，而不是只做 substring checks：
  stale pid cleanup、invalid numeric pid rejection、
  mismatched cwd rejection、mismatched cmdline rejection、
  relative `odas.log` resolution、`~`-relative path resolution、
  stop timeout failure behavior。
- 仅在外部不可观测但接口稳定性必须验证时，保留少量 script-shape 断言。

### Config-loader coverage

- 为以下场景补充测试：
  missing config file、blank `streams.listen_host`、
  non-string `remote.username`、non-string `remote.private_key`、
  non-string `odas.cwd`、invalid `remote.port`、
  invalid stream ports、以及 bool 被错误接受为 integer 的场景。
- 保留当前对 blank command、blank log、args type、
  wildcard default behavior 的测试。

### Recorder and audio-routing coverage

- 为 `_route_audio_chunk()` 补充以下场景：
  no channel map、不足一帧的 chunk、trailing partial frame bytes、
  invalid channel indices、以及 mode-specific pushes 相互隔离。
- 增加 over-capacity source handling 在 selection/filter 变动后的
  channel reuse 与 recording count contract 测试。
- 若 silent-drop inactive session 是既定语义，
  为 `AutoRecorder.push()` 增加明确的 no-op 测试。

### QML-facing contract coverage

- 至少增加一个 bridge-level contract test，覆盖
  `odasStarting`、`odasRunning`、`streamsActive` 组合状态下的
  按钮驱动语义。
- 若当前工具链可行，增加轻量 QML test 或 snapshot-like assertion，
  验证 log wrapping、starting 时的按钮文案、listen button enablement。
- 若 QML automation 暂不可行，则在 spec 中明确：
  这些 acceptance points 由 bridge-level tests + qmllint 联合保护，
  不再留作隐性假设。

## Quality Requirements

- 统一使用 `unittest`。
- 保持测试 deterministic 和 local，不依赖真实 remote network 或 SSH。
- 对 stateful behavior 使用 fake controllers、fake clocks、
  temporary directories。
- 仅在证明 shell-script semantics 必要时执行本地 shell 检查，
  并保证其 hermetic 到 workspace 临时目录。
- 让新增测试按 behavior 分组，而不是围绕 private helper internals 展开。
- 除非被更强的 behavior test 替代，否则保留现有稳定低风险测试。

## Acceptance Criteria

1. 所有参与 remote runtime control 的 AppBridge public slot，
   均具备 happy-path 与 failure-path 测试。
2. listener bind failure 时，系统不会把 startup 错报为 active。
3. remote preflight 不会因 cfg comments 或 unrelated text 而误判通过。
4. startup failure reason ordering 具备稳定测试保护。
5. config loader 会拒绝无效 required types 与 integer fields。
6. audio routing 能正确处理 frame boundary 与 unusable input。
7. 现有 parser 与 recorder tests 不出现回归。
8. 触及模块的 targeted unittest 集在实现完成后全部通过。

## Validation Workflow

1. 先更新本 spec。
2. 先为每个高风险未覆盖契约增加 red tests。
3. 再以最小实现修复这些测试。
4. 运行以下 targeted unittests：
   `test_app_bridge_integration.py`、
   `test_app_bridge_recording.py`、
   `test_remote_odas.py`、
   `test_odas_stream_client.py`、
   `test_config_loader.py`、
   `test_auto_recorder.py`、
   `test_json_stream.py`、
   `test_odas_message_view.py`。
5. 对触及的 Python 与 Markdown 文件运行仓库要求的质量检查。
6. 若仍存在暂不覆盖的分支，必须记录为 explicit deferred risk，
   不能继续保持隐性缺口。

## Preventive Rules

- 对 async、shell、lifecycle 代码优先使用 behavior-level tests，
  不把 substring checks 当作充分契约。
- 不在 asynchronous resource 真正 active 之前宣称 runtime state 已 active。
- 让 UI-facing status 始终源自 validated backend state，
  而不是 launch intent。
