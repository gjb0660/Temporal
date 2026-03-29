# Testing

## Overview

测试是保证系统行为可验证、可收敛的基础机制。

在 AI 参与开发的环境中，测试不仅用于验证正确性，还用于：

- 限制生成空间
- 提供收敛方向
- 防止 spec 与 code 偏离

测试的核心不是覆盖率，而是**可验证性（verifiability）与可收敛性（convergence）**。

---

## TDD as a Control Loop

测试驱动开发（TDD）是一种闭环机制：

```text
Red → Green → Refactor
```

它不是编码技巧，而是一种**约束系统演进的控制结构**。

---

## Red Phase（失败先行）

先写测试，并确保其失败。

目的：

- 明确期望行为（expected behavior）
- 防止“实现驱动设计”
- 将模糊需求转化为可验证条件

约束：

- 测试必须失败（否则无效）
- 失败原因必须明确且单一

---

## Green Phase（最小通过）

编写最少代码，使测试通过。

目的：

- 验证行为是否成立
- 快速建立“spec → code”的对应关系

约束：

- 不允许引入额外逻辑
- 不追求结构优化
- 仅关注通过测试

---

## Refactor Phase（结构收敛）

在测试通过的前提下，优化代码结构。

目的：

- 消除重复与偶然复杂度
- 提升可读性与可维护性
- 收敛到更稳定的实现形态

约束：

- 不改变外部行为
- 所有测试必须持续通过

> Refactor 是 TDD 容易被忽视的阶段

---

## Key Properties of TDD

### Behavior First

测试定义行为，而不是验证实现。

---

### Minimal Progress

每一步只做最小必要改变：

- Red：定义一个失败
- Green：通过一个测试
- Refactor：改善一个结构问题

---

### Continuous Validation

系统始终处于“可验证状态”：

- 任意时刻都可运行测试
- 不存在“暂时不可用”的中间态

---

## Why Testing Matters in AI-driven Development

在 AI 参与生成代码时：

### 1. 抑制幻觉

测试提供明确边界，限制不符合预期的生成。

---

### 2. 防止语义漂移

测试将行为固定下来，避免代码逐步偏离原始意图。

---

### 3. 支持迭代收敛

通过 Red-Green 循环，使复杂问题逐步逼近正确解。

---

## Testing as Specification

测试本质上是一种**可执行规范**：

- Acceptance → 测试用例
- 行为 → 断言
- 边界 → 失败场景

当测试存在时：

> 系统行为不再依赖描述，而依赖验证。

---

## Anti-Patterns

### Test After Implementation

先写实现再补测试，会导致：

- 行为未被约束
- 测试失去设计意义

---

### Multi-Concern Tests

一个测试覆盖多个行为：

- 失败原因不明确
- 难以定位问题

---

### Over-Specifying Implementation

测试依赖内部实现细节：

- 降低重构空间
- 增加维护成本

---

## Summary

- 测试的本质是建立可验证性，而不是提高覆盖率
- TDD 是一个控制系统演进的闭环，而不是编码流程
- Red / Green / Refactor 分别对应：定义行为、验证行为、收敛结构
- 在 AI 场景下，测试是抑制幻觉与防止偏离的核心机制

> 没有测试，系统行为无法收敛；没有收敛，spec 就无法成为真正的执行真源。
