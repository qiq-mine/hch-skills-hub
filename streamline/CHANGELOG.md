# Changelog

## 0.2.0 — 2026-11-17

### Breaking

- 插件更名为 `streamline`（原 `steamline`），主智能体更名为 `streamline-agent`。`.agents/plugins.json` 和 `.agents/skills.json` 里的路径要同步更新。
- 「方案先于代码」保留为常驻规则，并明确优先于 pstack 的 never-block。触发条件从笼统的"超过一小时"细化为三条：超过一小时、跨模块或改变用户可见行为、删除或批量改写。小改动仍按 never-block 直接做。「客户端必须设计安全模式」等发布类约束移出常驻规则。

### Fixed

- `release-gate` 的 pre-push hook 改为可用版本：配套 `test-and-stamp.sh` 记录测试通过的 commit，推送 `v*` tag 时检查版本文件和更新日志。已在临时仓库验证 9 种场景。
- `cut-losses` 两个排查者要求用不同模型，不再比较模型自报的置信度，改为按证据档位（已验证 / 可验证 / 推测）对比。
- 修正 pstack 技能名 `prove-it-works` → `principle-prove-it-works`。
- 去掉子技能和主入口之间、`readable-proposal` 和 `delegate-execute` 之间重叠的触发词。
- 路由表只保留在 `SKILL.md` 一处，`streamline-agent` 引用它，并写明怎么判断 pstack 是否可用。
- 子技能不再写死模型名，改为判断 / 执行角色；装了 pstack 时按 `setup-pstack` 的配置选模型。
- 「自动调用 pstack」统一改为「读取对应技能的 SKILL.md 并按它执行」。
- `layered-testing`：拆分测试层、删除无用测试都改为先列清单交人确认。
- `safe-mode`：补上崩溃检测要放在重型初始化之前、安全模式自身崩溃时的兜底页、启动标记误报的说明。
- `release-gate` 回滚模板里的 tag 不再叫分支。
- `project-governance` 示例规则换成通用的错误处理例子。
- `tech-recon` 的 AI 掌握度改为用小任务实测。
- 补充 README、LICENSE、CHANGELOG。

## 0.1.0 — 2026-11-17

- 首个版本：8 个技能（tech-recon、readable-proposal、delegate-execute、layered-testing、project-governance、cut-losses、release-gate、safe-mode）、常驻规则和主路由智能体。
