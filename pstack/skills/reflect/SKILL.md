---
name: reflect
description: "Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect or /reflect."
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent identifies its own transcript file before fanning out:
- **In Antigravity:** Read `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (and `transcript_full.jsonl` if needed).
- **In DSH:** Read the session transcript from the DSH runtime session directory.

If transcript files cannot be read directly, write a tight session digest and pass that instead.

### 2. Spawn three reviewers in parallel

Spawn three review subagents concurrently:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "self"`.
- **In DSH:** Spawn parallel worker subagents via DSH runner.

| Lens | Antigravity Model | DSH Model | Prompt template |
|---|---|---|---|
| Judgment | `pro` | `deepseek-reasoner` | `references/judgment-reviewer.md` |
| Tooling | `pro` / `flash` | `deepseek-chat` / `deepseek-reasoner` | `references/tooling-reviewer.md` |
| Divergent | `pro` | `deepseek-reasoner` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked.

### 3. Synthesize

Spawn one synthesizer subagent (in Antigravity: `TypeName: "self"`, `Model: "pro"`; in DSH: `deepseek-reasoner`).
Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for approval. Do not auto-apply without confirmation.

For each approved Accepted item:
- Minor edits (one-line bullet, tightened sentence): apply directly.
- Substantive edits (new section, new pattern): follow standard `SKILL.md` authoring rules.
- Save to project skills (`.agents/skills/` or `skills/`) or global config (`~/.gemini/config/skills/`).

### 6. Summarize for the user

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each.
- Backlog filed: `<issue title>`. One line each.
- Dropped: one line per rejected finding + reason.
