# Refactoring Required and Elective Checklist

## Purpose

This checklist is required by `$converge-commit` in both `single` and `subagent`
mode.

Use it to enforce two rules:

1. identify and classify all Chapter 3 smells in mandatory range
2. apply Chapter 6 micro-refactors whenever safe local cleanup is possible

## Two-Layer Enforcement

1. Hard fix in current commit (`must-fix-now`):
   - condition: smell is inside touched plus one-hop range and can be safely
     fixed in this commit
   - action: fix now
   - hard rule: if any such smell exists, apply at least one Chapter 6
     micro-refactor
   - gate impact: unresolved item sets `pollution-gate=fail` or `cleanup=fail`
2. Planned escalation (`must-report-plan`):
   - condition: fix crosses boundaries or requires broad refactor not safe for
     this atomic commit
   - action: record in `remaining-risk` and add
     `refactor-plan-suggestions`
   - gate impact: does not directly block by itself unless it causes
     `semantic-gate` or `static-gate` failure in mandatory range

## Required Smell Coverage (Chapter 3, All 24)

Every review must check and classify the full list below.

1. `3.1` Mysterious Name / 神秘命名
2. `3.2` Duplicated Code / 重复代码
3. `3.3` Long Function / 过长函数
4. `3.4` Long Parameter List / 过长参数列表
5. `3.5` Global Data / 全局数据
6. `3.6` Mutable Data / 可变数据
7. `3.7` Divergent Change / 发散式变化
8. `3.8` Shotgun Surgery / 霰弹式修改
9. `3.9` Feature Envy / 依恋情结
10. `3.10` Data Clumps / 数据泥团
11. `3.11` Primitive Obsession / 基本类型偏执
12. `3.12` Repeated Switches / 重复的 switch
13. `3.13` Loops / 循环语句
14. `3.14` Lazy Element / 冗赘的元素
15. `3.15` Speculative Generality / 夸夸其谈通用性
16. `3.16` Temporary Field / 临时字段
17. `3.17` Message Chains / 过长的消息链
18. `3.18` Middle Man / 中间人
19. `3.19` Insider Trading / 内幕交易
20. `3.20` Large Class / 过大的类
21. `3.21` Alternative Classes with Different Interfaces / 异曲同工的类
22. `3.22` Data Class / 纯数据类
23. `3.23` Refused Bequest / 被拒绝的遗赠
24. `3.24` Comments / 注释

## Required Micro-Refactor Toolkit (Chapter 6, All 11)

When a safe local smell fix exists in mandatory range, apply at least one
method from this set:

1. `6.1` Extract Function / 提炼函数
2. `6.2` Inline Function / 内联函数
3. `6.3` Extract Variable / 提炼变量
4. `6.4` Inline Variable / 内联变量
5. `6.5` Change Function Declaration / 改变函数声明
6. `6.6` Encapsulate Variable / 封装变量
7. `6.7` Rename Variable / 变量改名
8. `6.8` Introduce Parameter Object / 引入参数对象
9. `6.9` Combine Functions into Class / 函数组合成类
10. `6.10` Combine Functions into Transform / 函数组合成变换
11. `6.11` Split Phase / 拆分阶段

## Elective Application Guidance

Elective means optional only after all hard rules above are satisfied.

1. prefer the smallest change that removes a concrete smell cause
2. prefer semantic-preserving moves before structural expansion
3. do not add compatibility scaffolding just to avoid deleting dead paths
4. if all viable fixes are cross-boundary, keep commit minimal and escalate
   using `refactor-plan-suggestions`

## Review Output Mapping

Record checklist outcomes in skill outputs:

1. smell classification -> `findings`
2. chosen Chapter 6 actions -> `reduction-decisions`
3. unresolved cross-boundary debt -> `remaining-risk`
4. dedicated follow-up proposal -> `refactor-plan-suggestions`

## Occam Evidence Mapping (Hard)

`$converge-commit` requires explicit mapping into
`occam-reduction-proof` for each convergence round.

1. if a safe local reduction exists in mandatory range:
   - apply reduction now
   - map each change to one item in `reduction-decisions`
   - include removed or merged entity evidence in `occam-reduction-proof`
2. if no safe local reduction exists:
   - provide explicit "no safe reduction" proof in `occam-reduction-proof`
   - include why each candidate is unsafe or cross-boundary
   - record unresolved items in `remaining-risk`
3. if mandatory-range `must-fix-now` smell exists but no reduction evidence is
   provided:
   - set `pollution-gate=fail`
   - set `cleanup=fail`
   - block commit exit
