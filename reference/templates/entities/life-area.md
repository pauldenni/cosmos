---
type: life-area
area: ""
trend: New
last-updated: ""
tags:
  - life-area
  - home
---

# {{area}}

<!--
Cap: 250 words, excluding ## History and the Active Goals query. Obeys
.cosmos/instructions/output-contract.md.

Home voice — written about the operator as a person, not the operator the leader. Direct and
honest, warmer than the work files. No org-health framing, no executive
vocabulary.

No `## Line` here. A life area is a container for goals and observations, not a
claim other artifacts embed — the goals inside it carry their own canonical
lines.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.
-->

One sentence: what this area of life covers.

## Current Read

Honest state of this area right now.

## What's Working

One line each. Omit the section if nothing is.

## What Needs Attention

One line each. Omit the section if nothing does.

## Active Goals

```dataview
TABLE trend, target-date
FROM "home/goals"
WHERE area = "{{area}}" AND status = "active"
SORT file.mtime DESC
```

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

When a 5th entry lands, move the oldest to the matching file under `archive/`.
-->
