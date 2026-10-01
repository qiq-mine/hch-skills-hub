# 上游同步记录（SYNC）

本目录为上游开源项目的 **vendored 全量拷贝**，而非 git submodule。

## 上游信息

- 项目：阿里 `open-code-review`（AI 代码审查工具，Go 实现）
- 上游地址：https://github.com/alibaba/open-code-review
- 许可证：以本目录内上游自带的 LICENSE 文件为准

## 同步历史

| 日期 | 方式 | 说明 |
|------|------|------|
| 2026-10-01 | 手动全量拷贝 | 首次 vendored；未记录上游具体 commit/tag |

> 注意：首次拷贝时未记录上游版本号。如需精确追溯，建议下次同步时先
> 在上游仓库确认当前 release/tag 或 commit SHA，再执行同步。

## 后续同步步骤

1. 在上游仓库查看最新 release 或 commit：
   `https://github.com/alibaba/open-code-review/releases`
2. 将上游指定版本完整下载/克隆到临时目录。
3. diff 本目录与上游新版本，确认变更范围（特别注意上游 LICENSE /
   NOTICE 变更）。
4. 用新版本整体替换本目录内容（保留本文件 SYNC.md）。
5. 在上表追加一行同步记录（日期、上游版本、同步人）。
6. 跑一遍 `skills/open-code-review` 相关技能的冒烟验证，确认 Agent
   调用方式未发生破坏性变更。

## 替代方案

如希望改为自动跟踪上游，可将本目录替换为 git submodule：

```bash
git rm -r open-code-review
git submodule add https://github.com/alibaba/open-code-review.git open-code-review
```

改用 submodule 后本文件可删除，同步改为 `git submodule update --remote`。
