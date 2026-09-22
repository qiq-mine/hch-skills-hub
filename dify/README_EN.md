# Dify Fullstack Engineering & Code Review Skills Suite

> Adapted from the official engineering standards of [langgenius/dify](https://github.com/langgenius/dify).  
> Supported platforms: **Google Antigravity**, **DeepSeek Harness (DSH)**, and **Claude Code**.

---

## Overview

Dify is one of the world's most widely adopted open-source LLM application and Agent orchestration platforms. To power massive scale, multi-tenant isolation, complex workflow graphs, and an extensible design system, Dify created a rigorous set of software engineering principles and automated review skills.

This suite migrates and adapts the official Dify skills located in `.agents/skills`, offering 5 specialized skills covering the full engineering lifecycle:

1. **`backend-code-review`**: Python / Flask / SQLAlchemy backend layering and concurrency review
2. **`frontend-code-review`**: React / Next.js / TypeScript frontend architecture, a11y, and performance review
3. **`how-to-write-component`**: Production-grade React component architecture and state ownership guide
4. **`frontend-testing`**: Behavior-driven Vitest & React Testing Library (RTL) testing guide
5. **`e2e-cucumber-playwright`**: Cucumber BDD (Gherkin) + Playwright end-to-end testing suite

All 15 authoritative referenced guides have been bundled into the local `docs/` directory, ensuring 100% relative link resolution and offline capability.

---

## Skills Breakdown

### 1. `backend-code-review`
- **Trigger**: `/backend-code-review`
- **Target Stack**: Python 3.11+ / Flask / FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL / MySQL
- **Rule Catalogs**:
  - **Architecture Layering (`architecture-rule.md`)**: Thin controllers, strict one-way dependency direction (Controller → Service → Domain), business-agnostic `libs/`.
  - **Database Schema & Migrations (`db-schema-rule.md`)**: No cross-table queries in model `@property`, mandatory `tenant_id` scoping, redundant index avoidance, PostgreSQL/MySQL dialect portability.
  - **Repository Abstraction (`repositories-rule.md`)**: Enforce repository reuse, eliminate ad-hoc scattered ORM queries.
  - **SQLAlchemy & Concurrency (`sqlalchemy-rule.md`)**: Explicit session/transaction lifecycles, Core expressions over raw SQL, write-path concurrency safeguards (optimistic lock, Redis distributed lock, `SELECT FOR UPDATE`).

### 2. `frontend-code-review`
- **Trigger**: `/frontend-code-review`
- **Target Stack**: React 19 / Next.js / TypeScript 5+ / Tailwind CSS v4 / TanStack Query / Dify UI / Base UI
- **Rule Catalogs**:
  - **Accessibility (`accessibility-ui.md`)**: Accessible name computation, button vs link semantics, focus traps, keyboard navigation.
  - **Design System Primitives (`dify-ui.md`)**: Dify UI / Base UI primitive contracts, overlay rules (`overlays.md`), form semantics (`forms.md`).
  - **Component Architecture (`component-architecture.md`)**: Container vs presentation decoupling, minimal props interfaces, state placement.
  - **Data Query Contracts (`data-query-contracts.md`)**: TanStack Query structured keys, optimistic updates, query invalidation.
  - **Runtime Invariants (`dify-invariants.md`)**: Workflow node vs RAG pipe mounting isolation.
  - **Performance & Testing (`performance.md` & `testing.md`)**: Eliminate unnecessary re-renders, avoid waterfalls, regression testing.
  - **Code Quality (`code-quality.md`)**: Type safety, Tailwind v4 canonical utilities.

### 3. `how-to-write-component`
- **Trigger**: `/how-to-write-component`
- **Target Stack**: React / Next.js / TypeScript
- **Topics**:
  - **Ownership (`ownership.md`)**: Single responsibility, state placement tiering, avoiding prop drilling.
  - **State Lifecycle (`state.md`)**: Local state (`useState`), shared state (Jotai/Zustand), form drafts, URL search params.
  - **Interactions (`interactions.md`)**: Modals, drawers, popovers, dropdowns.
  - **Runtime Lifecycle (`runtime.md`)**: Strict `useEffect` disciplines, avoiding derived state effects, event listener cleanup.
  - **Tailwind CSS v4**: Canonical utilities (`w-105`, `px-2.25`, `wrap-break-word`).

### 4. `frontend-testing`
- **Trigger**: `/frontend-testing`
- **Target Stack**: Vitest / React Testing Library (RTL) / Mock Service Worker (MSW)
- **Guidelines**:
  - **Behavior over Implementation**: Black-box user perspective, test observables instead of internal state.
  - **Query Priorities**: `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText`.
  - **Interaction Simulation**: Always prefer `@testing-library/user-event` over `fireEvent`.
  - **Mocking Boundaries**: Mock only at external network (MSW) or browser API boundaries; never mock internal child components.

### 5. `e2e-cucumber-playwright`
- **Trigger**: `/e2e-cucumber-playwright`
- **Target Stack**: Cucumber.js (BDD/Gherkin) / Playwright / TypeScript
- **Guidelines**:
  - **Engine Roles**: Cucumber for scenario semantics and lifecycle; Playwright for browser execution.
  - **Declarative Gherkin**: Business goals over technical steps, high step reuse.
  - **Web-first Assertions**: Rely on Playwright auto-waiting, eliminating arbitrary sleep.

---

## Severity Grading (P0 - P3)

- **P0**: Security/privacy breach, multi-tenant leakage, data corruption, or production-wide crash.
- **P1**: User-visible regression, authorization failure, public API contract breach, hydration failure.
- **P2**: Concrete correctness issue, performance degradation (N+1 queries), unmanaged transaction, a11y defect.
- **P3**: Minor cleanliness recommendation (surfaced only on full audits).

---

## Documentation Index (`docs/`)

- [`authoring.md`](./docs/authoring.md) — Public API authoring
- [`styling.md`](./docs/styling.md) — Styling and design tokens
- [`overlays.md`](./docs/overlays.md) — Dialogs, drawers, popovers
- [`forms.md`](./docs/forms.md) — Form controls and validation
- [`selection.md`](./docs/selection.md) — Selection and controlled primitives
- [`accessible-names-and-descriptions.md`](./docs/accessible-names-and-descriptions.md) — A11y name and description standards
- [`testing.md`](./docs/testing.md) — Primitive testing guide
- [`test.md`](./docs/test.md) — Web testing policy and boundaries
- [`lint.md`](./docs/lint.md) — Static analysis guidelines
- [`landmarks.md`](./docs/landmarks.md) — Web landmark semantics
- [`truncated-text-disclosure.md`](./docs/truncated-text-disclosure.md) — Text truncation pattern
- [`api-agents.md`](./docs/api-agents.md) — Backend architecture charter
- [`web-agents.md`](./docs/web-agents.md) — Frontend architecture charter
- [`dify-ui-agents.md`](./docs/dify-ui-agents.md) — Dify UI module charter
- [`e2e-agents.md`](./docs/e2e-agents.md) — E2E automation charter
