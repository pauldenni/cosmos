---
title: "Operational Dashboard"
last-updated: 2026-05-17
status: active
tags:
  - dashboard
---

# Operational Dashboard

**Last Updated:** YYYY-MM-DD (via `/sync`)

<!--
Cap: 600 words. Nine H2 sections, and that is the whole set. Obeys
.cosmos/instructions/output-contract.md.

Always-current operational read, written and maintained by /sync. Hand edits get
overwritten on the next sync.

===================================================================
STATE EACH FACT ONCE. This is the rule this file exists to enforce.
===================================================================

Measured before this rule: one decision conflict appeared EIGHT times on this
board — in the Executive Summary, a posture table, Top Priorities, Active Risks,
Key Decisions Pending, Leadership Watchouts, Program Status, and Recent
Activity. Eight retellings of one fact, each in slightly different words.

Single-home mapping (contract §5). A fact is stated IN FULL in exactly one place:

  | Fact                  | Stated in full here                        |
  |-----------------------|--------------------------------------------|
  | Pending decision      | Key Decisions Pending row + work/decisions/ |
  | Risk detail           | work/risks/<r>.md                           |
  | Program detail        | work/programs/<p>.md                        |
  | Goal detail           | work/goals/<g>.md                           |
  | Ownership / overload  | work/ownership-map.md                       |
  | Org-health trend      | work/org-health.md                          |
  | Per-run blow-by-blow  | journal/sync-log/MMDDYY-sync.md             |

Everywhere else on this board it is ONE of:
  - an embed of the entity's canonical line — ![[work/risks/<r>#Line]]
  - a single clause plus a wikilink
Never a second paragraph that re-derives the same fact in fresh words.

Before publishing: take the run's two or three biggest items and confirm each is
detailed in exactly one section here.

Other standing rules for this file:
  - No `## Top Priorities` section. Priority order is carried by the Executive
    Summary's sentence order. A separate priorities block re-narrates every item
    already in the tables below — that is where four of the eight retellings
    came from.
  - No dataview code blocks. `Notes Created Today` and `Unfinished Tasks` render
    nothing in a plain read and cost ~40 lines.
  - No `# History` section. Per-run history lives in journal/sync-log/; this
    board carries only the `# Recent Activity` pointer at the bottom.
  - No placeholders. Empty table body, or omit the section. Never a bare `-`, a
    `TBD`, a `_None._`, or a `| | | |` row.
  - Prune closed/resolved rows older than 2 days from the tables below.
-->

## Executive Summary

<!--
ONE rewritten current-state read, regenerated from scratch each run. Maximum
~180 words / ~6 sentences.

Do not stack `**Update (Nth run)**` paragraphs. Do not keep an `## Earlier
(rolled up)` block. Fold still-live facts into the one narrative and drop what
is stale.

Name the top items; do not re-derive them — the tables below carry the detail.
The test: this reads as "here is where things stand today," not "here is what
happened across the last three runs."
-->

## Active Risks

<!-- One row per active risk. Severity column replaces the old High/Medium
section split. The `Read` cell is one clause or an embed of the risk's `## Line`
— never a paragraph. Detail lives in work/risks/<r>.md. -->

| Risk | Severity | Trend | Owner | Read | Leadership Action |
|---|---|---|---|---|---|

## Programs

<!-- One row per active program. Detail lives in work/programs/<p>.md. -->

| Program | Status | Trend | Owner | Read | Leadership Action |
|---|---|---|---|---|---|

## Key Decisions Pending

<!-- This table is the system of record for pending decisions on this board.
Nothing else here re-states a pending decision — the Executive Summary may name
it in a clause, and Leadership Watchouts may flag it, but the call, the owner,
and the date live only here and in work/decisions/<d>.md.

On closure, stamp the Status cell `Closed YYYY-MM-DD — <reason>` so the 2-day
prune clock can be computed on later runs. -->

| Decision | Owner | Needed By | Status | Linked Artifact |
|---|---|---|---|---|

## Goals

<!-- One row per active goal. Trajectory and trend carry the "at risk" and
"stalled" signal — do not also list those goals under Leadership Watchouts. -->

| Goal | Trajectory | Trend | Owner | Adjustment Needed |
|---|---|---|---|---|

## Leadership Watchouts

<!-- Only what is NOT already a row above. If a watchout is a risk, a decision,
or a goal trajectory, it belongs in that table, not here.

What legitimately lives here: overloaded ownership, dependency concentration,
recurring alignment friction, escalation likelihood, and artifacts awaiting
review or formal adoption. One line each, with a wikilink to the system of
record. Omit the section entirely on a quiet run. -->

## Recent Outcomes

<!-- The last ~5 verified outcomes, newest first. One line each:
verdict + one clause of evidence + [[archive/...]] link. Drop entries older than
~30 days. This is the visible proof that closed→outcome tracking ran. -->

## Cadence

<!-- Last-run dates for recurring work command modes. /sync sets `Last Run` from
the newest matching journal file; `Status` is then recomputed deterministically
by the cadence-status skill — never by hand. The rule lives in the skill and in
CLAUDE.md; do not restate it here.

Home cadences (`/prep life-reflect`, `/prep life-goals`, `/scan life-patterns`)
are tracked in home/dashboard.md ONLY. Never add them to this table.

Event-driven commands (`/brief`, `/prep <person>`, `/prep <meeting>`,
`/scan program <name>`) run when needed and never appear here. -->

| Command           | Last Run | Expected                | Status |
| ----------------- | -------- | ----------------------- | ------ |
| `/sync`           | —        | daily (2-3× per day)    | —      |
| `/prep reflect`   | —        | weekly                  | —      |
| `/scan risks`     | —        | monthly                 | —      |
| `/scan team`      | —        | monthly                 | —      |
| `/scan patterns`  | —        | monthly                 | —      |
| `/scan retro`     | —        | 2× per year (mid + end) | —      |
| `/prep goal-plan` | —        | annual                  | —      |

## State Freshness

<!-- Makes divergence between the always-live files visible at a glance. `As of`
is the last run that MATERIALLY changed the file — never blind-bump it. -->

| File | As of | Refreshed this run? |
|---|---|---|
| [[work/org-health]] | — | — |
| [[work/ownership-map]] | — | — |
| [[work/executive-patterns]] | — | — |

# Recent Activity

<!-- Pointer only — the most recent ~5 runs, newest first. Drop the oldest line
so the list never grows past ~5. The run detail lives in journal/sync-log/. -->

- **YYYY-MM-DD** (Nth run) — <one-line summary of the run's headline moves>. → [[journal/sync-log/MMDDYY-sync]]

_Older runs: see `journal/sync-log/`._
