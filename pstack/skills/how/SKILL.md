---
name: how
description: "Use for 'how does X work', code walkthroughs before changing something, and placement / ownership / layering questions ('where should this live', 'which package owns this', 'is this the right layer'). Explains subsystem architecture, runtime flow, and onboarding mental models. Use why for motivation."
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model without reading like annotated source code.

## Step 1. Assess Complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow function): no explorers. One explainer explores and explains in a single pass. Go to Step 2b.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): spawn parallel explorers first, then hand off to the explainer. Go to Step 2a.

When in doubt, take the simple path.

## Step 2a. Explore (complex questions only)

Decompose the question into 2 to 4 exploration angles, each a distinct slice of the subsystem. Spawn all explorers concurrently:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "research"`, `Model: "flash"` (or your configured how-explorer model from `.agents/rules/pstack-models.md`).
- **In DSH:** Spawn explorer subagents on `deepseek-chat`.

Each explorer gets the prompt in `references/explorer-prompt.md` with its angle filled in. Then proceed to Step 3.

## Step 2b. Direct Explain (simple questions)

Spawn or run one explainer that explores and explains in one pass:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "research"`, `Model: "pro"` (or parent model).
- **In DSH:** Run on `deepseek-reasoner` or current model.

Build its prompt from `references/explainer-prompt.md` without the explorer-findings section. Go to Step 4.

## Step 3. Synthesize (complex questions only)

Once all explorers have returned, spawn one synthesizer subagent to weave their findings into one explanation:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "research"`, `Model: "pro"` (or your configured how-explainer model).
- **In DSH:** Run synthesizer on `deepseek-reasoner`.

Build its prompt from `references/explainer-prompt.md` with every explorer's findings filled in.

## Step 4. Present

Present the explainer's output to the user. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output Format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
