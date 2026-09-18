# pstack — Rigorous AI Engineering Workflows & Skills

> Originally created by Lauren Tan ([@poteto](https://x.com/poteto)) | Adapted for Google Antigravity, DeepSeek Harness (DSH), and Claude Code.

There is a growing sense that AI writes too much slop code. Throughput without quality is not a goal to aspire to. If you want to go fast, go deep first.

**pstack is the answer.** These are structured, battle-tested skills designed to turn AI coding agents into a disciplined engineering team. The goal is not to maximize lines of code (LOC), but to write verified, concise, high-quality code.

**pstack gives you fearless parallelism.** When you go deep on one agent and trust it to write verifiable code, you can parallelize with confidence. Run multiple agents with `/poteto-mode` and trust them to apply rigorous engineering principles.

---

## What's in pstack

- **1 Primary Entrypoint**: [`/poteto-mode`](./skills/poteto-mode/SKILL.md) & [`pstack`](./SKILL.md)
- **23 Task Playbooks**: Structured runbooks for bugs, perf, features, refactoring, forensics, and releases
- **23 Engineering Principles**: Concrete constraints that guide subagents and prevent slop
- **11 Core Workflow Skills**: `architect`, `arena`, `swarm`, `interrogate`, `how`, `why`, `unslop`, `no-comments`, `tdd`, `show-me-your-work`, `create-verification-skill`
- **Subagent Personas**: `poteto-agent`, `comment-sicko`

---

## Compatibility: Antigravity & DeepSeek Harness (DSH)

This repository version has been modernized and decoupled from Cursor-proprietary mechanisms:

| Capability | Cursor Legacy | Antigravity Native | DeepSeek Harness (DSH) |
|---|---|---|---|
| **Subagent Spawning** | `Task(subagent_type: ...)` | `invoke_subagent` (TypeName: `self`/`research`) | DSH Subagent Runner |
| **High Judgment Model** | `claude-fable-5-1-thinking-max` | `Model: "pro"` | `deepseek-reasoner` (R1) |
| **Fast Execution Model**| `grok-4.6-fast-xhigh` | `Model: "flash"` | `deepseek-chat` (V3) |
| **Interactive Questions**| `AskQuestion` | `ask_question` tool | Console / Harness Prompt |
| **Configuration Rule** | `~/.cursor/rules/pstack-models.mdc` | `.agents/rules/pstack-models.md` | `.dsh/rules/` / `AGENTS.md` |
| **Transcripts** | `~/.cursor/projects/...` | `<appDataDir>/brain/<id>/.../transcript.jsonl` | Session Log Directory |
| **Autonomous Runs** | `/loop` command | `/goal` command / `schedule` tool | DSH Event Watcher Loop |

---

## Quick Start

Two steps:

1. Run [`/setup-pstack`](./skills/setup-pstack/SKILL.md) to detect your environment's models and set your reasoning budget.
2. Run [`/poteto-mode`](./skills/poteto-mode/SKILL.md) whenever you start a task that requires rigor.

```bash
/poteto-mode this endpoint has a race condition under load. repro first, trace root cause, then fix and verify.
```

---

## The 23 Playbooks

| Playbook | Purpose |
|---|---|
| [investigation](./skills/poteto-mode/playbooks/investigation.md) | Read-only question: how does X work, why was Y built this way. |
| [bug fix](./skills/poteto-mode/playbooks/bug-fix.md) | Reproduce a defect, root-cause it, and fix with live runtime evidence. |
| [perf](./skills/poteto-mode/playbooks/perf-issue.md) | Trace a measured slowness and improve it against a baseline. |
| [hillclimb](./skills/poteto-mode/playbooks/hillclimb.md) | Sustained scientific improvement of one metric against a target. |
| [runtime forensics](./skills/poteto-mode/playbooks/runtime-forensics.md) | Diagnose a live symptom (leak, idle-CPU spin) from instrumentation. |
| [trace forensics](./skills/poteto-mode/playbooks/trace-forensics.md) | Diagnose a captured profiling artifact (cpuprofile, trace, spindump). |
| [feature](./skills/poteto-mode/playbooks/feature.md) | New or changed behavior, built from a named data shape. |
| [refactoring](./skills/poteto-mode/playbooks/refactoring.md) | A behavior-preserving change to structure or shape. |
| [prototype](./skills/poteto-mode/playbooks/prototype.md) | A throwaway sketch to settle an empirical fork by observing it. |
| [visual parity](./skills/poteto-mode/playbooks/visual-parity.md) | Pixel-exact UI equivalence between two implementations. |
| [authoring a skill](./skills/poteto-mode/playbooks/authoring-a-skill.md) | Writing or editing a `SKILL.md` following standard conventions. |
| [eval](./skills/poteto-mode/playbooks/eval.md) | Blinded A/B test of how a prompt/skill affects agent behavior. |
| [babysit](./skills/poteto-mode/playbooks/babysit.md) | Drive a PR or stack to merge-ready: conflicts, review threads, CI. |
| [shipping](./skills/poteto-mode/playbooks/shipping.md) | Independently verify a green stack, then land bottom-up. |
| [autonomous run](./skills/poteto-mode/playbooks/autonomous-run.md) | Drive a long task to completion without stopping. |
| [orchestrate](./skills/poteto-mode/playbooks/orchestrate.md) | Multi-day project coordinator managing fleets of subagents. |
| [autopilot-full](./skills/poteto-mode/playbooks/autopilot-full.md) | Run independent PRs to merged with one owner per PR. |
| [autopilot-stack](./skills/poteto-mode/playbooks/autopilot-stack.md) | Build and verify one linear base-branch stack. |
| [session pickup](./skills/poteto-mode/playbooks/session-pickup.md) | Resume or take over a prior agent's in-flight work. |
| [pause safely](./skills/poteto-mode/playbooks/pause-safely.md) | Suspend in-flight work cleanly with durable checkpoints. |
| [multi-phase plan](./skills/poteto-mode/playbooks/multi-phase-plan.md) | Work that spans phases or stacked PRs. |
| [worktree cleanup](./skills/poteto-mode/playbooks/worktree-cleanup.md) | Reclaim disk by pruning merged or abandoned git worktrees. |
| [opening a pr](./skills/poteto-mode/playbooks/opening-a-pr.md) | Conventional commit title, briefing-style body, verified evidence. |

---

## The 23 Principles

- **Core**: `laziness-protocol`, `foundational-thinking`, `redesign-from-first-principles`, `attack-the-premise`, `subtract-before-you-add`, `minimize-reader-load`, `outcome-oriented-execution`, `experience-first`, `exhaust-the-design-space`, `build-the-lever`
- **Architecture**: `model-the-domain`, `boundary-discipline`, `type-system-discipline`, `make-operations-idempotent`, `migrate-callers-then-delete-legacy-apis`, `separate-before-serializing-shared-state`
- **Verification**: `prove-it-works`, `fix-root-causes`, `sequence-verifiable-units`, `test-behavior-not-implementation`
- **Delegation & Meta**: `guard-the-context-window`, `never-block-on-the-human`, `encode-lessons-in-structure`

---

## Installation in Antigravity or DSH

### Option 1: In this repository (`skills-hub`)
The skills are registered in `.agents/skills.json` and `.agents/plugins.json`. Opening this repository in Antigravity or DSH automatically mounts all pstack skills and playbooks.

### Option 2: Copy to your project
Copy `pstack/` into your project's `.agents/skills/pstack` or `.agents/plugins/pstack`.

---

## License

MIT
