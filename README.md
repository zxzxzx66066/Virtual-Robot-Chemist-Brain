# 🧪 Virtual Lab Agent (自动化实验室多智能体调度中枢)

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D.svg)

本项目是一个面向 **AI for Science (数字孪生/自动化实验室)** 赛道的软硬结合高并发调度系统。旨在通过大语言模型 (LLM) 与高频异步网络通信，实现从自然语言指令到多端底层硬件（光电传感器、工业机械臂）的自动化编排与无阻塞执行。

## ⚙️ 系统架构设计

系统采用前后端分离与多级异步容灾架构：

```mermaid
graph TD
    A[Vue3 赛博中控大屏] -->|HTTP POST 自然语言| B(FastAPI 高并发网关)
    B -->|分配 Task ID| A
    B -->|异步丢入后台任务池| C{GLM-4 Agent 大脑}
    C -->|思考与 DAG 拆解| D[(Redis 状态机)]
    D -.->|前端高频轮询状态| A
    C -->|下发结构化 JSON 队列| E[BaseDevice 硬件抽象层]
    E --> F[UR5 机械臂模拟]
    E --> G[Zeiss 显微镜模拟]
    F --> D
    G --> D






















## ✨ 核心特性



* **🧠 智能体任务编排 (Agent Orchestration):** 通过深度 Prompt Engineering，约束大模型输出严格的 JSON 格式，将非结构化自然语言精准转化为机器可读的执行队列。

* **⚡ 异步无阻塞网关 (Asynchronous I/O):** 采用 `FastAPI` + `BackgroundTasks`，将动辄几小时的物理采样任务转入后台执行，主线程秒级返回，极大提升 API 吞吐量。

* **💾 Redis 容灾与状态轮询:** 引入缓存中间件维护全局状态字典。前端通过 UUID 轮询获取亚秒级进度，具备系统宕机时的异常捕获与断点追溯能力。

* **🔌 硬件数字孪生 (OOP Mock):** 运用策略模式与基类抽象 (`BaseDevice`)，解耦软硬件通信协议，完美模拟真实光学仪器与机械臂的物理延迟，具备极强的水平扩展性。

