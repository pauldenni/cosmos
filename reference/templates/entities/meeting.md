---
type: meeting
meeting: ""
cadence: ""
owner: ""
programs: []
domains: []
related_risks: []
related_decisions: []
aliases: []
source: ""
journal_path: ""
tags:
  - meeting
  - entity
---

<!--
Cap: 200 words, excluding the Live References query. Obeys
.cosmos/instructions/output-contract.md (no cap row exists for meeting entities;
this is a definition file, so keep it short).

No `## Line` here. A meeting is a forum, not a fact other artifacts embed —
`## Purpose` already carries its one-sentence identity. Keep Purpose to one
sentence and nothing else needs a canonical wording.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter and in the query below. Do not hand-maintain a
parallel list of related programs or decisions (contract §8).
-->

## Purpose

One sentence: what this forum is for and who it serves.

## My Role / Attendance Posture

<!--
Read by /sync and /prep per .cosmos/instructions/attribution-discipline.md before
attributing any owner, decision, or action item drawn from this meeting.

State the operator's role (informational / owned / mixed) and the synthesis
guidance that follows from it. Omit the section if the meeting has no posture
worth stating — the core principle in attribution-discipline.md then applies.
-->

## Typical Inputs

What gets brought in. One line each.

## Typical Outputs

What comes out — decisions, escalations, status. One line each.

## Notes

Standing context about how this meeting actually runs. Omit if there is none.

---

# Live References

## Notes That Reference This Meeting
```dataview
LIST
FROM ""
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
