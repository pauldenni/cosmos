---
type: risk
status: active
severity:
trend:
category: # staffing | rollout | dependency | <other short label>
owner: ""
program: ""
domains: []
systems: []
related_decisions: []
related_goals: []
meetings: []
created: 2026-05-17
last-updated: 2026-05-17
tags:
  - risk
  - active
---

# Risk Name

<!--
Cap: 300 words, excluding ## History. Obeys .cosmos/instructions/output-contract.md.

Write only the sections with something real in them. Delete the rest — an empty
heading is noise. Never leave a bare `-`, a `TBD`, a `_None._`, or a blank table
row behind; omission beats a placeholder.

Relationships live in frontmatter. Do not re-list them in a trailing
`## Related Entities` block — that section is removed (contract §8).
-->

## Line

<!--
ONE sentence, 25 words maximum, stating this risk canonically.

This is the single wording for this fact across the whole vault. Every other
artifact embeds it rather than restating it in fresh words:

    ![[work/risks/search-capacity-headroom#Line]]

Update the sentence here and every artifact carrying it updates too. If you are
writing a second, differently-worded version of this fact somewhere else, that
is the bug this section exists to prevent.

Filled example:
Search capacity headroom has no owner above CMS Product; it rolled back the Collections
cutover and is unstarted on three entity migrations.
-->

## Current Read

Where the risk stands today and what moved since the last read. Do not restate the Line.

## Why It Matters

The consequence if it goes unaddressed. One or two sentences.

## Signals

The evidence. One line each, dated where the date carries weight.

## Mitigation Plan

What is being done, by whom, by when. Omit the section if nothing is underway — say that in Current Read.

## Leadership Action Needed

The specific ask of the operator or above. One line. Omit if there is none.

## History

<!--
Bounded per contract §6. Keeps the 4 most recent dated entries, no more.

Each entry is ONE line, in this exact form:

    - **YYYY-MM-DD** — <what changed, max 25 words>

When a 5th entry lands, move the oldest to the matching file under
`archive/risks/`. Per-run blow-by-blow belongs in `journal/sync-log/`, not here.

Measured before this rule: one risk file was 71% ## History.
-->
