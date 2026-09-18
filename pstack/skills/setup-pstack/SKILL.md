---
name: setup-pstack
description: "Configure which models pstack uses per role and at what reasoning budget. Detects your available models in Antigravity or DSH and writes an always-applied rule that overrides the skill defaults. Use for /setup-pstack, 'configure pstack models', 'pstack budget', or changing pstack's model choices."
---

# Setup pstack

Configure per-role model assignments and reasoning budgets for pstack in Antigravity or DSH. Writes `.agents/rules/pstack-models.md` (project-local) or `~/.gemini/config/rules/pstack-models.md` (global).

## Steps

### 1. Detect available models

Enumerate the model tiers or model slugs available in your agent environment:
- **In Antigravity:**
  - Standard tiers: `inherit` (parent model), `pro` (maximum reasoning/judgment), `flash` (fast execution/coding), `flash_lite` (lightweight tasks).
  - Specific frontier models if configured via custom providers.
- **In DeepSeek Harness (DSH):**
  - Standard models: `deepseek-reasoner` (R1 / thinking for judgment and architecture), `deepseek-chat` (V3 / fast code implementation), `inherit`.
- **In multi-provider setups:** Entitled model slugs such as Claude, GPT, or Grok models.

The aliases `inherit-parent`, `inherit`, and `auto` are always valid.

### 2. Load current state

Check if `.agents/rules/pstack-models.md`, `~/.gemini/config/rules/pstack-models.md`, or `~/.cursor/rules/pstack-models.mdc` already exists. If found, read it and treat its `# budget` line and role mappings as current choices. Otherwise start from the defaults shown in Step 5.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** In Antigravity, call the `ask_question` tool:
- `unlimited — keep max (pro / deepseek-reasoner / max reasoning)`
- `large — high reasoning (pro / deepseek-reasoner)`
- `medium — balanced (flash / deepseek-chat with thinking where supported)`
- `small — fast & economical (flash / flash_lite / deepseek-chat)`

**(b) Apply it.** Build the role-to-model table.
- `unlimited` / `large`: routes judgment, prose, hardest tasks, and synthesizers to `pro` (or `deepseek-reasoner`). Fast code roles stay on `flash` (or `deepseek-chat`).
- `medium`: routes standard code tasks to `flash`, reviews to `pro`.
- `small`: routes all mechanical and review tasks to `flash` / `deepseek-chat`.
- Any role set to `inherit` runs on the parent conversation's model.

**(c) Show the roles and confirm.** Show every role with its assigned model:
- Code delegates (`feature`, `refactoring`, `bug-fix`, `perf-issue`, `hillclimb`)
- Judgment & Prose (`hardest tasks`, `synthesizer`)
- Panel roles (`arena runners`, `architect runners`, `interrogate reviewers`)
Confirm via `ask_question` or user prompt.

### 4. Validate

Every chosen slug or tier must be valid in the environment. `inherit` and `auto` always pass.

### 5. Write the rule

Write `.agents/rules/pstack-models.md` (or `~/.gemini/config/rules/pstack-models.md` for global machine scope):

```markdown
---
description: pstack per-role model choices (overrides skill defaults)
trigger: always_on
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit` or `auto`: the role runs on the parent chat model.
# budget: large (high reasoning)
feature, refactoring: flash
bug-fix: flash
perf-issue: flash
hillclimb: flash
judgment and prose: pro
hardest tasks: pro
how explorer: flash
how explainer: pro
why investigators: flash
why synthesizer: pro
reflect tooling: pro
reflect judgment, divergent, synthesizer: pro
arena runners: pro, flash, inherit
arena cross-judge pool: pro, inherit
swarm workers: flash
architect runners: pro, flash, inherit
interrogate reviewers: pro, flash, inherit
```

*(For DSH environments, replace `pro` with `deepseek-reasoner` and `flash` with `deepseek-chat`)*.

### 6. Confirm

Inform the user that the configuration has been saved and is active. Re-running this skill updates it at any time.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill in `.agents/skills/` or an existing harness). If not, offer:
*"Would you like a project-local verification skill so agents can drive the app the way a user does? I can generate one with /create-verification-skill."*
