---
type: domain
domain: ""
owner: ""
secondary_owners: []
programs: []
related_risks: []
aliases: []
tags:
  - domain
  - entity
---

<!--
Cap: 250 words, excluding the Live References queries. Obeys
.cosmos/instructions/output-contract.md (no cap row exists for domain entities;
this is a reference definition file, so keep it short).

No `## Line` here. `## Scope` already serves as the canonical one-sentence
identity, and no artifact embeds a domain definition. Keep Scope to one sentence
and use one term per concept vault-wide (contract §2).

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter and in the queries below. Do not hand-maintain
a parallel list of related programs, risks, or decisions (contract §8).
-->

## Scope

One sentence: what falls inside this domain and what does not.

## Primary Owner

Who owns it. One line.

## Secondary / Consulted Owners

Who else has a say, and on what. One line each. Omit if there is no one.

## Leadership Notes

Standing context — contested edges, ownership ambiguity, escalation history. Omit if there is none.

---

# Live References

## Risks Related To This Domain
```dataview
TABLE severity, trend, owner, last-updated
FROM "work/risks"
WHERE contains(domains, this.file.link) OR contains(file.outlinks, this.file.link)
SORT severity DESC, last-updated DESC
```

## Decisions Related To This Domain
```dataview
TABLE status, owner, last-updated
FROM "work/decisions"
WHERE contains(domains, this.file.link) OR contains(file.outlinks, this.file.link)
SORT last-updated DESC
```

## People Connected To This Domain
```dataview
LIST
FROM "people"
WHERE contains(file.outlinks, this.file.link)
SORT file.name ASC
```

## Mentions In Journal
```dataview
LIST
FROM "journal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
