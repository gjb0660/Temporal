# Decision Not Only from Prompts

it may also be introduced through code

## Overview

在理想的 Spec-Driven 流程中，决策通常先以 prompt 或 spec 的形式出现，再进入 code。
但在真实的人机协作里，决策并不总是先以自然语言出现。

很多时候，新的局部决策先出现在代码里：

* 人类 reviewer 对 AI 产出的代码做了微重构
* 人类修正了某个细节行为
* 人类直接用一段暂存差异表达“这里应该这样做”
* 这段代码甚至还不完整，只是包含 `TODO`、占位符或骨架

这类变化往往不是噪音，而是在用 code 这种语言表达新的设计判断。

问题在于，AI 很容易坚持旧 spec，把这些改动当成漂移，甚至试图回退它们。
于是系统出现一个典型断裂：

* **代码已经变了**
* **spec 还停留在旧决策**
* **Agent 继续按旧 spec 理解世界**

这篇文档讨论的，就是如何理解这种断裂，以及为什么需要一个受控的辅助流程，把“人类通过 code 表达的新决策”重新收敛回 spec。

---

## The Pain

这个问题并不是“谁对谁错”，而是两种工作习惯之间的天然摩擦。

人类更习惯：

* 先改代码
* 再补文档
* 用最直接的实现表达意图

而极简 ESPC 更强调：

* 先澄清 Goal / Facts / Decision
* 再进入 code
* 保持 spec 与 code 同步演进

当这两种节奏相遇时，会出现几个现实痛点。

### Spec Drift After Human Review

AI 生成了一版代码后，人类 reviewer 会做少量但关键的调整。
这些调整常常不会第一时间同步回 spec。

于是下一轮 Agent 看到的是：

* spec 说 A
* code 更接近 B

如果 Agent 机械坚持 spec，就会把 B 视为错误或噪音。

### Code as Unspoken Decision

有些修改并不是“实现细节”，而是新的局部决策。
例如：

* stop 语义从 best-effort 改成 flush 完成后才算成功
* 某个错误分支从 silent failure 改成显式反馈
* 某个接口从宽松输入改成更严格约束

这些变化已经超出了“代码整理”，但它们并没有先写成自然语言。

### Human Intent Gets Lost

对人类来说，暂存区里的差异已经很明确：

> 这是我改的，不要回退，它代表新的判断。

但如果缺少一个明确的辅助机制，Agent 往往无法稳定理解这一点。
结果就是：

* 人类在修正 AI
* AI 却在下一轮修正人类

真正丢失的不是代码，而是**决策的归属**。

---

## Why This Is Not a Reversal of SSOT

表面看，这像是在允许 `code → spec`，似乎会破坏 Spec 是单一真源的原则。
但更仔细地看，问题并不是“代码能否影响 spec”，而是：

> **代码是否获得了最终裁决权。**

只要最终长期成立、被引用、被执行的仍然是 spec，那么 SSOT 并没有被放弃。

这里更准确的理解是：

* code 可以承载新的现实
* human 可以通过 code 表达新的局部决策
* Agent 负责把这种决策翻译回 spec
* 更新后的 spec 重新成为当前真源

换句话说，这不是让 code 取代 spec，
而是让 **human 借 code 提交 decision，再由 Agent 把 decision 收敛回 spec**。

真正危险的情况不是参考 code 更新 spec，
而是默认“只要代码存在，它就天然更对”。
那样才会让实现反过来统治意图。

---

## Decision May Also Introduce Code

通常人们会认为：

* prompt 提出意图
* spec 固化意图
* code 执行意图

但在 human-in-the-loop 场景里，还存在另一种路径：

* 人类直接修改代码
* 代码差异表达一个新的局部判断
* 这个判断再被追认到 spec

于是决策的入口不再只有 prompt。

这并不意味着“prompt 不重要”，而是意味着：

> **决策的载体可以不止一种。**

自然语言适合表达目标、边界和解释。
代码语言适合表达局部行为、结构选择和执行路径。
当人类明确选择用代码表达决策时，这种表达本身就值得被识别。

所以更准确的说法不是：

* decision comes from code

而是：

* **decision may be introduced through code**

代码不是权威本身，但它可以成为决策进入系统的入口。

---

## Why Human Trigger Matters

如果没有额外限制，这套思路会迅速失控。

因为一旦 Agent 开始习惯“按代码补 spec”，它就很容易：

* 自动追认任何实现漂移
* 把偶然状态写进 spec
* 让 spec 退化成 implementation diary

所以这里最关键的不是“能不能从 code 更新 spec”，
而是“谁在授权这件事发生”。

这个辅助流程之所以成立，是因为它带有明确的人类背书：

> 当前 staged diff 是我有意为之。
> 不要回退。
> 把它当作新的已采纳决策，更新到 spec。

这条声明非常重要。
它说明被导入的不是“代码事实本身”，而是“人类确认过的决策”。

于是整个权威关系仍然清楚：

* human intent 提供裁决
* code diff 提供载体
* spec 提供长期真源

---

## Why The Flow Should Be Optional

这类流程不适合变成默认策略。

