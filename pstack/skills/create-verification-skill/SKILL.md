---
name: create-verification-skill
description: "Generate a project-local verification skill that drives your app the way a user does — any language, framework, or platform. Use for /create-verification-skill, 'make a control skill for this repo', or when a project has no scripted way to prove UI/CLI/service behavior."
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill (`.agents/skills/verify-<app>/` or `skills/verify-<app>/`) tailored to the repo. Write the output for the next agent: it will be read cold, mid-task, by an agent that has never seen the app.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask the user what you cannot observe:
- **Surface:** What does a user touch? Web UI, CLI/TUI, desktop app, API, mobile app, or library?
- **Run:** How does the app start locally? Prefer repo documented dev commands (npm start, cargo run, Makefile). Note ports, env vars, seed data.
- **Drive:** How can an agent interact programmatically? Existing harnesses first (Playwright, Cypress, expect, curl, CLI commands).
- **Observe:** What evidence can be captured? Screenshots, terminal output, responses, logs, exit codes.
- **Isolate:** Can two instances run side by side without collisions?

If the checkout doesn't build or start as-is, fix that first before generating.

## 2. Generate the skill

Write `.agents/skills/verify-<app>/SKILL.md` (or `skills/verify-<app>/SKILL.md`) with YAML frontmatter (`name: verify-<app>` and a descriptive `description`) with these sections:
- **Launch:** The exact command that starts the app for verification, and how to verify readiness (log line, port listening, prompt). Include teardown.
- **Doctor:** One read-only check that answers "is this instance worth driving?" (process up, port owned, auth valid).
- **Drive:** The harness recipe with real selectors/commands from this repo. Prefer stable handles (semantic IDs, data attributes, CLI flags).
- **Evidence:** What to capture for proof and where it goes.
- **Cleanup:** How to safely terminate what you started without killing unrelated processes. Proof artifacts must survive cleanup.
- **Helpers:** Any helper script must be executable and documented in the skill body.

## 3. Seed the feature map

Create `.agents/skills/verify-<app>/features/README.md` plus one file per user-facing feature (top 3-5 to start). Each file answers from the user's POV:
- Sub-features
- How to reach it
- Driving it with the harness
- Gotchas

## 4. Prove the generated skill

Run its own instructions end to end once: launch, doctor, drive ONE mapped feature, capture evidence, clean up. Confirm the evidence still exists after cleanup.

## 5. Maintenance

Refer to `/maintain-verification-skill` for keeping the feature map and harness honest as the application evolves.
