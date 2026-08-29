# /brief

Produce an upward-facing brief for leadership.

## Modes

```
/brief vp [topic]       VP-level update
/brief svp [topic]      SVP-level update (also covers exec briefs)
/brief short [topic]    3-5 bullets, ultra-tight
```

`[topic]` is optional. If omitted, the brief covers the overall portfolio. If provided, it scopes to that program, person, or initiative (e.g. `/brief vp atlas`, `/brief short search`).

Level controls altitude and tone:
- **vp** — exec-ready, decision-focused, week-scoped
- **svp** — strategic narrative, longer time horizon, leadership-level framing
- **short** — 3-5 bullets, highest signal only

## Read-only on persistent state

`/brief` reads `work/`, `people/`, recent `journal/`, and `inbox/` to produce the brief. It **does not write** to persistent state — only `/sync` does that. The brief is a packaged artifact for someone else's eyes.

If `/sync` hasn't run today, the brief still works — it reads inbox/journal directly. But state-level artifacts (`work/dashboard.md`, etc.) may lag if you've added significant signal since the last sync.

## Sync Freshness check (print before the brief)

Answer the recurring "should I `/sync` first?" question with a signal-based verdict, not a time-based guess — `/brief` reads inbox/journal directly, so a stale sync rarely degrades the brief itself; the real question is whether there's *unincorporated signal in this brief's scope*.

Print this short block before the brief:

```
### Sync Freshness
**Last /sync:** <date/run of newest journal/sync-log/*.md>
**In-scope notes newer than last sync:** <none | list inbox/journal files in scope with mtime later than last sync>
**Verdict:** <✓ Current | ◑ Reading N unsynced note(s) directly | ⚠ Recommend /sync first>
```

- **Scope** = the topic if scoped (`/brief vp atlas` → Atlas notes, risks, programs), else the whole portfolio.
- **Compute it with the `sync-freshness` skill.** The three-state verdict is defined there.

  ```bash
  python3 .claude/skills/sync-freshness/check_freshness.py <in-scope files/globs ...>
  ```

- **Recommend, never auto-run.** `/brief` stays read-only on persistent state.

## Inputs

- `work/dashboard.md` (the current operational read)
- `work/risks/*.md` (filter by topic if scoped)
- `work/programs/*.md` (filter by topic if scoped)
- `work/goals/*.md`
- `work/decisions/*.md` (especially pending)
- `work/org-health.md`, `work/executive-patterns.md` (for narrative framing)
- Recent `journal/briefs/*.md` (for continuity and delta detection)
- `journal/scans/` recent files (for diagnostic signal that fed this brief)
- `inbox/*.md` not yet incorporated (capture fresh signal)
- The historical executive deck in `.cosmos/instructions/primary-sources.md` (for trend validation and tone calibration)

## Delta-based synthesis

A brief is not a status dump. It synthesizes:
- what changed since the last brief at this level
- what materially worsened or improved
- what requires decision or air cover
- what's quietly continuing to matter

If you ran `/brief vp` last Thursday, today's `/brief vp` should focus on what's *different*. Don't restate stable items unless leadership attention is still required.

## Templates

```
/brief vp     → reference/templates/brief-vp.md
/brief svp    → reference/templates/brief-svp.md
/brief short  → reference/templates/brief-short.md
```

## Output file paths

Portfolio-level briefs (no topic) go into a level-named subfolder:

```
/brief vp                → journal/briefs/vp/MMDDYY-brief-vp.md
/brief svp               → journal/briefs/svp/MMDDYY-brief-svp.md
/brief short             → journal/briefs/MMDDYY-brief-short.md
```

Topic-scoped briefs go into a topic-named subfolder, regardless of level:

```
/brief vp <topic>        → journal/briefs/<topic>/MMDDYY-brief-vp-<topic>.md
/brief svp <topic>       → journal/briefs/<topic>/MMDDYY-brief-svp-<topic>.md
/brief short <topic>     → journal/briefs/<topic>/MMDDYY-brief-short-<topic>.md
```

Both `journal/briefs/vp/` and `journal/briefs/svp/` already exist. Topic subfolders (e.g. `atlas`, `search`) are created automatically if they don't exist. Use the topic slug as-is, lowercase.

If a file at the target path already exists for today, refresh it in place.

## Final check

Before finishing:
- Leads with movement, not activity — the first bullet of `## What Moved` (vp) or the opening of `## Narrative` (svp) is the headline
- Decisions are actionable, with named decider and timing
- Risks have trend + leadership ask
- **Within cap** — short 150 words, vp 300, svp 400. Lint the file and fix every `ERROR`:

  ```bash
  python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py <the brief file>
  ```

- **Single-home self-check** — take the two or three biggest items. Each is stated in full exactly once. A `## TL;DR` that restates what `## What Moved` already says is one item written twice; cut one.
- **No `## Related Entities` section** re-listing links already in frontmatter and the body.
- Tone matches audience: vp executive-ready, svp strategic, short brutal compression.
- **Respect the Scope rule in `CLAUDE.md`.** Briefs go to an audience that does not know or care about cosmos. Only the corrected work fact appears, never the mechanism that misread it.
