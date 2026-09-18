---
name: show-me-your-work
description: "Keep a reviewable decision trail for long-running or unattended work: a TSV log with one row per decision (what, why, evidence, result). Local by default; commit it when a reviewer needs the trail to trust the result. Use for /show-me-your-work, autonomous or multi-phase runs, or work a human reviews after stepping away."
---

# Show me your work

Keep one canonical log.

## The format

A single TSV file, one row per decision. Cells stay single-line. Evidence is a pointer, not prose.

Copy `references/decision-log-template.tsv` (the header row) to start a clean log. Columns:
- **ts.** ISO8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words.
- **evidence.** A link or path that proves it: commit SHA, PR number, `file:line`, or an artifact, trace, or screenshot path. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

Example:
```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted work first, ~100 components	size scope before long run	commit 3a9f1c2	5 blockers identified
2026-05-24T11:15:00Z	widget	moved widget styles without layout changes	keep diff small & verified	commit 7c21e0a	identical render, tests pass
```

## Logging a row

Write each entry plainly without AI conversational fluff (the **unslop** skill applies to log text too).

Use the helper `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`. It stamps `ts`, writes the header on first use, strips stray tabs/newlines, and escapes spreadsheet formula triggers.

Log decision points and checkpoints, not every trivial command: a fork chosen, a unit completed with verification result, a revert with its trigger, or a gate fixed.

## Where it lives

By default the log is a working artifact, not committed. Keep it at `decisions.tsv` in the workspace root, or `scratch/decisions-<task-slug>.tsv`. Leave it out of git unless the work requires a permanently committed audit record.

## Rules

- One row is one decision or checkpoint.
- Append-only. A wrong call gets a new row that supersedes it. Never rewrite history.
- Prefer evidence produced by committed scripts over hand-made assertions.

## Audit the log against the transcript

At the end of the run, before handing back, check the log told the truth against the conversation transcript:
- **In Antigravity:** Read `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
- **In DSH:** Read session transcript logs in the DSH session runtime path.

Walk the log against what actually happened:
- Every row maps to a real action. Cut invented entries.
- Each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work must be logged.

## Cross-model review of the trail

Before handing back, spawn a subagent on a different model tier (e.g. In Antigravity: call `invoke_subagent` with `Model: "pro"` reviewing `flash` execution, or vice versa).
The subagent reads the audit trail and the run's transcript, scanning for risks:
- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof.
- Choices that look risky or paper over symptoms.
- Gaps the user would otherwise miss.

Every reply for a run producing a trail ends with an "Attention" section naming the reviewer model and specific rows or flags flagged.
