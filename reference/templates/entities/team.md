---
type: team
team: ""
lead: ""
programs: []
domains: []
related_risks: []
aliases: []
tags:
  - team
  - entity
---

<!--
Cap: 250 words, excluding the Live References query. Obeys
.cosmos/instructions/output-contract.md (no cap row exists for team entities;
this is a definition file, so keep it short).

No `## Line` here. A team is an actor referenced by wikilink, not a claim other
artifacts embed. `## Scope` carries its one-sentence identity — keep Scope to one
sentence and nothing else needs a canonical wording.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter. Do not hand-maintain a parallel list of
related programs, domains, or risks (contract §8).
-->

## Scope

One sentence: what ttheir team owns.

## Key Contacts

Name and what to go to them for. One line each.

## Notes

Standing context — how the team works, where the seams are. Omit if there is none.

---

# Live References

## Notes That Reference This Team
```dataview
LIST
FROM ""
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
