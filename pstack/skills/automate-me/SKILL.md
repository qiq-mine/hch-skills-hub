---
name: automate-me
description: "Use for 'automate me', 'create/update/refresh my -mode skill', 'turn/capture my preferences or working style into a skill', or wanting agents to follow how the user works. Drafts or revises a personal -mode skill via unslop, optionally pulling fresh evidence from recent transcripts."
---

# Automate me

A guided flow for turning the user's working conventions into a skill agents will follow. The output is one `-mode` skill tailored to them (e.g. `jay-mode`, `priya-mode`).

This skill sequences an inline mining pass, skill authoring, and the **unslop** skill for prose discipline.

## Flow

### 0. Check for an existing skill

Look for `.agents/skills/**/*-mode/SKILL.md` or `skills/*-mode/SKILL.md` matching the user's handle. If one exists, confirm intent with `ask_question` (or direct prompt):
- Update the existing skill (default for repeat runs)
- Start fresh

### 1. Mine history

Locate the active workspace's transcripts before fanning out:
- In Antigravity: Read transcripts from `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
- In DSH: Read session logs from the DSH runtime session directory.

Survey recent conversations for recurring patterns:
- Response preferences (length, tone, format, directness)
- Delegation habits (subagents, model choices, parallelism)
- Verification posture (unit tests, live proof, strict criteria)
- Code and prose discipline (style, linters, principles)
- Process conventions (worktrees, commits, PRs)

Cross-check patterns across conversations. Patterns seen repeatedly are high-confidence.

### 2. Ask the user directly

Use `ask_question` (structured options) rather than asking the user to type from scratch:
- Which areas matter most (response style, autonomy, verification, tools)?
- Specific follow-up choices on selected areas.

### 3. Cluster findings

Group the combined signals into clear operational sections:
- Response style
- Autonomy & boundaries
- Subagents & delegation
- Review and verify
- Process conventions

### 4. Draft the skill

Create the skill file:
- Path: `.agents/skills/<handle>-mode/SKILL.md` (or `skills/<handle>-mode/SKILL.md`).
- Frontmatter: Standard YAML with `name: <handle>-mode` and a clear `description` explaining when to activate.
- Follow Antigravity / DSH skill standards.

### 5. Iterate on prose

Apply the **unslop** skill: remove AI conversational filler, keep short declarative sentences, and eliminate vague rules. Show the draft to the user for feedback.

### 6. Land it

Save the skill, verify registration, and commit to version control.
