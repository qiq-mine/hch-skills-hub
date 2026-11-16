# streamline

AI 长期项目护航套件：一个 Antigravity 插件，用 8 个按需触发的技能覆盖一个人加 AI 长期开发复杂项目时的各个阶段，从技术选型到发布。

| 阶段 | 技能 |
|------|------|
| 开工前 | `tech-recon`（选型调研）、`readable-proposal`（可读方案） |
| 开发中 | `delegate-execute`（分工执行）、`layered-testing`（分层测试）、`project-governance`（项目治理）、`cut-losses`（疑难止损） |
| 收尾 | `release-gate`（发布门禁）、`safe-mode`（安全模式） |

完整说明和路由表见 [SKILL.md](./SKILL.md)，版本记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 安装

在项目的 `.agents/plugins.json` 里加上：

```json
{
  "entries": [
    { "path": "streamline" },
    { "path": "pstack" }
  ]
}
```

pstack 可选。装了它，审查和验证环节会按 pstack 的对应技能执行；没装时用各技能里写的替代方案。

## 许可证

MIT
