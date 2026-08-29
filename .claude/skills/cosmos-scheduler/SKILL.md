---
name: cosmos-scheduler
description: Decide deterministically what cosmos should run and for which meetings. Turns a raw Google Calendar payload into a routed prep work order (filtering focus blocks, declined events, broadcasts, and build noise), and decides whether /sync is due based on unincorporated signal rather than a clock. Used by the cosmos-morning and cosmos-evening scheduled tasks, and on demand to preview what is due.
---

# Cosmos Scheduler

## What this is

Two bundled scripts that make the "what should run now?" decision deterministic instead of a judgment call the operator has to remember to make.

Claude does the I/O that needs MCP — fetching the calendar. Everything downstream is plain Python, so routing decisions do not vary run to run and can be tested offline.

```
Google Calendar MCP ──> raw calendar JSON     (Claude; the only MCP step)
                              │
                    resolve_meetings.py  ── filter · classify · route
                              │
                        whats_due.py     ── + sync-freshness + cadence-status
                              │
                    ordered plan: /sync -> /prep -> /now -> overdue cadence
```

## `resolve_meetings.py` — calendar to prep work order

```bash
python3 .claude/skills/cosmos-scheduler/resolve_meetings.py <raw-calendar.json> \
    --date 2026-08-28 --json
```

Reads the raw Google Calendar payload as returned by the Calendar MCP. Emits `preps`, `skipped`, and `unrouted`.

**Filtering.** In a representative week only ~14 of 69 events deserve a prep. Dropped: `FOCUS_TIME` / `OUT_OF_OFFICE` blocks, declined events, all-day blocks, zero-duration reminders, solo holds (one human attendee — some are typed `DEFAULT` and look like meetings), broadcasts at or above 25 attendees, and build/deploy/office-hours noise.

**1:1 detection** requires *both* signals:

```
title matches /\b1:1\b/  AND  exactly 2 non-resource attendees, one of them self
```

Both guards are load-bearing. Every 1:1 on this calendar has three attendees because of a room resource, so a naive `attendees == 2` finds **zero**. And anchoring the regex on the slash rather than the `1:1` suffix parses "Atlas Program / Rollout Strategy" as a 1:1.

**Routing never guesses.** A meeting resolves through `work/meetings/` entity `meeting`/`aliases`/filename to its `journal_path`. If nothing matches, or more than one entity matches equally well, the event lands in `unrouted` with the reason. It is not filed into a kebab-cased folder derived from the title.

That strictness is deliberate: two live collision pairs exist on this calendar ("Atlas Product / Program Weekly Sync" vs. "Atlas Program Rollout", and four "Weekly CMS/Product" variants). A silent fallback would file real meeting history into the wrong folder, where it would quietly stop being found.

**Person matching** prefers `emails:` in `people/*.md`, because after a merger or rebrand the same human routinely appears under several corporate domains — and a domain-naive match silently picks the wrong person or none at all. It falls back to the email localpart, then to the title token matched against `aliases`.

## `list_sources.py` — the pre-flight listing

```bash
python3 .claude/skills/cosmos-scheduler/list_sources.py [--days 14] [--today YYYY-MM-DD] [--json]
```

Emits the Inbox / Journal / Persistent State / Home State / Outcomes-due sections of the `/sync` and `/prep` pre-flight block, already formatted to paste.

**This replaced a prose instruction, and the reason matters for automation.** "Run a directory listing of all required source locations" made Claude improvise a different compound pipeline every run — `for d in journal/scans/*/; do ...; done` and similar. Commands containing shell expansion can only ever be approved **once**; Claude Code will not write a persistent permission rule for them, because it cannot bound what the expansion produces next time. So an unattended run stalled on a prompt that could never be permanently granted. A fixed `python3 …` command is allowlistable, and the audit record is identical every run.

It also resolves the archived risks and decisions whose `## Outcome` is still `_Pending verification — check back <date>_` with a date that has come due — a date comparison that is easy to get wrong by eye.

## `whats_due.py` — should /sync run?

```bash
python3 .claude/skills/cosmos-scheduler/whats_due.py --json
```

Composes `sync-freshness` and `cadence-status` rather than reimplementing them.

**`/sync` is signal-triggered, not clock-triggered.** It is due when any file under `inbox/`, `journal/meetings/`, or `journal/personal/` is newer than the last sync log. A clock-based rule fires when nothing changed and stays quiet right after three notes get written. Age is a backstop only (`--max-sync-age-hours`, default 12) so state cannot rot silently during a quiet stretch.

**Everything else is cadence-triggered** from the two dashboards' Cadence tables, via `cadence-status`. `/sync` is excluded from that path — it is decided by signal.

The emitted `plan` is ordered: `/sync` first, then `/prep`, then `/scan`. Preps must consume fresh state, so the ordering is not cosmetic.

## Boundary

Both scripts **decide**; neither **acts**. They emit a plan. Claude executes it, and Claude alone judges whether a routed prep is worth generating and what goes in it. An `unrouted` entry is data for the operator, not an error — the fix is usually adding a `journal_path` to a `work/meetings/` entity (see the routing repair in `work/meetings/`).
