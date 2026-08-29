---
type: system
system: ""
owner: ""
programs: []
domains: []
related_risks: []
aliases: []
tags:
  - system
  - entity
---

<!--
Cap: 250 words, excluding the Live References queries. Obeys
.cosmos/instructions/output-contract.md (no cap row exists for system entities;
this is a reference definition file, so keep it short).

No `## Line` here. `## What It Is` already serves as the canonical one-sentence
identity, and no artifact embeds a system definition — briefs reference Search,
they do not restate what Search is. Keep What It Is to one sentence and use one
term per concept vault-wide (contract §2).

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter and in the queries below. Do not hand-maintain
a parallel list of related programs, risks, or decisions (contract §8).
-->

## What It Is

One sentence: what this system does and what depends on it.

## Primary Owners

Who owns it, and for what. One line each.

## Operational Notes

Standing context — constraints, known fragility, upgrade posture. Omit if there is none.

---

# Live References

## Risks Involving This System
```dataview
TABLE severity, trend, owner, last-updated
FROM "work/risks"
WHERE contains(systems, this.file.link) OR contains(file.outlinks, this.file.link)
SORT severity DESC, last-updated DESC
```

## Decisions Involving This System
```dataview
TABLE status, owner, last-updated
FROM "work/decisions"
WHERE contains(systems, this.file.link) OR contains(file.outlinks, this.file.link)
SORT last-updated DESC
```

## Mentions In Journal
```dataview
LIST
FROM "journal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
