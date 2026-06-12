# 🧪 Virtual Lab Agent (自动化实验室多智能体调度中枢)

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D.svg)

本项目是一个面向 **AI for Science (数字孪生/自动化实验室)** 赛道的软硬结合高并发调度系统。旨在通过大语言模型 (LLM) 与高频异步网络通信，实现从自然语言指令到多端底层硬件（光电传感器、工业机械臂）的自动化编排与无阻塞执行。

## ✨ 核心特性与系统架构

* **🧠 核心中枢 (LLM Agent Core):** 基于大模型构建自然语言解析引擎，通过严格的提示词工程 (Prompt Engineering) 将非结构化语言精准拆解为机器可读的 DAG 任务队列 (JSON)。
* **⚡ 高并发异步网关 (Asynchronous Gateway):** 采用 `FastAPI` + `asyncio` 架构。通过 `BackgroundTasks` 将耗时的硬件调度操作转移至后台池，杜绝主线程阻塞，保证 API 的极速响应。
* **💾 容灾与状态机 (State Machine & Redis):** 引入 `Redis` 构建高频状态缓存。前端下发任务后秒回 Task ID，通过 UUID 轮询查询任务断点与执行状态，支持系统崩溃时的异常捕获与状态回溯。
* **🔌 硬件抽象层 (Device Mock & OOP):** 基于面向对象 (OOP) 与设计模式，构建了高内聚的 `BaseDevice` 接口规范，完美模拟光电显微镜成像与机械臂运动耗时。
* **💻 赛博终端大屏 (Full-stack UI):** 采用原生 `Vue 3` 构建前端中控大屏，支持跨域 (CORS) 通信，实现亚秒级的终端日志滚动与状态高亮反馈。

## 🚀 快速启动

1. **环境安装:**
   ```bash
   pip install fastapi uvicorn redis fakeredis pydantic zhipuai
