---
type: life-goal
goal: ""
area: ""
status: active
trend: New
last-updated: ""
target-date: ""
tags:
  - life-goal
  - home
---

# {{goal}}

<!--
Cap: 250 words, excluding ## History. Obeys .cosmos/instructions/output-contract.md.

Home voice — written about the operator as a person, not the operator the leader. Direct and
honest, warmer than the work files. No executive vocabulary.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.
-->

## Line

<!--
ONE sentence, 25 words maximum, stating this goal canonically — what it is and
where it currently stands.

This is the single wording for this fact across the whole vault. Every other
artifact embeds it rather than restating it in fresh words:

    ![[home/goals/run-a-5k#Line]]

Update the sentence here and every artifact carrying it updates too.

Filled example:
Run a 5K without stopping by October; running twice a week since June, still
walking the last half mile.
-->

## Definition of Success

What "done" actually looks like — specific and observable. Not "be healthier" but "run a 5K without stopping."

## Current Read

Where this stands right now. Honest trajectory.

## Trajectory

**Status:**
**Trend:**
**Target:**

## Why It Matters

One honest sentence. Not motivation-poster language — the real reason this is on the list.

## What's in the Way

The real obstacles, not the easy ones. One line each.

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

When a 5th entry lands, move the oldest to the matching file under
`archive/goals/`.
-->

---

## Mentions In Journal

```dataview
LIST
FROM "journal/personal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
