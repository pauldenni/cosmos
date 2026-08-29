---
type: prep
mode: meeting
meeting: weekly-pmo
attendees: []
programs: []
related_risks: []
related_decisions: []
date: 2026-05-17
tags:
  - prep
  - prep-meeting
  - weekly-pmo
---

# Weekly PMO / Product / Eng Sync — 2026-05-17

<!--
Cross-functional execution sync.

Cap: 400 words. Obeys .cosmos/instructions/output-contract.md.

Write only the sections with something real in them. Delete the rest — an
empty heading is noise. Each item is stated ONCE, at the altitude that helps
the operator act. For a risk or decision, embed its canonical line rather than
restating it:  ![[work/risks/<risk>#Line]]
-->

## Walk Out With

What the operator wants decided, aligned on, or surfaced by end of meeting. One to three lines, imperative.

## Cross-Functional Status

One row per program that moved or is blocked. `Trend` uses the enum only: `New`, `Increasing`, `Stable`, `Decreasing`, `Resolved`. `Blocker / Dependency / Ask` covers inter-team handoffs — do not give dependencies a second table.

| Program | Trend | Blocker / Dependency / Ask |
|---|---|---|

## Decisions Needed

Only decisions that need this room. One row each; embed the decision's `## Line` for detail. Omit the section if there are none.

| Decision | Who Decides | By When |
|---|---|---|

## Raise

What the operator brings that is not in the status table — risks to escalate, alignment drift between Product/Eng/Design, sequencing and rollout concerns. One line each, with the ask and the reason it is today's problem.

Group under `### Escalate`, `### Alignment`, or `### Sequencing` **only if** more than one item shares a heading. Do not emit empty buckets.

## Notes

<!--
The single capture section. the operator writes here during and after the meeting.

/sync treats everything below this heading as post-meeting writeback and
propagates it to persistent state: decisions route to work/decisions/,
commitments surface owners and timing, program and risk movement lands on the
entity file. the operator's observation here beats shared docs when it is more recent.

Do not pre-fill this section. Do not add separate Decisions Made, Action
Items, or Follow-Ups scaffolds — record them here as they happen.
-->
