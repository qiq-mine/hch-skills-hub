# @langgenius/dify-ui

This file owns the package boundary. Read the matching contract guide below directly; use the
[package index] when discovering available primitives or usage examples.

## Package boundary

- Keep this an independent primitive package. Do not import from application packages or depend on
  routing, i18n, application state, schemas, data fetching, or business APIs.
- Keep package contracts and contributor guidance self-contained here. Application docs and agent
  skills may reference these guides; these guides must not require Web docs or skills to define package behavior.
- Prefer `@base-ui/react` when it owns the required headless behavior. Style primitives with `cva`,
  `cn`, and Dify design tokens. Keep one primitive per `src/<name>/` folder with optional colocated
  stories and tests.
- Prefer Base UI data attributes for state styling and CSS variables for exposed dynamic values.
  Follow [Styling] for state callbacks; do not mirror primitive state in React solely to add classes.
- When an upstream API or selector contract is unclear, read the current official Base UI
  documentation and installed `@base-ui/react` declarations before coding.

## Contract owners

- Imports, exports, naming, public types, generics, and anatomy: [Public API authoring]
- Button and icon-only action behavior: [Button contract] and [Icon Button contract]
- Cross-component accessible-name and description choices: [Accessible names and descriptions]
- Compound input behavior: [Input Group contract]
- Form structure, labels, and value ownership: [Forms]
- Picker choice and typed values: [Selection]
- Portals, presence, layering, and floating-surface semantics: [Overlays]
- State styling, callbacks, composition, Tailwind integration, and border radius: [Styling]
- Package test ownership and setup: [Testing and development]

A component needs a local README only when it owns a substantial Dify-specific contract that its
types, stories, and upstream documentation do not express. Do not create one for completeness.

[Accessible names and descriptions]: accessible-names-and-descriptions.md
[Button contract]: button-readme.md
[Forms]: forms.md
[Icon Button contract]: icon-button-readme.md
[Input Group contract]: input-group-readme.md
[Overlays]: overlays.md
[Public API authoring]: authoring.md
[Selection]: selection.md
[Styling]: styling.md
[Testing and development]: testing.md
[package index]: dify-ui-readme.md
