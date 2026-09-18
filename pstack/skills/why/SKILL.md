---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Discovers available MCPs and queries each evidence category (source control, issue tracker, long-form docs, real-time chat, infrastructure observability, error tracking, product analytics warehouse) in parallel, then returns a cited read on decisions and tradeoffs. Use how for runtime behavior."
---

# Why

Investigate the motivation and intent behind code.

Companion to the `how` skill. `how` answers what the code does and how it works. `why` answers what forces led to its shape.

## Operating Posture

Operate as a **careful, cautious, and precise investigator**. Be honest about what you know vs what you're inferring. Read `references/epistemics.md` for the full confidence framework and phrasing guide. The synthesizer must follow it.

## Step 1. Understand the Target and the Question

Parse what the user is asking. The **target** is usually a chunk of code, a pattern, a feature, or a named design decision. The **question** is usually a design rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a broad history sweep.

If the target is vague ("why do we do it this way?" with no clear referent), make your best guess from conversation context (open files, recent edits, what was just discussed). State your interpretation briefly so the user can redirect if you're off, then proceed.

## Step 2. Establish the Code Anchor

Before spawning investigators, anchor the investigation in concrete code:
- The relevant file path(s) and line range(s)
- The key symbols (function names, class names, constants)
- An initial commit list: the last few commits touching the target
- PR numbers from merge commits (pattern `(#1234)` in the subject line)

Build this inline:
```bash
# Blame target lines for last-touch commits
git blame -L <start>,<end> <file>

# Full file history, with patches, through renames
git log --follow -p -- <file>

# Last N commits touching the file, PR numbers visible
git log --oneline -20 -- <file>

# Extract PR numbers from a commit message
git log -1 --format=%B <commit>
```

Pull PR bodies and discussion via `gh` for any substantive commits:
```bash
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

Capture this as seed context (file paths, symbols, commits, PR numbers, linked ticket IDs) to pass to investigators.

## Step 3. Spawn Parallel Investigators (default posture)

### Discovery

Before spawning investigators, inspect available tools and MCP servers in the environment:
- In Antigravity: Check registered MCP servers in `<appDataDir>/mcp/`, `mcp_config.json`, or eager tools (`mcp_*`).
- In DSH: Check loaded plugins and available tool harnesses.

Map each available tool/MCP to an evidence category:
1. **Source control history** (always available via git / `gh`)
2. **Issue / ticket tracker** (GitHub Issues, Linear, Jira)
3. **Long-form documents** (Notion, Confluence, Google Docs)
4. **Real-time team chat** (Slack, Discord, Teams)
5. **Infrastructure observability** (Datadog, Grafana, CloudWatch)
6. **Error / exception tracking** (Sentry, Bugsnag)
7. **Product analytics warehouse** (BigQuery, ClickHouse, Snowflake)

Aim for a complete **coverage map**. Document the null, don't skip the search.

Launch matching investigators concurrently:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "self"` (to retain tool/MCP access), `Model: "flash"` (or configured `why investigators` model).
- **In DSH:** Spawn parallel worker subagents on `deepseek-chat`.

Each investigator gets:
1. The base prompt from `references/investigator-prompt.md`
2. The category playbook `references/sources/<source>.md`
3. Cross-cutting `references/sources/incident-postmortem.md` if the target code is defensive
4. The code anchor from Step 2
5. The user's original question

### When to skip an investigator

Only skip with an **explicit, written justification** in the final "Sources Consulted" section:
- **No MCP / tool available for that category** in this environment. Flag as a gap.
- **The source is provably irrelevant** (e.g. error tracking for a build script).

## Step 4. Synthesize

Spawn one synthesizer subagent:
- **In Antigravity:** Call `invoke_subagent` with `TypeName: "self"`, `Model: "pro"` (or configured `why synthesizer` model).
- **In DSH:** Run synthesizer on `deepseek-reasoner`.

The synthesizer receives investigator findings, code anchor, original question, and the epistemics framework.

## Step 5. Present

Present the synthesizer's output to the user. Light edits for clarity are fine, but **preserve confidence language**.

## Output Format

Follow `references/synthesizer-prompt.md`: The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted, Confidence Summary.

## Reference Files

- `references/epistemics.md`: Confidence tiers and phrasing guide.
- `references/investigator-prompt.md`: Base prompt template for investigators.
- `references/source-playbook.md`: Category playbooks index.
- `references/sources/*.md`: Category-specific playbooks.
- `references/synthesizer-prompt.md`: Synthesizer prompt template.