默认的极简 ESPC 仍然应该是：

* spec 先行
* code 跟随
* spec-code 原子一致

辅助流程的意义，不是替代主流程，而是承认现实中的例外输入。
它更像一种恢复机制，而不是常规模式。

只有当人类显式触发时，这条路径才成立。
否则 Agent 仍应把 spec 作为首要依据，并警惕漂移。

这样设计的原因很简单：

* 避免“例外变默认”
* 避免 code-language decision 被过度泛化
* 避免每次实现偏差都被自动追认

optional 的价值，在于把这条路径严格限制在“确有必要”的时刻。

---

## Why It Must Be One-Shot

即使有了 human trigger，还不够。

如果这次授权会污染同一个会话窗口的后续对话，
Agent 就可能在之后的轮次里继续套用同样的逻辑：

* 你之前允许过一次 code → spec
* 那我这次也继续这么做

这会把“一次性的人工授权”滑成“会话级模式切换”。

因此更合理的理解是：

* 它只针对当前这一次调用
* 只针对当前这批 staged diff
* 只针对当前这一轮产生的 spec patch
* 本轮结束后自动失效

这让整个流程保持：

* 显式
* 局部
* 可审计
* 可失效

也避免了上下文被长期污染。

---

## Partial Code Still Carries Decision

另一个容易被忽略的现实是：
人类不一定会一次把代码写完整。

很多时候，staged diff 只是表达了方向，例如：

* 骨架已经改了
* 分支已经调整了
* 关键语义已经明确了
* 但仍然有 `TODO`、占位符、未补的测试或未完成的边界处理

这说明一个事实：

> 决策的表达可以先于实现的完成。

如果系统只能接受“完整代码”作为 decision carrier，就会错过很多真实的协作场景。
但反过来，如果看到半成品代码就直接宣布完成，又会破坏 spec 的可信度。

所以这里需要区分两个层次：

### Decision Import

从 staged diff 中识别并追认新的局部决策：

* 哪个行为被重新定义了
* 哪个路径被改成新的当前方案
* 哪些事实已经成立

### Execution Continuation

在导入决策之后，Agent 仍然继续正常执行：

* 补完实现
* 修复质量问题
* 跑测试与门禁
* 真实更新 Progress

也就是说，半成品代码可以引入新决策，
但不能伪装成已完成交付。

---

## Decision Is Not Completion

这是整套设计里最需要说透的一点。

人类通过 staged code 表达的，首先是：

* 当前接受的方向
* 当前接受的局部设计
* 当前不应被回退的改变

它不自动等于：

* 已满足 Acceptance
* 已通过验证
* 已完成实现
* 已可提交

所以在这个流程里，Agent 要做两件不同的事：

一是把新的决策翻译到 spec 中；
二是继续像正常极简 ESPC 一样完成闭环。

这样一来：

* `Decision` 可以先更新
* `Plan` 可以随之调整
* `Progress` 仍然只能写真实完成的内容
* 未完成部分仍应继续实现或明确延期

这就避免了“decision import”被误用成“completion shortcut”。

---

## Why Quality Gates Still Matter

如果人类已经明确说“不要回退这段代码”，
是否意味着 Agent 就不该再审查它？

答案显然是否定的。

“不要回退”只说明：

* 这段修改承载了人类确认过的决策

它并不说明：

* 实现已经完整
* 结构已经合理
* 边界已经处理好
* 测试已经充分
* 项目门禁可以跳过

因此，在决策被导入 spec 之后，
Agent 仍然需要承担正常的工程责任：

* 检查代码质量
* 补全当前 Acceptance 所需的实现
* 运行测试和仓库门禁
* 发现问题时继续修正
* 只在真实通过后结束当前闭环

换句话说：

> 人类决定“往哪走”，
> Agent 仍然负责“把这条路走完”。

---

## A More Accurate Mental Model

如果用一句话来理解这套思路，可以这样说：

> 在 human-in-the-loop 场景里，决策不只来自 prompts，也可能先通过 code 被引入，再由 Agent 重新收敛回 spec。

这里的关键不是“反向”，而是“收敛”。

* prompt 是一种决策输入
* code 也是一种决策载体
* spec 仍然是最终沉淀点

于是整个流程并没有背离极简 ESPC，
反而是在现实协作条件下，给 spec-code consistency 增加了一条更稳的恢复路径。

---

## Summary

这个辅助思路试图解决的，不是文档补写这么简单的问题，
而是一个更根本的人机协作断裂：

* 人类通过 code 表达了新的局部决策
* Agent 却仍停留在旧 spec 上

要让系统真正稳定，关键不是让 code 变成真源，
而是允许一种受控的、一次性的、显式授权的 decision import：

* 人类明确声明 staged diff 是有意决策
* Agent 不将其回退
* Agent 将这份决策翻译回 spec
* 然后继续完成实现、质量检查与门禁验证
* 最终由更新后的 spec 再次成为当前真源

因此，这套设计想表达的核心并不是：

> code is the source of truth

而是：

> **decision is not only from prompts.
> it may also be introduced through code.**
