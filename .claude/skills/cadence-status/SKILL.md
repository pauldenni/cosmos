---
name: cadence-status
description: Deterministically recompute the Status column of cosmos cadence tables (Command | Last Run | Expected | Status) in work/dashboard.md and home/dashboard.md. Use during /sync after updating each row's Last Run, instead of hand-computing Status. Settles the overdue-day count and the Expected→interval mapping that hand-computation gets wrong.
---

# Cadence Status

## What this is

A bundled script that recomputes the `Status` column of every cadence table in a cosmos dashboard from each row's `Last Run` and `Expected`. cosmos's status rule is pure date math, but doing it by hand each `/sync` is where the `overdue Nd` count and the interval mapping drift. This makes Status a derived, deterministic value.

## When to use it

- During `/sync`, **after** the `Last Run` values have been refreshed (the cadence row → file-pattern mapping step). `/sync` sets `Last Run`; this skill sets `Status`.
- Any time you want to verify or refresh dashboard cadence Status.

## How to run it

```bash
# Preview (non-destructive) — prints each row's recomputed status and what changed
python3 .claude/skills/cadence-status/compute_cadence.py work/dashboard.md home/dashboard.md

# Apply — rewrite the Status column in place
python3 .claude/skills/cadence-status/compute_cadence.py --write work/dashboard.md home/dashboard.md
```

With no file args it defaults to `work/dashboard.md` and `home/dashboard.md` (if present). `--json` emits machine-readable rows. `--today YYYY-MM-DD` pins the reference date (used for testing; defaults to the system date).

It finds **every** table whose header contains `Command`, `Last Run`, `Expected`, and `Status` (so both the work cadence table and a "Personal Cadence" table in the same file are handled), and rewrites only the `Status` cell — other columns, the separator row, and surrounding content are untouched.

## The status rule (from CLAUDE.md)

| Condition | Status |
|---|---|
| `Last Run = —` (or blank / unparseable) | `—` |
| `days_since ≤ interval_days` | `✓` |
| `days_since > interval_days` | `⚠️ overdue Nd` where `N = days_since − interval_days` |
| `Expected` not recognized | `?` (a finding — fix the wording) |

`days_since = today − Last Run`. Overdue counts days **past** the expected interval, not total days since last run.

### Expected → interval_days

Substring match, case-insensitive (so `daily (2-3× per day)` → `1`):

`daily` 1 · `weekly` 7 · `bi-weekly` 14 · `monthly` 30 · `quarterly` 90 · `semi-annual` / `2× per year` / `twice per year` 180 · `annual` / `yearly` 365

A `?` verdict means the `Expected` string isn't in this map — correct the dashboard wording (or extend the mapping in the script if it's a legitimately new cadence).

## Notes

- A long status (e.g. `⚠️ overdue 12d`) can be wider than a tightly-padded column, so it may overflow the original alignment. This is cosmetic — the markdown table still renders correctly.
- The script only computes Status; it does **not** set `Last Run` (that's `/sync`'s job, from the journal file-pattern mapping). Run the script after `Last Run` is current.
