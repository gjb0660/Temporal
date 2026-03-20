# ODAS 配置分析 - 详细总结

## 1. SSL/SST/SSS 输出通道与字段

### SSL (Sound Source Localization)

- **输出端口**: 9001 (TCP Socket)
- **IP 地址**: 172.21.16.139
- **输出格式**: JSON
- **配置路径**: `ssl.potential`
- **字段类型**: POTs (Point of Targets) - 包含定位候选源点

### SST (Sound Source Tracking)

- **输出端口**: 9000 (TCP Socket)
- **IP 地址**: 172.21.16.139
- **输出格式**: JSON
- **配置路径**: `sst.tracked`
- **字段类型**: Tracks - 包含追踪的声源轨迹
- **跟踪模式**: Kalman滤波器（可选粒子滤波器）
- **关键参数**:
  - `Ptrack = 0.8`: 追踪概率
  - `N_inactive = (150, 200, 250, 250)`: 非活跃追踪帧数阈值
  - `theta_inactive = 0.9`: 非活跃追踪得分阈值

### SSS (Sound Source Separation & Post-filtering)

- **分离输出**:
  - 端口: 10000 (TCP Socket)
  - IP: 172.21.16.139
  - 采样率: 16000 Hz
  - HopSize: 128
  - 分离模式: DDS (Delay and Sum)
  - 增益: 25.0 (提升分离音量)

- **后滤波输出**:
  - 端口: 10010 (TCP Socket)
  - IP: 172.21.16.139
  - 采样率: 16000 Hz
  - HopSize: 128
  - 后滤波模式: SS (Spectral Subtraction)
  - 增益: 35.0 (提升后验滤波音量)

## 2. odaslive 启动参数与依赖

### 启动参数

```bash
odaslive [OPTIONS]

OPTIONS:
  -c <cfg_file>    配置文件路径（必须）- 例如: odas.cfg
  -h               显示帮助信息
  -s               单线程处理（默认为多线程）
  -v               详细输出模式
```

### 编译依赖

从 CMakeLists.txt：

- libfftw3f: FFT运算库
- libconfig: 配置文件解析
- libalsa: 音频驱动（ALSA）
- libpulse-simple: PulseAudio支持
- pthread: 多线程支持
- libm: 数学库

### odaslive 源文件组成

- main.c: 主程序入口、命令行参数解析、信号处理
- configs.c: 配置文件加载和初始化
- objects.c: ODAS处理对象构造
- parameters.c: 配置参数查询函数
- threads.c: 多线程/单线程处理
- profiler.c: 性能分析

### 处理流程

1. 信号采集 (Raw audio from soundcard)
2. 映射 (Mapping)
3. 重采样 (Resample)
4. STFT (频率域转换)
5. 噪声估计 (Noise Estimation)
6. SSL (声源定位)
7. SST (声源追踪)
8. SSS (声源分离)
9. ISTFT + 重采样 (音频域转换)
10. 音量调整 (Volume)
11. 分类 (Classification)

## 3. Temporal 客户端最小数据契约建议

### 3.1 核心接收端口

```text
SSL:  172.21.16.139:9001 (JSON)
SST:  172.21.16.139:9000 (JSON)
SEP:  172.21.16.139:10000 (Raw audio PCM)
PF:   172.21.16.139:10010 (Raw audio PCM)
```

### 3.2 JSON 数据格式预期（基于 ODAS 代码）

**SSL POTs 格式** (来自 snk_pots_ssl):

- ID: 唯一源标识符
- x, y, z: 3D空间位置坐标（米）
- 可能还有：energy, confidence, activity等

**SST Tracks 格式** (来自 snk_tracks_sst):

- TrackID: 追踪ID
- x, y, z: 当前位置
- vx, vy, vz: 速度向量
- energy: 能量/强度
- activity: 活跃程度（0-1）
- 状态: 活跃/非活跃/新增/消失

### 3.3 音频数据格式预期

**分离音频** (port 10000):

- 采样率: 16000 Hz
- 格式: 16-bit PCM
- HopSize: 128 samples
- 多声道: 分离后的单声道音频（按源标识）

**后滤波音频** (port 10010):

- 采样率: 16000 Hz
- 格式: 16-bit PCM
- HopSize: 128 samples
- 单声道: 后滤波后的干净语音

### 3.4 最小客户端实现检查清单

[] 创建 TCP 连接池 (4个socket: SSL, SST, SEP, PF)
[] 实现 JSON 解析器 (目标是解析 POTs和Tracks消息)
[] 实现音频接收缓冲 (环形缓冲处理HopSize=128)
[] 实现错误处理 (连接断开、心跳检测)
[] 记录接收配置 (IP/端口/格式) 用于Temporal workflow

### 3.5 推荐的监听顺序

1. **优先级1**: SST 9000 (追踪数据 - 最有价值)
2. **优先级2**: SSL 9001 (定位数据 - 补充SST)
3. **优先级3**: PF 10010 (后滤波音频 - 用于验证)
4. **可选**: SEP 10000 (分离音频 - 实验用)

### 3.6 数据流时序注意事项

- SSL/SST: 实时JSON事件流
- 音频(SEP/PF): 连续音频流，需要缓冲和同步
- 建议: 用timestamp关联 JSON事件和音频片段
- 考虑网络延迟（本地网络应 <10ms）
