# Testing

## 1. Overview

本文件描述当前项目测试的重点风险面与推荐关注点。
它不是执行步骤，也不是 Code Protocol；它仅提供可复用的测试关注材料。

## 2. Stable Test Facts

- 当前单元测试与集成测试使用 `unittest`。
- unit test 应尽量避免真实网络与非确定性时间因素。
- fake sockets、受控 fixtures、确定性输入更适合该项目的协议与状态测试。

## 3. High-Value Coverage Areas

- protocol parsing
- reconnect behavior
- malformed message handling
- recorder transition behavior
- recording filename contract
- timestamp presence in recording outputs

## 4. Readability Facts

- test helper 越大，越容易掩盖因果关系。
- “一个失败只表达一个原因”更利于定位状态机与协议解析问题。

## 5. Summary

- 当前测试重点不在“跑得多”，而在“覆盖高风险状态转换与协议边界”。
- 该项目特别依赖确定性测试输入。
- filename contract 与 recorder transition 是高价值回归点。
