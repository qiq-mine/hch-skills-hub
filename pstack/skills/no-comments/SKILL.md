---
name: no-comments
description: "Spawn Comment Sicko subagent, strip gratuitous narration and dead code comments, fix accepted findings, and offer encodings for claimed constraints."
---

# No comments

Spawn the Comment Sicko reviewer. Act on accepted findings.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch (default `main`), including the working tree.

## Steps

1. **Spawn Comment Sicko.** In Antigravity: call `invoke_subagent` with `Role: "Comment Sicko"`, passing the system prompt from `agents/comment-sicko.md` and the scope diff/files. In DSH: spawn a dedicated comment review subagent.
2. **Inspect report and diff.** Reject application-code edits, scope escapes, and exception-protected deletions. Surprises in our own code must be reshaped rather than explained by comments. Restore deletions only with exact exceptions and scoped proof.
3. **Fix trivial accepted flags directly** by deleting dead paths, dropping unneeded parameters, or using the real API. If a fix requires architectural reshaping, run `/architect`.
4. **Implement the smallest root-cause fix in scope.** Remove workaround explanations. Guide intent using `principle-fix-root-causes` and `principle-redesign-from-first-principles`.
5. **Constraint comments:** Where comments say `do not remove` or `do not change wording`, offer in-scope type, runtime, test, or lint rules instead of prose comments.
6. **Report:** Output deletion count, restored comments, fixes, and open constraints.
