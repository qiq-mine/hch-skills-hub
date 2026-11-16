---
name: release-gate
description: "发布流程程序化：测试门禁、回滚配置、版本号同步。Triggers: release-gate, 准备发版, 发布流程, 发版检查, 上线准备."
---

# release-gate — 发布门禁

> 重要发布条件应该是程序化限制，不是口头约定。

## 触发条件

- 用户说"准备发版"、"上线准备"、"设置发布流程"
- 项目进入持续发版阶段

## 发布检查清单

每次发布前必须通过：

### 必过门禁

| 检查项 | 如何验证 | 不过怎么办 |
|--------|---------|-----------|
| 全量测试通过 | 本地运行完整测试套件 | 修复失败的测试 |
| 无未完成的关键修复 | 检查 issue/任务列表 | 完成或推迟到下个版本 |
| 版本号已更新 | 检查版本配置文件 | 更新版本号 |
| 更新日志已写 | 检查 CHANGELOG 或发布说明 | 补写 |
| 代码已合并到主分支 | 检查 git 状态 | 合并 |

### 可选门禁（根据项目配置）

- [ ] 性能指标未退化（对比上一版基线）
- [ ] 官网/落地页版本信息已同步
- [ ] 安全扫描通过
- [ ] 内测用户反馈无阻断问题

## 程序化限制

尽可能把门禁变成自动拦截，而不是靠记忆。下面两个脚本配合使用：测试通过时记下 commit，推送时检查要推的 commit 有没有记录；推送 `v*` tag 时额外检查版本号和更新日志。

**`scripts/test-and-stamp.sh`**：跑测试，通过后记录当前 commit。工作区有未提交改动时拒绝记录，因为那时测的代码不等于 commit 里的代码。

```bash
#!/usr/bin/env bash
set -euo pipefail
TEST_CMD=${TEST_CMD:-make test}
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "❌ 有未提交的改动，测试结果无法对应到某个 commit，请先提交" >&2
  exit 1
fi
bash -c "$TEST_CMD"
git rev-parse HEAD > "$(git rev-parse --git-dir)/last-test-pass"
echo "✅ 测试通过，已记录 $(git rev-parse --short HEAD)"
```

**`.git/hooks/pre-push`**（记得 `chmod +x`）：

```bash
#!/usr/bin/env bash
set -euo pipefail
STAMP="$(git rev-parse --git-dir)/last-test-pass"
VERSION_FILE=${VERSION_FILE:-package.json}
CHANGELOG=${CHANGELOG:-CHANGELOG.md}
ZERO=0000000000000000000000000000000000000000

fail() { echo "❌ $1" >&2; exit 1; }

while read -r local_ref local_sha remote_ref remote_sha; do
  [ "$local_sha" = "$ZERO" ] && continue
  commit=$(git rev-parse "$local_sha^{commit}")
  if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$commit" ]; then
    fail "$local_ref 指向的 ${commit:0:7} 没有测试通过记录，请先运行 scripts/test-and-stamp.sh"
  fi
  case "$local_ref" in
    refs/tags/v*)
      version=${local_ref#refs/tags/v}
      git show "$commit:$VERSION_FILE" 2>/dev/null | grep -qF "$version" \
        || fail "$VERSION_FILE 里没有版本号 $version"
      git show "$commit:$CHANGELOG" 2>/dev/null | grep -qF "$version" \
        || fail "$CHANGELOG 里没有 $version 的条目"
      ;;
  esac
done
```

按项目调整：

- `TEST_CMD`：测试命令，默认 `make test`
- `VERSION_FILE`：版本号所在文件，默认 `package.json`（Rust 用 `Cargo.toml`，Python 用 `pyproject.toml`）
- `CHANGELOG`：更新日志文件，默认 `CHANGELOG.md`

行为说明：

- 普通分支推送：只要求推送的 commit 测试通过过，不要求改版本号。版本号只在发版时检查。
- 推送 `v1.2.3` 这样的 tag：额外要求该 commit 里的版本文件和更新日志都包含 `1.2.3`。
- 删除远端分支或 tag 不受限制。
- 记录只保存最近一次通过的 commit。一次推送多个指向不同 commit 的分支时，只有和记录一致的能通过。
- 本地 hook 可以用 `git push --no-verify` 跳过。团队项目要把同样的检查放进 CI 和分支保护，hook 只是让问题早点暴露。

## 回滚准备

每次发布前，确认以下回滚能力：

1. **保留上一版的发布配置**：能在 10 分钟内回退到上一个稳定版本
2. **回滚步骤文档化**：不依赖记忆，任何人按步骤都能执行
3. **回滚后验证**：回滚后跑一遍核心流程，确认恢复正常

```markdown
## 回滚步骤（模板）

1. 检出上一版的 tag：`git checkout v1.2.3`
2. 重新构建：`make build`
3. 部署/分发：[具体步骤]
4. 验证：[核心流程检查]
5. 通知用户：[渠道和话术]
```

## 发布后观察

- 发布后 24 小时内关注崩溃报告、用户反馈
- 设定回滚触发条件：崩溃率超过 X%，或核心功能不可用
- 确认新版本稳定后，才清理上一版的回滚配置

## 与 safe-mode 的关系

`release-gate` 管发布流程，`safe-mode` 管发布后崩溃的恢复。两者配合：
- 发布门禁降低出问题的概率
- 安全模式提供出问题后的最后防线
