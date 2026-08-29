---
type: scan
mode: program
program: ""
status:
trend:
confidence:
owner: ""
stakeholders: []
systems: []
related_risks: []
related_decisions: []
date: 2026-05-17
tags:
  - scan
  - scan-program
---

# Program Scan — {{program}} — 2026-05-17

<!--
Cap: 600 words. Obeys .cosmos/instructions/output-contract.md.

Deep dive on one program. Diagnostic, not packaged for upward share.

Risks, dependencies, and decisions share one table — each item appears once,
in one row. For detail, embed the canonical line rather than retelling it:
![[work/risks/<risk>#Line]]

Do not add a trailing entity list. Frontmatter and the body already carry the
links.

An empty section is omitted, not filled. Never emit a bare `-`, `TBD`, or an
empty table row.
-->

## Read

**Status:** {{status}} · **Trend:** {{trend}} · **Confidence:** {{confidence}}

One paragraph: where the program actually is versus where it should be.
Include the ownership call — right people on it, stakeholders aligned or not.

## What Changed

Material movement since the last scan. What became blocked or unblocked. One
line each. Skip anything stable.

## Open Items

Every unresolved risk, dependency, and decision. `Type` is `Risk`,
`Dependency`, or `Decision`. `Item` links the entity file.

| Item | Type | Owner | Status / Trend | Needed By |
|---|---|---|---|---|

## Next

The one to three things this program is driving toward. Imperative, one line
each.

## Asks

What needs decision, escalation, or air cover from outside the program. Named
person, concrete request, timing.
