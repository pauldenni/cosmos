---
type: person
role: ""
team: ""
manager: ""
domains: []
programs: []
related_risks: []
aliases: []
tags:
  - person
  - entity
---

<!--
Cap: 300 words, excluding ## History and the Live References queries.
Obeys .cosmos/instructions/output-contract.md.

No `## Line` here, deliberately. The `## Line` mechanism exists so a *claim* has
one wording that every artifact embeds. A person is not a claim. A fixed
canonical sentence about a colleague, auto-embedded into briefs and preps, would
propagate a calcified judgment about a human without re-examination. People are
referenced by wikilink — [[Beverly]] — and their state is read fresh.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Relationships live in frontmatter and in the queries below. Do not hand-maintain
a parallel list of related programs, risks, or decisions (contract §8).
-->

## Current Role

One or two sentences: what they own and where they sit.

## Ownership Areas

What they are accountable for. One line each. The org-wide view lives in `[[work/ownership-map]]` — this is their slice, not a re-narration of it.

## Leadership Notes

Growth, overload, alignment signal. One line each. Trend reads live in `[[work/org-health]]`; this file is the longitudinal record for this person.

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

This is where /sync migrates dated observations aged out of
`work/org-health.md`'s People Observations window — the person file is the
system-of-record home for their longitudinal record. When a 5th entry lands,
move the oldest to the matching file under `archive/`.
-->

---

# Live References

## Notes That Reference This Person
```dataview
LIST
FROM ""
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```

## Active Risks Owned By This Person
```dataview
TABLE severity, trend, program, last-updated
FROM "work/risks"
WHERE owner = this.file.link OR contains(owner, this.file.link) OR contains(owners, this.file.link)
SORT severity DESC, last-updated DESC
```

## Decisions Owned By This Person
```dataview
TABLE status, program, last-updated
FROM "work/decisions"
WHERE owner = this.file.link OR contains(owner, this.file.link) OR contains(owners, this.file.link)
SORT last-updated DESC
```

## Mentions In Journal
```dataview
LIST
FROM "journal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
