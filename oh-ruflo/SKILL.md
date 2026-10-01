---
name: oh-ruflo
description: >
  企业级多智能体协同底座与蜂群编排技能（基于开源项目 Ruflo / 原 claude-flow）。
  核心理念“Agent = Model + Harness”：模型负责推理思考，Harness 负责提供环境沙箱、跨会话记忆、314+ MCP 工具与分布式蜂群编排。
  具备分层蜂群协调（Hierarchical Swarm）、防漂移拓扑架构（Anti-Drift Topology）、3 阶模型智能路由（确定性脚本→轻量模型→深度推理模型）
  以及基于 HNSW 向量检索的长效持久记忆。
  当任务涉及大型复杂项目重构、多角色协同开发、跨多机 Agent 联邦、或需要调度复杂 Agent Swarm 时触发。
  触发词包括 "ruflo", "oh-ruflo", "多agent编排", "agent swarm", "蜂群编排", "智能体协作", "多模型路由" 等。
metadata:
  version: 1.0.0
  source: "https://github.com/ruvnet/ruflo"
---

# oh-ruflo: 企业级多智能体蜂群编排底座 (Multi-Agent Harness)

在应对超大型项目改造或高复杂度工程时，单智能体往往会受限于上下文长度和单一角色视角，容易出现幻觉与方案漂移。
**Ruflo** 提出了 **Agent = Model + Harness** 架构：大模型是“大脑”，Harness 是“身体与外骨骼”——提供记忆存取、防漂移协作拓扑和精准的工具沙箱。

---

## 一、核心编排拓扑 (Swarm Topologies)

```
       【分层蜂群 (Hierarchical Swarm)】              【网状蜂群 (Mesh Swarm)】
                 ┌──────────┐                          ┌──────────┐
                 │ Lead/Arch│                          │ Agent A  ├──────┐
                 └────┬─────┘                          └────┬─────┘      │
        ┌─────────────┼─────────────┐                       │            ▼
        ▼             ▼             ▼                       │       ┌──────────┐
   ┌─────────┐   ┌─────────┐   ┌─────────┐                  ├──────►│ Agent B  │
   │ Coder   │   │ Reviewer│   │ Tester  │                  │       └────┬─────┘
   └─────────┘   └─────────┘   └─────────┘                  ▼            │
  (主控拆解任务，分发专职子智能体，防漂移拓扑)         (同级智能体点对点接力，自主协商)
```

1. **分层拓扑（推荐，防漂移）**：由架构师/主控 Agent 全局掌握实施计划与验收标准，分发给 55+ 种专职智能体（编码员、测试员、安全审计员），避免单智能体越级导致上下文失真。
2. **网状拓扑**：适合流水线式数据流转与多专家独立并联审查。

---

## 二、三阶模型动态路由体系 (3-Tier Model Routing)

为了在工程质量与 Token 成本之间取得最优解，Ruflo 建立了 3 阶调度分工：

| 阶层 | 承担角色 | 典型任务 | 成本与延迟 |
| :--- | :--- | :--- | :--- |
| **Tier 1: 确定性代码** | 本地脚本 / AST Codemod | 格式化、规则正则校验、代码重命名、死引用清除 | 0 Token / 毫秒级 |
| **Tier 2: 敏捷高效模型** | Flash / 轻量通用模型 | 编写单元测试用例、简单模块实现、语法修复、文档抽取 | 低成本 / 秒级响应 |
| **Tier 3: 深度推理模型** | Pro / Reasoner / 旗舰模型 | 核心领域建模、跨模块重构、架构对抗审查、复杂算法优化 | 高精度 / 深度思考 |

---

## 三、快速上手与常用命令

Ruflo 封装在 `@claude-flow/cli` 与 `ruflo` 中，通过 CLI 快速驱动：

### 1. 项目级初始化与自愈检查
```bash
# 1. 在当前工程目录初始化 Harness 运行时与 MCP 配置
npx ruflo init

# 2. 一键体检与依赖自愈修复 (检查 Node 20+, MCP 通信, 向量数据库)
npx ruflo doctor --fix

# 3. 动态发现当前项目适配的插件
npx ruflo discover-plugins
```

### 2. 蜂群启动与任务派发
```bash
# 启动分层编排蜂群（主控 + 专职角色）
npx ruflo swarm init --topology hierarchical --agents coder,reviewer,tester

# 启动任务执行
npx ruflo task run --plan "实现系统从单机内存缓存迁移至分布式 Redis 方案"
```

### 3. 持久记忆检索 (HNSW 向量检索)
Ruflo 通过本地嵌入与 HNSW 向量索引支持跨会话记忆，避免反复初始化认知：
* `mcp__claude-flow__memory_store`: 将架构决策与接口规范存入知识库。
* `mcp__claude-flow__memory_search`: 通过语义相关性快速召回过往踩坑记录与设计准则。

---

## 四、何时使用与何时回避 (Boundaries)

* ✅ **强烈推荐使用的场景**：
  * 大型代码库全量迁移（如从 JS 迁移到 TS，微服务解耦）。
  * 涉及多视角对抗的代码生产（开发智能体写代码 + 质询智能体挑刺 + 测试智能体验证）。
  * 跨越数天、多次重启的长期工程任务（依赖持久向量记忆维持连续性）。
* ❌ **不建议使用的场景**：
  * 单文件的小修小补、普通 Bug 修复（单 Agent 完全胜任，引入 Swarm 属于过度工程，违背 `oh-ponytail` 原则）。
  * 简单的问答、翻译或纯文本润色。
