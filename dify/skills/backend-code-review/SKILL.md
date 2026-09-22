---
name: backend-code-review
description: "Dify 后端代码审查技能。面向 Python/Flask/SQLAlchemy 架构，审查控制器、服务层、领域模型、存储库抽象、数据库迁移与并发保护。支持 Git 变更、特定文件或 diff 审查。分级输出 P0-P3 缺陷。Triggers: backend-code-review, /backend-code-review, 后端审查, 后端代码审查, SQLAlchemy审查, 数据库迁移审查."
---

# Backend Code Review (Dify 后端工程审查)

面向生产级 Python / Flask / SQLAlchemy 后端代码的精准审查技能。基于 Dify 后端工业级标准，严格排查可复现的代码缺陷、架构侵蚀、租户隔离隐患与数据一致性问题。

## 审查原则：Evidence First (证据优先)

1. **确立审查边界**：获取指定的审查范围（Git staged/unstaged diff、特定 commit、分支对比或目标代码文件）。
2. **理解行为契约**：阅读变更代码、关联的所有者模块、邻近单元测试以及定义契约的 docstrings 与注释。
3. **追踪关键链路**：仅在决定正确性时追踪调用方、持久化边界、鉴权隔离、数据模型生成与外部 I/O。
4. **拒绝无据猜想**：仅上报能对应到可观察失败、违背架构契约、越过安全边界、数据完整性风险或可证明的维护性缺陷。

## 规则路由 (Rule Routing)

根据 diff 触及的代码范畴，按需加载对应规则包：

| 变更范围 | 对应规则文件 | 核心审查要点 |
|---------|------------|-------------|
| 数据模型与迁移 | [`references/db-schema-rule.md`](references/db-schema-rule.md) | 禁止 `@property` 跨表查询、强制包含 `tenant_id`、排查冗余索引、跨数据库方言可移植性 (PostgreSQL/MySQL)、数据迁移双向兼容 |
| 分层依赖与模块边界 | [`references/architecture-rule.md`](references/architecture-rule.md) | Controller 保持轻量（无业务逻辑）、严格单向依赖 (Controller → Service → Core/Domain)、`api/libs/` 保持业务无关 |
| 数据表访问与仓库抽象 | [`references/repositories-rule.md`](references/repositories-rule.md) | 已有 Repository 强制复用、复杂查询下沉至 Repository、禁止跨层直接使用 ad-hoc SQLAlchemy 查询绕过抽象 |
| SQLAlchemy 会话与并发 | [`references/sqlalchemy-rule.md`](references/sqlalchemy-rule.md) | 显式 Session 与事务边界控制、强制 `tenant_id` 查询过滤、SQLAlchemy 表达式优于原生 SQL、写入路径并发保护（乐观锁/分布式锁/行锁） |

> 当无专有规则包匹配时，直接审查核心正确性、安全漏洞、行为回归与测试覆盖。

## 严重级别与输出规范 (Severity & Output)

发现项严格按以下严重级别由高到低排序呈现：

- **P0 (阻断级)**：安全/隐私泄露、数据损毁/丢失、多租户穿透或生产级宕机。
- **P1 (严重级)**：用户可见的功能回归、越权漏洞、破坏公开接口契约、主业务流程中断。
- **P2 (重要级)**：具体正确性问题、严重性能退化（如 N+1 查询）、事务未受控、缺乏必要并发防护、破坏分层架构。
- **P3 (建议级)**：轻微的代码整洁度建议；仅在用户明确要求全面审计时输出。

### 输出格式

每个审查意见包含：
1. **[级别] 文件路径:行号**（例如 `[P1] api/services/app_service.py:142`）
2. **问题描述与违反契约**：明确指明违反了哪项规则或引发何种运行时失败。
3. **影响面 (Impact)**：说明在何种场景下会导致错误（如并发冲突、跨租户泄露）。
4. **修复建议与代码范例 (Fix Direction)**：给出精简、可落地的修改方案。

若未发现问题，明确回复 `No issues found.` 并注明存在的客观验证盲区（如外部依赖未 mock 验证等）。禁止输出客套吹捧或未经请求的主动代写承诺。
