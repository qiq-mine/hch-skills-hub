# Checklists (AI Native Repo)

## 新仓库启动（Phase 1，当天可完成）

- [ ] AGENTS.md（50–150 行，frontmatter 四字段齐）
- [ ] harness.yaml（blocking 至少 tests / spec-validate / secret-scan）
- [ ] rules/ 两件套（agent-permissions.md、security.md）
- [ ] .env.example（CI 扫一遍确认无真实密钥）
- [ ] env/Taskfile.yml（setup / test / lint 本地跑通）
- [ ] docs/architecture.md（一页）+ adr/ 第一条
- [ ] PR 模板（含"测试证据 / 风险说明"两栏）

## PR 合并前

- [ ] 测试证据已贴
- [ ] spec 变更走 delta，未直接改原文件
- [ ] AGENTS.md / skills / prompts / rules 变更有人审
- [ ] secret 扫描通过

## 季度防腐

- [ ] AGENTS.md 回归评审（当测试套件跑一遍）
- [ ] last-verified 超期文档：更新或归档
- [ ] 连续 6 个月未触发的 skill：进待删除清单
- [ ] 换工具演练（每年至少一次，抽查）

## 验收标准（换工具演练 / 度量）

1. **换工具演练通过**：新工具只读 harness.yaml + AGENTS.md，走完一次 changes/ 提案。
2. **一次通过率**：agent 生成的 PR 一次合入比例，试点后提升。
3. **违规拦截数**：CI 拦下的密钥提交、越权修改、缺失测试证据。
4. **救火时长**：agent 写坏代码后人修复的平均耗时，下降。
