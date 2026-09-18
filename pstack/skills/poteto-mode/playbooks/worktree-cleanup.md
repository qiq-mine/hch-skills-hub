### Worktree and simulator cleanup

**You own the disk and the safety gate.** Prune merged or abandoned git worktrees and stale temporary artifacts to reclaim space. Deletion is irreversible, so every step guards against deleting something in use or holding uncommitted work.

1. Snapshot and audit. Record `df -h /`, then run `scripts/worktree-audit.sh` (principle-build-the-lever). It reads paths from `git worktree list`, never hand-typed. It classifies each worktree by size, age, merge state, uncommitted work, PR state, and the newest session that touched it, then suggests a bucket.
2. The bucket is advice, not permission. The pinned and active sessions are the real artifact (principle-prove-it-works). Cross-check every candidate against active conversations.
3. Verify usage before deleting. For every `verify-recent-chat` row, or anything you doubt, fan subagents out to read the transcripts and report whether the worktree is ongoing (principle-guard-the-context-window).
4. Pause on irreversible loss. `wip:N` is N tracked uncommitted edits. Show the diff and get a decision first, since removing a clean worktree is recoverable from its branch but uncommitted work is gone. `scratch:N` is untracked throwaway, safe to drop, but name the files. Clean and merged and not-in-use proceeds. `wip` and in-use pause.
5. Prune the confirmed set. Per path, `git worktree remove --force <path>`. If the dir survives on ignored build artifacts, `rm -rf` it, then `git worktree prune`. Branch refs survive, so no commits are lost. Confirm with `df -h /` and re-list.
6. Other reclaimers. Simulator / emulator cleanup where applicable: `xcrun simctl delete unavailable`, runtime prune. More when needed: build and package caches (pnpm, uv, pip, cargo, yarn), workspace temporary `scratch/` directories. Clear only caches the user has not said to keep.

**Reply:** `df -h /` before and after with space reclaimed, the worktrees pruned, and a one-line reason for each held back.
