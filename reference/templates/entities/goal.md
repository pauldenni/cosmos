---
type: goal
goal: ""
status:
trajectory:
trend:
period: ""
target-date: ""
owner: ""
source-url: ""
program: ""
systems: []
related_risks: []
related_decisions: []
aliases: []
tags:
  - goal
  - entity
---

<!--
Cap: 250 words, excluding ## History and the Live References queries.
Obeys .cosmos/instructions/output-contract.md.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter and in the Live References queries below. Do
not hand-maintain a parallel list of related entities (contract §8).
-->

## Line

<!--
ONE sentence, 25 words maximum, stating this goal canonically — the outcome and
where it currently stands.

This is the single wording for this fact across the whole vault. Every other
artifact embeds it rather than restating it in fresh words:

    ![[work/goals/collections-cutover-h2#Line]]

Update the sentence here and every artifact carrying it updates too.

Filled example:
Move all Collections traffic onto the new taxonomy by 2026-12-31; three of nine
entity migrations are done and the cutover has slipped twice.
-->

## Definition of Success

What achieving this actually looks like. Specific and measurable. Do not restate the Line.

## Current Read

Where the goal stands today and what moved since the last read.

## Trajectory

**Status:**
**Trend:**
**Confidence:**

## Adjustments Needed

The course corrections — scope changes, resource shifts, dependency unblocks, decisions to escalate. Omit if none.

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

When a 5th entry lands, move the oldest to the matching file under
`archive/goals/`. Per-run blow-by-blow belongs in `journal/sync-log/`.
-->

---

# Live References

## Related Risks
```dataview
TABLE severity, trend, owner, last-updated
FROM "work/risks"
WHERE related_goals = this.file.link OR contains(related_goals, this.file.link)
SORT severity DESC, last-updated DESC
```

## Related Decisions
```dataview
TABLE status, owner, last-updated
FROM "work/decisions"
WHERE related_goals = this.file.link OR contains(related_goals, this.file.link)
SORT last-updated DESC
```

## Mentions In Journal
```dataview
LIST
FROM "journal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
