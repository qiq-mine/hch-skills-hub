---
name: interrogate
description: "Use for 'interrogate', 'adversarial review', 'multi-model review', 'challenge this', 'stress test this code', 'find blind spots', or 'tear this apart'. Multiple reviewers challenge changes from independent angles."
---

# Interrogate

Spawn one reviewer per configured model to adversarially review code changes. Each model gets the same prompt and rubric. The adversarial signal comes from model diversity, not assigned personas.

The deliverable is a synthesized verdict. Do NOT auto-apply changes.

## Step 1. Determine Scope

Identify what to review from context:
- If the user points at specific files or a diff, use that.
- If on a feature branch, run `git diff main...HEAD` (or appropriate base branch) for the full changeset.
- If the user's message references recent work, gather the relevant files.

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

## Step 2. State the Intent

Before spawning reviewers, state the intent explicitly. Derive this from:
- The user's message
- Commit messages
- PR description if one exists
- The code itself

Write one clear paragraph. If you're unsure about the intent, ask the user before proceeding.

## Step 3. Spawn Reviewers

Launch all reviewers in a single message:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "research"` (read-only) for each reviewer. Use the `interrogate reviewers` list from `.agents/rules/pstack-models.md` when present. Otherwise use the environment defaults:

| Subagent | Antigravity Default | DSH Default | Multi-Model Default |
|----------|---------------------|-------------|---------------------|
| Reviewer A | `pro` | `deepseek-reasoner` | `claude-3-7-sonnet` |
| Reviewer B | `pro` | `deepseek-reasoner` | `gpt-4o` |
| Reviewer C | `flash` | `deepseek-chat` | `deepseek-chat` |
| Reviewer D | `inherit` | `inherit` | `gemini-2.5-pro` |

- **In DSH:** Spawn parallel read-only review subagents via DSH runner.

Read `references/reviewer-prompt.md` and fill in the template with:
1. The stated intent
2. The diff or file contents
3. The review rubric from `references/rubric.md`
4. The code-quality lens from `references/code-quality-review.md`

The same filled template goes to all reviewers.

## Step 4. Synthesize

As results come back:
1. **Parse all findings** from the reviewers.
2. **Identify consensus**: findings raised by 2+ models independently are highest signal.
3. **Identify lone-model findings**: still worth reading, but weighted accordingly.
4. **Deduplicate**: merge synonymous findings and note which models raised them.
5. **Note disagreements**: explicit contradictions between reviewers offer valuable context.

## Step 5. Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.
Read `references/lead-judgment.md` for the full framework.

Categorize every finding:
- **Act on**: Real issues affecting correctness, security, or maintainability given the actual goals.
- **Consider**: Legitimate points, but user should weigh cost vs benefit.
- **Noted**: Technically valid but low-impact or premature.
- **Dismissed**: Wrong, nitpicky, or missing context (with brief reason).

For each finding, include:
- Which model(s) raised it
- The category (act on / consider / noted / dismissed)
- A one-line rationale

## Output Format

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On
[Findings that should be addressed: description, which models raised it, why it matters.]

### Consider
[Findings worth evaluating: description, which models raised it, tradeoff involved.]

### Noted
[Valid but low-priority. Brief list.]

### Dismissed
[Rejected findings with brief rationale.]

### Agreement Map
[Where models agreed vs diverged, and what the pattern indicates.]
