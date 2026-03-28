# UI Specific Contracts: Defining Stable User-Facing Interface Constraints

## Overview

UI Contract 是 Contract 体系中的一个特化分支，用于描述**用户可感知的界面元素及其稳定交互语义**。

与通用 Contract 不同，UI Contract 直接锚定用户认知中的界面结构：

- 不关注实现（组件 / QML / DOM）
- 不关注具体布局（grid / flex / pixel）
- 关注的是：**用户在某个位置，始终能看到什么、做什么**

---

## Why UI Needs Specific Contracts

在系统演进过程中，UI 往往是最容易发生变化的部分：

- 布局调整
- 组件替换
- 技术栈迁移
- 视觉改版

如果缺乏稳定约束：

- 用户操作路径会被破坏
- 认知成本不断上升
- 行为预期变得不稳定

因此需要一种机制，使得：

> 在 UI 可持续演进的同时，用户心智模型仍然保持稳定

UI Contract 正是用于表达这一层稳定性。

---

## Core Idea

UI Contract 关注的不是“界面长什么样”，而是：

> **界面中的哪些位置，是用户长期依赖的稳定语义锚点**

这些锚点通常包括：

- 导航位置
- 主要操作区域
- 关键数据展示区
- 控制入口

一旦形成用户习惯，这些位置就不再只是实现细节，而成为系统语义的一部分。

---

## File Organization

UI Contract 通常组织在：

```text
specs/contracts/ui/
````

每个文件对应一个稳定 UI 元素，例如：

```text
ui/main-window.md
ui/left-sidebar.md
ui/source-sphere-view.md
```

这种结构表达的是：

> Contract 的粒度，与用户可感知的界面元素一致

而不是与代码结构或组件层级一致。

---

## Naming Principle

UI Contract 的命名遵循一个直接原则：

> **文件名应与页面中的稳定元素一一对应**

例如：

- `MainWindow` → `ui/main-window.md`
- `LeftSidebar` → `ui/left-sidebar.md`
- `SourceSphereView` → `ui/source-sphere-view.md`

命名来源于用户认知，而不是实现命名或技术术语。

---

## Element as Semantic Anchor

在 UI Contract 中，每个元素承担“语义锚点”的角色。

例如：

- LeftSidebar 不只是一个视觉区域
- 它代表：

  - 全局导航入口
  - 对象切换位置
  - 稳定的空间参考点

Contract 约束的不是：

- 使用何种组件实现

而是：

- 始终承担什么语义角色

---

## Contract Scope in UI

UI Contract 通常围绕三类稳定语义：

### 1. Interaction Semantics

- 用户在该位置可以执行什么操作
- 操作是否具有可预期性

---

### 2. Visibility and Hierarchy

- 元素是否持续可见
- 在信息层级中的位置

---

### 3. Cognitive Consistency

- 用户是否可以依赖该位置形成习惯
- 不同场景下语义是否一致

这些关注点与具体布局实现无关。

---

## What UI Contract Does NOT Define

UI Contract 不涉及：

- 具体布局方式（上下 / 左右 / grid）
- 样式细节（颜色 / 字体 / spacing）
- 技术实现（QML / React / HTML）

这些属于实现层或 Feature 层的职责。

---

## Stability Consideration

UI Contract 的 `stability` 通常为：

```text
flexible
```

这并不意味着其重要性较低，而是反映：

- UI 表现形式会持续演进
- 视觉与布局具有变化空间

但稳定的部分仍然存在：

- 语义位置
- 操作路径
- 认知结构

UI Contract 关注的是这些长期不变的部分。

---

## Evolution Pattern

UI Contract 的变化通常表现为：

### 1. Layout Changes

- 元素位置调整
- 布局方式变化

只要语义锚点未改变，Contract 通常仍然成立。

---

### 2. Visual Redesign

- 样式更新
- 组件替换

只要用户仍能识别该元素，其语义保持不变。

---

### 3. Semantic Shift（较少发生）

- 元素职责改变
- 用户操作路径改变

这类变化通常意味着：

> 原有 Contract 不再成立，需要重定义语义

---

## Relationship with Feature

UI Contract 与 Feature 之间是正交关系：

- Feature 描述“功能如何实现”
- UI Contract 描述“用户如何与功能交互”

Feature 可以演进实现方式，

但 UI Contract 使交互语义保持稳定。

---

## Relationship with Agent

对于 Agent 来说，UI Contract 提供：

- 稳定的界面锚点
- 可推理的交互边界
- 对用户习惯的隐式约束

在修改 UI 时：

- 实现可以变化
- 但语义锚点通常保持不变

---

## Mental Model

UI Contract 可以理解为：

> **用户脑海中的界面地图**

而不是代码中的组件结构。

- 组件可以替换
- 布局可以调整
- 技术可以变化

但这张“地图”通常应保持一致。

---

## Summary

UI Specific Contract 的核心在于：

- 将 UI 从实现细节提升为语义结构
- 将用户习惯转化为系统约束表达
- 在持续演进中保持认知一致性

它并不阻止 UI 变化，

而是使变化仍然可理解。

> UI 可以改变形态，但不改变用户的方向感。
