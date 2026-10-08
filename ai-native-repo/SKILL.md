---
name: ai-native-repo
description: "Apply the AI Native Repo team standard when scaffolding, reviewing, or working in a code repo: directory layout, AGENTS.md, harness.yaml, spec/CodeSpec, changes proposal flow, SDD phases, and checklists. For rigorous working methods (principles, playbooks, adversarial review), see the pstack skill suite（重活方法论见 pstack）；多仓库团队资产中台与配置分发见 oh-teamai。"
---

# AI Native Repo

## Purpose
Make any repo agent-ready the same way: minimal structure, versioned instructions, contracts as source of truth, and human gates where they matter. Tracks《AI Native Repo 团队标准（草案 v0.1）》+《实用规范 v0.1》(hch-agentic-esm PR #3, docs/20 + docs/21 — draft, under team review).

## Workflow

### 1. Scaffold or audit the repo layout
M = required, R = recommended. Small repos (<5k lines, single module) do M only.

- `AGENTS.md` (M): root manual, 50–150 lines (hard cap 200–500), frontmatter `owner`/`status`/`last-verified`/`standard-version`; paths and pointers only, never pasted content (JIT)
- `README.md` (M), `harness.yaml` (M), `docs/` (M: one-page `architecture.md` + `adr/` with at least one entry), `spec/` (M when the repo has interfaces — contracts are the single source of truth)
- `rules/` (M: `agent-permissions.md` + `security.md`), `tests/` (M), `.env.example` (M: no real secrets), `.github/` (M: CI + PR template), `env/Taskfile.yml` (M: `setup` / `test` / `lint` must run)
- `changes/` (M: proposal → apply → archive), `prompts/` (R: versioned templates), `skills/` (R: distill when one operation repeats 3 times), `tools/` (R: codegen/migration scripts with `--help`), `eval/` (R: phase 3)

### 2. Wire the harness
`harness.yaml` declares skills, hooks, gates, permissions. Blocking gates (merge-stoppers): `tests`, `spec-validate` (spec↔CodeSpec consistency, provided by the SDD CLI), `secret-scan`. Garden gates (issues only, never block): `doc-freshness`, `eval-drift`. Decoupling test: a new tool reading only `harness.yaml` + `AGENTS.md` must complete one `changes/` proposal unaided — if swapping the tool loses assets, the layout is wrong.

### 3. Pick the work channel
- **Daily change** → `changes/<verb-slug>/` proposal: `proposal.md` (why in one concrete sentence, scope in/out, rejected alternatives), `spec-delta.md` (delta only — never edit the spec file directly), `tasks.md` (T-* with acceptance). Proposal review is the only human gate; agent implements; archive to `changes/archive/YYYY-MM-DD-<id>/`. Skip proposal for bugfix (restoring expected behavior), typo, format, non-breaking dependency upgrades, pure config.
- **Feature** → SDD five phases (details: `references/sdd-and-codespec.md`): clarify → specify → design → task → verify. Agent produces content, CLI holds state (`state.json`), human confirms gates G1–G5. Traceability RQ-* → FR-*/AC-* → D-* → T-* → commit → test; a broken chain sends the work back one phase.
- **Module implementation** → CodeSpec (`*.codespec.yaml`): contract first (human confirms interface shape), CLI generates stubs, agent fills implementation, contract tests must go green. Never modify the contract during implementation; contract changes route back through CodeSpec + human confirmation.

### 4. Run the checklists
New-repo, pre-merge, and quarterly anti-rot checklists: `references/checklists.md`. Pre-merge hard requirements: test evidence attached, spec changes via delta, instruction-file changes (`AGENTS.md`/`skills`/`prompts`/`rules`) human-reviewed, secret scan green.

## Output Contract
- New repo: every M item present; `task setup && task test && task lint` green.
- Change: proposal reviewed → implemented → archived; spec updated via delta, never in place.
- Review: every finding cites the exact clause (e.g. "§2.4.5", "实用规范 §3.1").

## Operating Rules
1. Security hard lines (§2.4):instruction files change only via PR + human review (2026 saw real attacks via repo instruction files); secrets never enter the repo — env injection plus secret-scan gate; permissions declared once at root (`rules/agent-permissions.md`), subdirectories never widen them; dangerous ops (prod / hardware / data deletion) declared in the file header and `rules/security.md`, merged only with a named reviewer; **an MCP server must never be the sole custodian of credentials** — scopes are explicitly issued per call, never inherited from the caller.
2. AGENTS.md is human-written and human-reviewed; never adopt agent-generated context files unverified.
3. Tools stay light and replaceable; the repo carries the engineering assets.
4. Ship staged (Phase 1 → 2 → 3), never big-bang. Pilot items (eval thresholds, context budgets, guardrail placement) run 3 months before becoming standard.
5. Measure three numbers: agent first-pass merge rate, standard violations intercepted by CI, human firefighting time after agent-written code.
6. Maintenance of this skill: changes go straight to master with a CHANGELOG entry — no PR (Robin 2026-10-08).
