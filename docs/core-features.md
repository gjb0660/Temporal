# Core Features: Responsibilities and Collaboration

## 1. Overview

本系统主要由以下不可再分的核心能力构成：

- media-pipeline
- routing-session
- recording
- remote-control
- ui-system
- preview-mode

这些 feature 不是实现模块划分，而是**能力维度的最小完备分解**。

每个 feature：

- 表达一个独立的系统能力
- 拥有独立的 Goal 与 Acceptance
- 不与其他 feature 重叠职责

系统行为由这些 feature **协作形成，而非相互嵌套**。

---

## 2. Responsibility Model

### 2.1 media-pipeline

定义数据的**产生与处理方式**：

- 数据源（audio / video）
- 数据转换与过滤
- pipeline 结构

本质：**data transformation layer**

---

### 2.2 routing-session

定义数据与控制的**分发路径**：

- session 概念
- stream routing
- 多消费者分发

本质：**data distribution layer**

---

### 2.3 recording

定义数据的**持久化行为**：

- start / stop recording
- 数据写入
- 输出格式

本质：**persistence layer**

---

### 2.4 ui-system

定义用户的**交互机制**：

- 状态管理
- 用户操作 → 系统行为映射
- UI 与 backend 同步

本质：**interaction layer（human input）**

---

### 2.5 remote-control

定义外部系统的**控制入口**：

- API / socket / IPC
- 控制协议
- 命令结构

本质：**interaction layer（machine input）**

---

### 2.6 preview-mode

定义系统的**安全执行环境能力**：

- 提供独立入口（temporal-preview）
- 注入 PreviewBridge 替代真实控制路径
- 限制所有副作用为本地 no-op 行为
- 在不修改 UI 的前提下复用主界面

本质：**safe execution environment capability**

---

## 3. Capability Boundaries

### 3.1 Data Flow vs Control Flow

系统存在两条正交流：

#### Data Flow（数据流）

```text
media-pipeline → routing-session → recording
````

- media-pipeline 负责“产生与处理”
- routing-session 负责“去向”
- recording 负责“持久化消费”

---

#### Control Flow（控制流）

```text
(ui-system | remote-control) → routing-session → system behavior
```

- ui-system：人类输入
- remote-control：外部系统输入
- routing-session：统一调度入口

---

### Key Insight

- Data Flow 与 Control Flow **严格分离**
- routing-session 是两者的交汇点

---

## 4. Collaboration Patterns

### 4.1 Pipeline → Routing → Consumers

标准数据路径：

```text
media-pipeline
    ↓
routing-session
    ↓
recording
```

特点：

- pipeline 不关心消费方
- routing 负责解耦
- consumer 独立演化

---

### 4.2 Control → Routing → Execution

标准控制路径：

```text
ui-system / remote-control
        ↓
routing-session
        ↓
target feature（recording / pipeline 等）
```

特点：

- 控制入口统一
- 执行目标解耦
- 支持多控制源并存

---

### 4.3 Runtime Isolation Pattern

```text
preview-mode
    ↓
inject PreviewBridge
    ↓
ui-system (Main.qml)
```

特点：

- UI 完全复用
- 控制路径被替换（PreviewBridge）
- 所有副作用被隔离

---

## 5. Non-Overlapping Guarantees

每个 feature 必须满足：

- 不重复定义他人能力
- 不隐式承担他人职责
- 不跨越边界实现功能

---

### Examples

#### ❌ 错误

- recording 直接处理 pipeline 数据结构
- ui-system 控制数据流路径
- preview-mode 修改系统真实状态或触发外部行为

---

#### ✅ 正确

- recording 只消费 routing 后的数据
- ui-system 只发出控制意图
- routing-session 负责调度
- preview-mode 仅替换执行环境，不引入新业务逻辑

---

## 6. Evolution Rules

### 6.1 新 feature 的归属

所有新 feature 必须：

- 归属于这 6 个能力域之一
- 或明确证明是新的能力维度

---

### 6.2 扩展方式

- 行为变化 → 新 feature（supersede）
- 实现优化 → refactor
- 行为错误 → bugfix

---

### 6.3 不允许的演化

- 在现有 feature 内混入其他能力
- 通过“临时逻辑”跨 feature 边界
- 用 implementation 替代 capability

---

## 7. Summary

### Core Conclusions

1. 系统由 6 个不可约能力构成，形成最小完备集合
2. Data Flow 与 Control Flow 必须分离
3. routing-session 是系统的结构性中枢
4. recording 是数据消费能力，而非数据源
5. preview-mode 是安全执行环境能力，而非数据消费或观测能力
6. ui-system 与 remote-control 是两类不同输入源
7. feature 边界必须长期稳定，禁止语义漂移

---

### One-Sentence Principle

> 系统结构由能力决定，能力通过协作形成整体行为，而不是通过嵌套或阶段组织。
