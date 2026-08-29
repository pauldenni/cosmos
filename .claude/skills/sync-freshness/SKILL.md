---
name: sync-freshness
description: Deterministically answer "should I /sync before this prep/brief?" by finding the last /sync and reporting which caller-supplied in-scope files were modified after it. Use during the /prep pre-flight Sync Freshness check and the /brief Sync Freshness block. Settles the file-mtime comparison; the three-state verdict (✓ Current / ◑ reading N unsynced / ⚠ recommend sync) is the caller's judgment on top of the facts it returns.
---

# Sync Freshness

## What this is

A bundled script that does the deterministic half of cosmos's "is persistent state fresh for this work?" check: locate the last `/sync` and compare it against the in-scope files. It removes the bit that's easy to get wrong — finding the right sync timestamp and comparing modification times — while leaving the semantic judgment (what counts as in-scope, and whether an unsynced note is *material*) to the caller.

## When to use it

- The **`/prep` pre-flight Sync Freshness check** and the **`/brief` Sync Freshness block**.
- The caller first decides the **in-scope file set** (for `/prep <person>`: their 1:1s, notes mentioning them, their owned programs/risks; for `/brief <topic>`: that topic's notes/risks/programs; portfolio scope = the relevant inbox/journal set), then passes those paths to the script.

## How to run it

```bash
python3 .claude/skills/sync-freshness/check_freshness.py <in-scope files/globs ...>
```

Example (a Zach prep):
```bash
python3 .claude/skills/sync-freshness/check_freshness.py \
  journal/meetings/1on1s/alex/*.md \
  work/risks/search-capacity-headroom.md \
  inbox/060526-*.md
```

`--json` for machine-readable output. `--sync-log-dir <dir>` to override (default `journal/sync-log`).

## What it returns

- **Last /sync**: the sync-log file with the latest `MMDDYY` filename date (tie-break by mtime); its mtime is the freshness threshold.
- **Per file**: `NEWER` (modified after the last sync — unsynced), `CURRENT`, or `MISSING` (path not found — fix it).
- **A deterministic verdict** plus the decision framing.

## Turning the output into the pre-flight verdict

The script gives the facts; you choose the three-state verdict:

| Script result | Your verdict |
|---|---|
| 0 newer | **✓ Current** — state is fresh for this work; no sync needed. |
| ≥1 newer, all ordinary writeback (1:1 / inbox / meeting notes) | **◑ Reading N unsynced note(s) directly** — the prep/brief reflects them; persistent state won't until you `/sync`. Not required first. |
| ≥1 newer where a note introduces a **new risk / changed decision / ownership change** | **⚠ Recommend /sync first** — name the note and why; syncing first yields correct cross-links/trends. |
| no sync-log at all | **⚠ Recommend /sync first** — never synced. |

## Boundary

The script never recommends running `/sync` on its own authority and never runs it — `/prep` and `/brief` stay read-only on persistent state. It only reports freshness facts; escalating to ⚠ is a judgment about *materiality* that stays with the caller.
