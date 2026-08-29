---
type: program
program: ""
status:
trend:
owner: ""
systems: []
related_risks: []
related_decisions: []
aliases: []
tags:
  - program
  - entity
---

<!--
Cap: 500 words, excluding ## History and the Live References queries.
Obeys .cosmos/instructions/output-contract.md.

Write only the sections with something real in them. Delete the rest. Never
leave a bare `-`, a `TBD`, a `_None._`, or a blank table row behind.

Risks and decisions are detailed in their own files and surface here as a clause
plus a link, or as an embed of their `## Line`. Do not re-narrate them.
-->

## Line

<!--
ONE sentence, 25 words maximum, stating this program canonically — what it is
delivering and where it currently stands.

This is the single wording for this fact across the whole vault. Every other
artifact embeds it rather than restating it in fresh words:

    ![[work/programs/Atlas#Line]]

Update the sentence here and every artifact carrying it updates too.

Filled example:
Atlas replaces the legacy CMS for channel and collection curation; rollout is
mid-migration and gated on Search capacity headroom and rights-data coverage.
-->

## Current Read

Where the program stands today and what moved since the last read. Do not restate the Line.

## Current Priorities

The two or three things the program is actually driving now. One line each.

## Open Risks & Decisions

One line each, as a link or an embed of the entity's `## Line`. The detail lives in `work/risks/` and `work/decisions/`, not here.

## Leadership Notes

What needs the operator or above. One line each. Omit if there is none.

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

When a 5th entry lands, move the oldest to the matching file under
`archive/programs/`. Per-run blow-by-blow belongs in `journal/sync-log/`.

Measured before this rule: work/programs/Atlas.md was 88% dated changelog —
7,248 of 8,252 words. This section is where that happened.
-->

---

# Live References

## Active Risks
```dataview
TABLE severity, trend, owner, last-updated
FROM "work/risks"
WHERE program = this.file.link OR contains(program, this.file.link) OR contains(programs, this.file.link)
SORT severity DESC, last-updated DESC
```

## Related Decisions
```dataview
TABLE status, owner, last-updated
FROM "work/decisions"
WHERE program = this.file.link OR contains(program, this.file.link) OR contains(programs, this.file.link)
SORT last-updated DESC
```

## Mentions In Journal
```dataview
LIST
FROM "journal"
WHERE contains(file.outlinks, this.file.link)
SORT file.mtime DESC
```
