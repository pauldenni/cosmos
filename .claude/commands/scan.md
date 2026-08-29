# /scan

Internal operational diagnostic. For your eyes — blunt, analytical, not packaged for upward share.

## Modes

```
/scan risks              risk landscape across the portfolio
/scan team               team / org health
/scan program <name>     deep dive on one program
/scan patterns           recurring themes / executive patterns
/scan retro              portfolio retrospective (cycle-end)
/scan life-patterns      longitudinal analysis of personal life patterns (requires 4+ life-reflects)
```

Difference from `/brief`: a scan is a diagnostic for you. A brief is a packaged output for someone else. Same source material; different tone, depth, and audience.

## Read-only on persistent state

`/scan` reads `work/`, `people/`, recent `journal/`, and `inbox/`. It **does not write** to persistent state — only `/sync` does that. If a scan surfaces material new signal (e.g. a previously-unknown risk), mention it in the chat reply so the user can decide whether to run `/sync`.

## Sync Freshness check (print before the scan)

A scan is a diagnostic against current state, so an out-of-date `/sync` matters more here than for `/prep` or `/brief` — but the trigger is still signal-based, not time-based. Print this short block before the scan output:

```
### Sync Freshness
**Last /sync:** <date/run of newest journal/sync-log/*.md>
**In-scope notes newer than last sync:** <none | list inbox/journal files in scope with mtime later than last sync>
**Verdict:** <✓ Current | ◑ Reading N unsynced note(s) directly | ⚠ Recommend /sync first>
```

- **Scope** = the scan's subject: `risks` → risk files plus risk-flagged inbox/journal; `program <name>` → that program's notes and risks; `team`, `patterns`, `retro`, `life-patterns` → the whole portfolio.
- **Compute it with the `sync-freshness` skill.** The three-state verdict is defined there.

  ```bash
  python3 .claude/skills/sync-freshness/check_freshness.py <in-scope files/globs ...>
  ```

- A scan's value is an accurate read of *synced* state, so for `risks` and `program` scopes lean toward ⚠ when in doubt.
- **Recommend, never auto-run.** `/scan` stays read-only on persistent state.

## Inputs by mode

### `/scan risks`
- All `work/risks/*.md`
- `work/dashboard.md`
- Recent `inbox/*.md` flagged as risks
- Previous `journal/scans/risks/*-scan-risks.md` (for trend comparison)

### `/scan team`
- All `people/*.md` and `people/teams/*.md`
- `work/org-health.md`
- `work/ownership-map.md`
- Recent 1:1 notes in `journal/meetings/`
- Recent `inbox/*.md` tagged with people
- Previous `journal/scans/team/*-scan-team.md`

### `/scan program <name>`
- `work/programs/<name>.md`
- Risks, decisions, goals linked to this program
- Recent meeting notes touching this program
- Inbox notes tagged with this program
- Previous `journal/scans/program/*-scan-program-<name>.md`

### `/scan patterns`
- `work/executive-patterns.md`
- Last 60-90 days of journal artifacts across all subfolders
- Resolved + active risks (look for repeats)
- Previous `journal/scans/patterns/*-scan-patterns.md`

Be conservative — patterns require multi-week recurrence and multi-source support.

### `/scan retro`
- All `work/goals/*.md` (including recently archived)
- All `work/programs/*.md` over the cycle period
- Previous `journal/scans/retro/*-scan-retro.md`
- `work/executive-patterns.md`

Cycle period defaults to last 6 months unless specified.

### `/scan life-patterns`

Longitudinal analysis of personal life patterns. **Requires at least 4 prior `/prep life-reflect` files** to generate meaningful pattern signal. If fewer than 4 exist, note the gap and generate a lighter version based on what's available — do not refuse to run.

- `journal/personal/life-reflect/` — all life-reflect files available (read all of them, oldest first)
- `home/areas/*.md` — all life area files
- `home/goals/*.md` — all personal goals (active and archived)
- `home/intentions/*.md` — all intentions
- `home/dashboard.md` — current home state
- Previous `journal/scans/life-patterns/*-scan-life-patterns.md` — most recent prior scan for comparison

**Do not read:** work state, people files, meeting notes, or briefs. This scan is exclusively about the personal life domain.

**Tone:** Same blunt diagnostic standard as all scans. The goal is to find patterns the operator might not be seeing himself — the gap between stated values and actual behavior, the goal that keeps not moving, the area that's been neglected for months while they tell themselves he'll get to it. No hedging.

**Minimum useful signal:** 4+ life-reflects covering at least 4 different weeks. Before that threshold, `/scan life-patterns` should note it's running in early-signal mode and the patterns identified are tentative.

**Use case:** Run quarterly, or whenever you want a longer view on whether the personal investments you're making are actually producing the life you want.

## Templates

```
/scan risks      → reference/templates/scan-risks.md
/scan team       → reference/templates/scan-team.md
/scan program    → reference/templates/scan-program.md
/scan patterns   → reference/templates/scan-patterns.md
/scan retro      → reference/templates/scan-retro.md
/scan life-patterns → reference/templates/scan-life-patterns.md
```

## Output file paths

```
/scan risks              → journal/scans/risks/MMDDYY-scan-risks.md
/scan team               → journal/scans/team/MMDDYY-scan-team.md
/scan program <name>     → journal/scans/program/MMDDYY-scan-program-<name>.md
/scan patterns           → journal/scans/patterns/MMDDYY-scan-patterns.md
/scan retro              → journal/scans/retro/MMDDYY-scan-retro.md
/scan life-patterns      → journal/scans/life-patterns/MMDDYY-scan-life-patterns.md
```

**Folder creation:** If the mode subfolder does not yet exist, create it before writing the file. Do not write flat into `journal/scans/`.

If a file at the target path already exists for today, refresh it in place.

## Final check

Before finishing:
- **Within cap — 600 words.** Lint the file and fix every `ERROR`:

  ```bash
  python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py <the scan file>
  ```

- **Single-home self-check.** Scan templates are the worst offenders: one finding legitimately belongs in Recurring Patterns, Emerging Themes, Cross-Cutting Friction, Strategic Implications, and Leadership Asks. That is five retellings of one idea. State it once, at the altitude where it drives action, and reference it elsewhere in a clause.
- Tone is diagnostic, not exec-packaged — blunt honesty over polish.
- Trend classifications are accurate; do not inflate `Increasing`.
- Patterns are real and recurring; do not manufacture them.
- Leadership Asks are concrete and actionable, not generic.
- **Respect the Scope rule in `CLAUDE.md`.** Scans diagnose the work, never cosmos. If a real work pattern sits underneath a cosmos failure ("decisions get made verbally and never land in artifacts"), describe the work pattern in work language and leave the tool out of the frame.
