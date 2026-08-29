# /sync

Pull all operational signal into persistent state. Run 2-3× per day, especially after a series of meetings.

## What it does

`/sync` is the **only** command that writes to persistent state in `work/` and `people/`. It is the propagation step that connects what you wrote (in Obsidian) to what cosmos can synthesize against later.

Read sources, distill signal, update persistent state, archive what's been incorporated.

**All writes obey `.cosmos/instructions/output-contract.md`** — word caps, 25-word sentences, no placeholders, single-home. Persistent state is capped: dashboard 600 words, org-health 600, ownership-map 400, executive-patterns 400, program 500, risk 300. If content will not fit, the fact belongs in its system of record with a pointer here — not compressed into denser prose.

---

## Modes (argument parsing)

`/sync` accepts an optional argument that scopes the run. Default (no args) is the full portfolio pass that has always been the behavior.

```
/sync                  Default. Full portfolio sync. Read inbox + journal +
                       primary sources per recency. Write to all touched
                       persistent state. Refresh dashboard.

/sync full             Same scope as default BUT force-read every configured
                       primary source regardless of how recently it was last
                       read. Use when you want to confirm no source has moved
                       since the last full pass — e.g. before a major
                       stakeholder review.

/sync <scope>          Scoped sync. Read sources and write persistent state
                       only for the named scope. Dashboard still gets a
                       narrow refresh of the affected sections (so today's
                       date and the run's history entry land), but
                       out-of-scope sections of the dashboard are not
                       touched.

/sync full <scope>     Combine: force-read primary sources AND scope writes.
```

### Recognized scope values

Argument matching is case-insensitive.

| Scope | Reads | Writes |
|---|---|---|
| any basename of a file in `work/programs/` (e.g. `atlas`) | inbox notes whose `programs:` includes the scope; recent 1:1s of the program's named owners; recent journal entries linking the program; primary sources whose `Use for:` line mentions the program | `work/programs/<scope>.md`; `work/risks/<r>.md` linked to that program; `work/decisions/<d>.md` linked to that program; `people/<p>.md` for owners of touched entities; narrow dashboard refresh |
| `risks` | inbox notes with `note-type: risk` or non-empty `related_risks:`; all current risk files (for trend context); primary sources tagged as risk-bearing (Pipeline Errors, Weekly CMS Product Sync, PMO/PROD/ENG) | all `work/risks/*.md` with new signal; narrow dashboard refresh of the Risks section |
| `decisions` | inbox notes with `note-type: decision` or non-empty `related_decisions:`; all current decision files | all `work/decisions/*.md` with new signal; narrow dashboard refresh of the Decisions Pending table |
| `people` | inbox notes mentioning specific people; recent 1:1s; `work/org-health.md` | `people/*.md` with new signal; `work/org-health.md`; `work/ownership-map.md`; narrow dashboard refresh of the Watchouts section |
| `home` | inbox notes tagged `domain: Home` only; existing `home/` state | `home/dashboard.md`; `home/areas/*.md`; `home/goals/*.md`; `home/intentions/*.md`. No work writes. |

### Resolution rules

1. Tokenize the argument on whitespace. First token is the mode; remaining tokens are the scope.
2. If the first token is `full`, set `force_primary_sources = true` and treat any remaining tokens as the scope.
3. Otherwise the first token IS the scope and `force_primary_sources = false`.
4. Resolve the scope token in this order:
   - exact match against the reserved keywords (`risks`, `decisions`, `people`, `home`)
   - case-insensitive basename match against `work/programs/*.md`
   - if no match found, stop and ask the operator which scope was meant — list the available program names; do not guess
5. If no scope token at all, scope is `all` (full portfolio).

### What scoping does NOT change

The pre-flight, the inbox-vs-source recency rule, the trend taxonomy, the closed-row-retention rule, the canonical-entity-index regeneration, the meeting-entity source registration, and the inbox archival rules all apply within the scope. The What Moved block is always printed. The receipt always includes the scope label.

---

## ⚠️ Pre-Flight: Source Declaration (MANDATORY — FIRST OUTPUT)

Before reading any source, before synthesizing anything, before writing any file — print the pre-flight block to chat as the **first and only output** of the run. Do not skip this. Do not combine it with synthesis. Do not proceed until it is complete.

This block is the audit record. If a required source is missing from it, the operator can catch the gap before bad synthesis propagates into persistent state.

**The pre-flight is scope-aware.** Always print the resolved scope at the top. List only the sources actually required by the scope — do not pad with sources that are out-of-scope for this run. Out-of-scope sources should not appear as `[ ]` items, because they were not required; including them dilutes the audit signal. The Gaps section is for in-scope sources that were *required but not read*.

### Step 1 — List the vault

Run the bundled listing script. **Do not hand-write shell commands for this.**

```bash
python3 .claude/skills/cosmos-scheduler/list_sources.py
```

It emits the Inbox, Journal, Persistent State, Home State, and Outcomes-due sections of the pre-flight block, already formatted. Paste its output.

It covers every required location: active inbox notes; 1:1s and other meetings in the last 14 days; the newest scan per mode; newest brief, reflect, life-reflect, and sync-log; the four core `work/` files plus counts for programs, risks, decisions, goals, meetings and people; home state; and the archived risks/decisions whose `## Outcome` is still pending with a check-back date that has come due.

Two reasons this is a script and not a prose instruction. It makes the audit record identical every run, which is the point of an audit record. And an improvised pipeline containing shell expansion (`for d in journal/scans/*/`) can only ever be granted "allow once" — never a persistent permission rule — so it stalls an unattended run every single time.

Use `--days N` to widen the window, `--today YYYY-MM-DD` to reproduce a past run, `--json` for machine-readable output.

### Step 1b — Tabulate task state per inbox note (MANDATORY)

Archive-eligibility is decided **deterministically by the bundled `inbox-archive-tabulation` skill**, not by reading interpretation. Run its script once across all inbox notes:

```bash
python3 .claude/skills/inbox-archive-tabulation/tabulate_followups.py inbox/*.md
```

The script reads each note's frontmatter `status` and counts checkbox state inside the `## Follow-Up Needed` section (case-insensitive, indentation- and `*`-bullet tolerant, section-scoped — boxes elsewhere are ignored), then emits a verdict per file. **Paste its output verbatim** into the Pre-Flight block under:

```
### Inbox task state (deterministic tabulation)
<script output — one line per note, with open tasks listed under HOLD / ARCHIVE verdicts>
```

The verdict column encodes the archival rules; they are defined in the skill, not here.

**The script's output is the only source of truth for archival eligibility this run.** If narrative synthesis disagrees with the script, the script wins — re-run it and re-verify before publishing the receipt. Reading interpretation of checkbox state is forbidden as the basis for the decision.

The script settles the deterministic half (status plus checkbox state). Whether an `ARCHIVE-ELIGIBLE` note has been *fully synthesized* remains your judgment.

### Step 2 — Declare what you actually read

Print this block, filled in. One line per source actually in scope. Do not pad with out-of-scope sources.

```
## /sync Pre-Flight — Source Declaration
**Date:** YYYY-MM-DD
**Scope:** <all | full | <program> | risks | decisions | people | home | ...>
**Force primary sources:** <true | false>

### Inbox
[x] `inbox/<file>` — <note type / topic>

### Inbox task state (deterministic tabulation)
<script output from Step 1b, verbatim>

### Journal (last 14 days)
[x] `journal/meetings/1on1s/<person>/<file>` — <person, date>
[x] `journal/meetings/<subdir>/<file>` — <meeting, date>
[x] `journal/scans|briefs|personal/<most recent per type>`

### Configured Primary Sources
[x] <source name> — <date of most recent entry read>
(one line per in-scope source in .cosmos/instructions/primary-sources.md)

### Existing Persistent State
[x] <file or directory> — <count read>

### Home State
(include only when domain:Home inbox notes exist)

### Gaps
[ ] <source> — <why not read>
```

List a source under `Gaps` only if it was in scope and not read. Omit any section with nothing in it — an empty heading is noise, not an audit record.

Then state in one line that pre-flight is complete, naming any gaps. Synthesis begins after that line.

---

## Sources (read order)

The read order below is for the default (full) scope. **Apply the scope filter at each step** — when the scope is a program, "Inbox" means inbox notes touching that program, "Recent journal entries" means 1:1s with its owners plus journal entries linking it, and "Configured Primary Sources" means only sources whose `Use for:` matches it. The read-order discipline (inbox first, then journal, then primary sources, then persistent state) does not change.

1. **Inbox** — `inbox/*.md` not yet archived. Highest precedence on any conflict. Inspect each note's `domains:` frontmatter field — notes listing `Home` route to home persistent state; notes without `Home` route to work persistent state. Notes can route to both if they span domains.
2. **Recent journal entries** — last 7 days of `journal/meetings/` (1:1 notes live in `journal/meetings/1on1s/<person>/` — traverse all person subfolders), `journal/scans/`, `journal/briefs/`, `journal/personal/` (traverse all subfolders including `weekly-reflection/` and `life-reflect/`).

   **Journal re-read discipline (MANDATORY — no recency shortcut applies):**

   Journal files are *not* like primary sources. A `/prep` artifact in `journal/meetings/` is **both the prep and the live-meeting notes** — the operator writes into it during and after the meeting, often inline in the existing "Notes" section. Every `/sync` run must therefore:

   - **Compute `mtime > <last_sync_timestamp>`** for every file in the last-7-days journal window. Any file whose mtime is later than the last sync timestamp MUST be re-read on this run.
   - **Never claim "no material moves" based on session memory of a journal file.** If the file was modified since the last sync — even if you wrote it earlier in this same session — re-read it from disk before reporting deltas.
   - **The harness's "file unchanged since your last Read" signal is not authoritative for `/sync`.** That signal is based on the harness's diff cache, which can mark a file unchanged even when a linter or external editor has modified it. Use the file's actual mtime as the source of truth.
   - **Prep artifacts are not exempt.** Files like `journal/meetings/<meeting>/<date>-<meeting>.md` and `journal/meetings/1on1s/<person>/<date>-<person>-1on1.md` are the canonical location of live-meeting notes. If they've been modified since the prior sync, they almost certainly contain new signal — read them, do not skip them.
   - If a journal file has a `## Notes` or `## Notes (filled in during/after)` section with content that wasn't there at the prior sync, that content is post-meeting writeback signal — propagate it per the file's "Post-1:1 Write-Back Guidance" (for 1:1s) or per general inbox-vs-source rules.
   - **Meeting-note attribution discipline:** for each `journal/meetings/<folder>/` note, resolve `<folder>` to its `work/meetings/` entity (match on `journal_path`, falling back to `meeting` / `aliases` / filename) and apply that entity's `## My Role / Attendance Posture` block per `.cosmos/instructions/attribution-discipline.md` when deciding owners, decisions, and action items drawn from that note. If no posture block exists, apply the core principle in that file.
3. **Configured Primary Sources** — see `.cosmos/instructions/primary-sources.md`. For each source, check for a `Reading:` hint and follow these rules:
   - **Standard hint** (`start:` + `depth:`): use `start:` to determine where to begin reading and `depth:` to bound how much to read.
   - **`structure: child-pages`** (Confluence only): fetch the parent page via Atlassian MCP (`mcp__atlassian__getConfluencePage`), extract the list of child page links, sort by last-modified date or title date descending, and read only those falling within the `depth` window. `start:` does not apply.
   - **Missing hint**: apply the Large File Strategy defaults and add one line to the sync receipt: `Missing Reading: hint — <source name>. Add start: and depth: to its CLAUDE.md entry.`
   - **Recency shortcut (default scope only):** If the prior `/sync` run read this source within the last 24 hours and the source has not been edited since (per the file's modified-date / page revision metadata), it may be skipped — log it in the Pre-Flight Gaps section with reason "fresh from prior sync". **`force_primary_sources = true` disables this shortcut** — every source must be read regardless of recency.
   - **Source attribution discipline:** if a source maps to a meeting entity (match the source URL or name against `work/meetings/*.md` `source:`), apply that entity's `## My Role / Attendance Posture` to attribution from it, per `.cosmos/instructions/attribution-discipline.md`. If no entity matches, apply the core principle in that file.
4. **Existing persistent state** — `work/`, `people/`, for comparison and continuity.

If an inbox note conflicts with a primary source on the same topic, the inbox note wins when more recently dated (or when its frontmatter sets `supersedes_source: true`).

If a journal note conflicts with a primary source on the same topic, the journal note wins when more recently dated — operator's direct observation takes precedence over shared docs.

## What gets written

After distillation, update these files in place. Preserve History sections; append don't replace.

- **`work/dashboard.md`** — refresh all sections. Recompute Cadence by scanning the newest journal file matching each row's pattern. Update `Last Updated`. **Prune closed/resolved rows older than 2 days from the Key Decisions Pending, Current Operational Posture, and Resolved This Run tables** (see "Closed-row retention" below). **Do not append a per-run History section to the dashboard** — the run log lives in `journal/sync-log/` (see "Sync run log" below). The dashboard carries only a `# Recent Activity` pointer.
  - **Executive Summary — rewrite, never stack (current-state collapse).** The Executive Summary is **one** rewritten current-state read, regenerated from scratch each run. **Do not** stack `**Update (Nth run)**` paragraphs, and **do not** keep an `## Earlier (rolled up — DATE)` block. Each run replaces the prior summary with a single fresh narrative of **≤ ~180 words / ~6 sentences**; if you find yourself appending a new paragraph, you're doing it wrong — fold the still-live facts into the one narrative and drop what's now stale. The per-run blow-by-blow (what moved this run, in what order) belongs in `journal/sync-log/`, not on the board. The test: the Executive Summary should read as "here is where things stand today," not "here is what happened across the last three runs."
- **`journal/sync-log/MMDDYY-sync.md`** — the per-run history entry for this sync (see "Sync run log" below).
- **`work/org-health.md`** — update trend reads if signal materially changed. Apply the refresh-or-stamp rule (see "State freshness" below) and the bounded-growth rule (see "Bounded narrative growth" below).
- **`work/ownership-map.md`** — update if ownership changed. Apply the refresh-or-stamp rule.
- **`work/executive-patterns.md`** — only if new patterns emerged (be conservative; patterns require multi-week recurrence). Apply the refresh-or-stamp rule.
- **`work/programs/<program>.md`** — for each program with material movement, update Current Read + trend frontmatter + append dated History entry. Apply the refresh-or-stamp rule per program file.
- **`work/risks/<risk>.md`** — update trend, last-updated, Current Read; append History. Create new risk files for newly surfaced risks. Mark resolved risks `status: resolved` and move to `archive/risks/`. **On resolution, stamp an `## Outcome` section in the archived file:** `**Outcome:** _Pending verification — check back YYYY-MM-DD_` (set the check-back date ~14 days out). The Outcome review step (below) closes it later.
- **`work/decisions/<decision>.md`** — update status/last-updated; append History. Create for newly surfaced decisions. Move superseded decisions to `archive/decisions/`. **On closure, stamp the same `## Outcome` section** in the closed/archived file (`**Outcome:** _Pending verification — check back YYYY-MM-DD_`).
- **`work/goals/<goal>.md`** — update trajectory + trend if materially changed. Move achieved/abandoned goals to `archive/goals/`.
- **`people/<person>.md`** — update overload, growth, alignment notes if signal warrants.

## Single-home discipline

Apply §5 of `.cosmos/instructions/output-contract.md`. Every fact is stated in full in exactly one file; everywhere else it is a clause plus a wikilink, or an embed of the entity's `## Line`.

The dashboard is where this fails most often — a single decision can end up narrated in the Executive Summary, the posture table, a Top Priority, the Key Decisions table, the Watchouts, and the ownership map. Six retellings of one fact.

Dashboard-specific mapping:

| Fact | Stated in full | Elsewhere |
|---|---|---|
| Pending decision | Key Decisions Pending table + `work/decisions/<d>.md` | clause + link |
| Ownership / overload | `work/ownership-map.md` | clause + link |
| Org-health trend | `work/org-health.md` | clause + link |
| Risk detail | `work/risks/<r>.md` | one-line summary + link in Active Risks |
| Program detail | `work/programs/<p>.md` | one-line summary + link in Program Status |
| Per-run blow-by-blow | `journal/sync-log/MMDDYY-sync.md` | `# Recent Activity` pointer |

**Before publishing the dashboard:** take the run's two or three biggest items and confirm each is detailed in exactly one place.

## State freshness (refresh-or-stamp; never blind-bump)

The four always-live work files (`dashboard`, `org-health`, `ownership-map`, each `work/programs/*`) drift out of sync with each other when some runs refresh one and not the others — a file can read as "live" while carrying a two-week-old read, and nothing tells the operator which is current. Fix it by making freshness honest and visible:

1. **Never blind-bump `last-updated` / `As of:`.** Set a file's freshness stamp to today **only when this run materially refreshed its content.** If a run reads `org-health.md`, finds no new people/trend signal, and writes nothing, **leave its prior date** — a stamp must mean "this is current as of," not "/sync looked at it."
2. **Stamp form.** Each always-live work file carries a header line `> **As of:** YYYY-MM-DD` reflecting the last run that materially changed it. (The dashboard's existing `**Last Updated:**` stamp already serves this role for the dashboard.)
3. **Dashboard "State Freshness" mini-table (maintained every default run).** Near the bottom of the dashboard, keep a small table so divergence is visible at a glance:

   ```
   ## State Freshness
   | File | As of | Refreshed this run? |
   |---|---|---|
   | [[work/org-health]] | YYYY-MM-DD | yes / no |
   | [[work/ownership-map]] | YYYY-MM-DD | yes / no |
   | [[work/programs/Atlas]] | YYYY-MM-DD | yes / no |
   | [[work/programs/Meridian]] | YYYY-MM-DD | yes / no |
   ```
4. **Receipt note.** When an always-live file is *not* refreshed on a default-scope run, say so in the What Moved receipt ("org-health not refreshed — no new people/trend signal; as-of remains YYYY-MM-DD"), so "not touched" is a deliberate, visible call rather than a silent gap. (Scoped runs only refresh in-scope files by design — note the out-of-scope ones under the existing Out-of-scope receipt line, not here.)

## Closed-row retention (dashboard tables)

The dashboard reflects **current state**, not closure history. Each `/sync` run must prune closed entries older than **2 days** from these tables:

- **Key Decisions Pending** table — rows where the `Status` cell starts with `**CLOSED**` or `**RESOLVED**`
- **Current Operational Posture** table — rows whose `Trend` is `Resolved` or whose `Status` is `CLOSED`
- **Resolved This Run** risk block — resolved-risk entries

The window is **2 days everywhere** — a closure stays on the board for a couple of days of at-a-glance reads, then the table returns to current-state-only. There is no longer a separate "two sync runs" rule for the Resolved This Run block or a condition-based rule for the posture table; all three use the same 2-day clock.

**Closure-date stamping (required when a row first goes closed):**

So the 2-day clock can be computed on later runs, `/sync` must stamp the closure date inline the moment it transitions a row to a closed/resolved state:
- **Key Decisions Pending** — in the `Status` cell: `Closed YYYY-MM-DD — <reason>` or `Resolved YYYY-MM-DD — <reason>`
- **Current Operational Posture** — append to the `Notes` cell: `(Closed YYYY-MM-DD)`
- **Resolved This Run** — the block is dated by the run that resolved the risk; use that date

**Prune rule (all three tables):**

1. Parse the closure date from the row (the `Status` cell, the `Notes`-cell `(Closed …)` stamp, or the resolved-run date).
2. If `today − closure_date > 2 days`, remove the row from the table.
3. The row's closure context is preserved in three places — do not duplicate it in the table beyond the 2-day window:
   - The `journal/sync-log/MMDDYY-sync.md` entry for the run that logged the closure (see "Sync run log" below)
   - `archive/<decisions|risks>/<name>.md` (the moved entity file, when one exists)
   - The program file's `## What Changed (YYYY-MM-DD)` block
4. If the closure date cannot be parsed from the row, leave it alone and flag it in the sync receipt as a row needing manual cleanup.

**Do not** prune rows whose status is `Open`, `Blocked`, `Deferred`, or `Pre-stage` regardless of age — those represent live state, even if stale, and stale-but-open is itself signal worth surfacing.

## Bounded narrative growth (`org-health.md` and other narrative files)

The closed-row rule keeps the dashboard *tables* bounded, but the narrative files grow unbounded by stacking dated entries that never collapse — `org-health.md`'s "Overall Read" accretes a new block every run, and "People Observations" stacks dated sub-entries per person going back weeks. The file ends up an archive wearing a "current state" label. Apply the same current-state discipline to narrative state:

- **`## Overall Read`** — keep the **single most recent** read. Rewrite it each material refresh; do not stack prior dated reads above or below it. The prior read's content is already preserved in that run's `journal/sync-log/` entry and in the 1:1 / meeting notes it came from.
- **`## People Observations`** — under each person, keep the **current read plus the most recent 2 dated entries**. When a third older entry would push the count past that, **migrate the oldest entry into that person's `people/<person>.md` History section before removing it from org-health** (the person file is the system-of-record home for their longitudinal record — this is the single-home rule applied to people). Never silently delete a dated observation; it either stays in org-health (within the keep-window) or moves to the person file.
- **Bounded-growth migration is content-preserving, not lossy.** If you remove a dated block from org-health, the receipt's What Moved must show where it went (`people/Alex Chen.md` History) so the operator can confirm nothing was dropped.
- This is a good future candidate for a deterministic skill (count dated `#### YYYY-MM-DD` blocks per person section, keep last N, emit the rest for migration) — until that exists, apply it by hand each run.

## Sync run log (`journal/sync-log/`)

The per-run history of `/sync` lives in `journal/sync-log/`, **not** in the dashboard. This keeps `work/dashboard.md` a bounded current-state read instead of an ever-growing append log. Each run writes its history entry to a dated file, exactly like `/scan` and `/brief` write dated artifacts.

**Write target — one file per day:**
- Path: `journal/sync-log/MMDDYY-sync.md` (date-first naming, same convention as other journal artifacts).
- **First run of the day:** create the file with frontmatter (`type: sync-log`, `date: YYYY-MM-DD`) and an `# Sync Log — YYYY-MM-DD` H1, then add the run's entry as a `## YYYY-MM-DD — Sync (<descriptor>)` block.
- **Subsequent runs the same day:** append another `## YYYY-MM-DD — Sync (<descriptor>)` block to the *same* file. Do not create a second file for the day.

The content of each block is what used to go in the dashboard's `# History` section — the run's deltas, archival notes, cadence updates, primary-source read/skip record, etc. Same detail, same voice; only the location changed.

**Dashboard `# Recent Activity` pointer (maintained every run):**

After writing the sync-log entry, refresh the dashboard's `# Recent Activity` section so it lists **only the most recent ~5 runs**, newest first. Each line is a one-sentence summary plus a wikilink to that run's sync-log file:

```
- **YYYY-MM-DD** (Nth run) — <one-line summary of the run's headline moves>. → [[journal/sync-log/MMDDYY-sync]]
```

Drop the oldest line(s) so the list stays at ~5. Keep a trailing `_Older runs: see \`journal/sync-log/\`._` pointer. Never let `# Recent Activity` grow without bound, and never re-introduce a full `# History` section on the dashboard.

**Scope discipline still applies.** The sync-log entry describes what moved in the *work* (programs, risks, decisions, people) and carries when/where metadata (cadence stamps, primary-source read record). Cosmos-internal narration stays out of it, same as before — the only change is the file it lands in.

## Home state writes (conditional — only when domain:Home inbox notes exist)

When inbox notes tagged `domain: Home` are present, also update home persistent state. **Do not touch home state if no home-tagged inbox notes exist in this run.**

- **`home/dashboard.md`** — refresh Life Areas table, Active Goals, Active Intentions, and Cadence section. Recompute Cadence by scanning newest matching journal file per row. Update Last Updated.
- **`home/areas/<area>.md`** — update Current Read, What's Working, What Needs Attention, and append dated History entry for any area with material signal. Do not update areas with no relevant inbox signal.
- **`home/goals/<goal>.md`** — update trajectory + trend if inbox signal relates to a personal goal. Create new life-goal files for newly surfaced personal goals (use `reference/templates/entities/life-goal.md`). Move achieved/abandoned personal goals to `archive/goals/`.
- **`home/intentions/<intention>.md`** — create or update intention files when inbox notes describe personal commitments being tracked. Keep these lightweight — no heavy structure required.

**Home synthesis standard:** Home notes are the only source of home signal. There are no external primary sources. Synthesize only from what was written in inbox notes tagged `domain: Home` and existing `home/` persistent state. Do not infer personal life state from work notes or sources.

**Home tone:** Home persistent state is personal, not executive. Write for the operator as a person, not the operator the leader. No org-health framing, no "leadership visibility," no executive vocabulary. Direct, honest, and human.

## Inbox archival

**Eligibility is determined by the Step 1b tabulation, not by reading interpretation.** For each inbox note the tabulation marked archive-eligible (or `status: complete`), once it has been fully incorporated into persistent state:
- Set `status: archived` in frontmatter
- Move to `archive/inbox/`

Notes the tabulation marked **hold** stay in `inbox/` regardless of how operationally "done" they feel — the unchecked task with content is the operator's explicit signal that the note still has business. If your synthesis is convinced a held note is functionally done, the right move is to surface it in the receipt ("note X reads as functionally complete but has 1 open task — operator may want to check the box or set status: complete") and let the operator decide. Do not archive on inference.

## Outcome review (did the closure actually hold?)

cosmos tracks open→closed well and closed→outcome not at all: a decision gets made and pruned, a risk gets resolved and archived, and nothing ever checks whether the decision produced the result it was supposed to or the mitigation actually held. That's the difference between a tracker and an intelligence system that compounds. This step closes the loop.

**On every default-scope run:**

1. **Find pending outcomes.** Scan `archive/risks/*.md` and `archive/decisions/*.md` for files with an `## Outcome` section still marked `_Pending verification…_` whose check-back date is on or before today. (Files resolved before this discipline existed have no `## Outcome` section — skip them; this applies going forward.)
2. **Verify against current signal.** For each, look at what's happened since closure — inbox, recent journal, the relevant program file, primary sources — and judge whether the closure held. Write the verdict into the `## Outcome` section, replacing the pending stub:
   - `**Outcome (YYYY-MM-DD): Landed as intended.** <one line of evidence>`
   - `**Outcome (YYYY-MM-DD): Partial / with issues.** <what's off, and whether it needs attention>`
   - `**Outcome (YYYY-MM-DD): Reopened / backfired.** <what broke>` — and **take action**: re-open the risk (move it back to `work/risks/` with trend `Increasing`) or create a new decision/risk, and surface it prominently in the receipt and on the dashboard.
   - `**Outcome (YYYY-MM-DD): Still pending.** <why not yet verifiable>` — push the check-back date out and leave it pending.
3. **Feed patterns.** When outcomes start to rhyme (e.g. several verbally-made decisions reopen because they never landed in an artifact), that's a real organizational pattern — record it in `work/executive-patterns.md` (the work pattern, in work language; not the cosmos mechanism that noticed it).
4. **Surface on the dashboard.** Maintain a small `## Recent Outcomes` section listing the last ~5 verified outcomes (verdict + one line + `[[archive/…]]` link), newest first. This is the visible proof the loop closed. Drop entries older than ~30 days.

Keep the judgment honest: "Landed as intended" requires actual evidence of the intended result, not just "we haven't heard otherwise." Absence of complaints is `Still pending`, not success.

## Source registration

Two triggers, one behavior. For any **inbox note** or **`journal/meetings/` note** read this run where `save-source: true` and `source:` holds a non-empty URL:

1. If a Primary Source entry with that exact URL already exists in `.cosmos/instructions/primary-sources.md`, skip. The URL dedup keeps re-runs idempotent, so a still-checked box never produces a duplicate.
2. Otherwise append a stub:

```
## <name>

<url from source: field>

Reading:
  start: <fill in>
  depth: <fill in>

Use for: <fill in>
```

Name it from the `meeting:` field, else the filename, else `New Source — <domain>`. **Do not guess** the description or `Reading:` values — leave `<fill in>` for the operator.

3. Add one receipt line: `New primary source registered: <name> — set Reading: and Use for:`.

`save-source` does not affect archival eligibility, and is left as-is after registration.

**Do not scan `work/meetings/` entities or `reference/templates/`** for registration. Those are definition files and never carry a source to promote.

## Canonical entity index

If this run created, archived, or renamed any entity file in `work/`, `people/`, `people/teams/`, `reference/systems/`, `reference/domains/`, or `work/meetings/`, regenerate the canonical entity index with the bundled `canonical-entity-index` skill — do not rebuild it by hand (hand-rebuilding drifts: it misses on-disk entities, drops `CLAUDE.md`-frontmatter-only ones, and scrambles People ordering):

```bash
python3 .claude/skills/canonical-entity-index/rebuild_index.py --write
```

The script implements the algorithm in `.cosmos/instructions/canonical-entity-index-rebuild.md` (filesystem + `CLAUDE.md` frontmatter, operator/chain-first People ordering, alphabetical elsewhere, idempotent). Run with `--diff` first to preview the change. **Skip entirely if no entity files were created, archived, or renamed this run** (do not regenerate on content-only edits).

## Artifact lint (QA — recommended)

After writing persistent state, QA the files you created or edited this run with the bundled `cosmos-artifact-linter` skill:

```bash
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py <files written this run>
```

Fix any `ERROR` before finishing (broken wikilinks, bare vault paths in code spans, unquoted frontmatter wikilinks). Treat `WARN`s — especially `scope-narration` — as review prompts, not auto-fixes: a cadence row with `/sync`, a "via /sync" stamp, or a wikilink to a `journal/` folder is legitimate metadata, not narration. Lint only the files this run touched (a full-vault sweep is for on-demand cleanup, not every sync).

## Scope discipline (work vs. cosmos)

Apply the Scope rule in `CLAUDE.md`. Everything `/sync` writes to `work/`, `people/`, `home/`, and `journal/` describes your organization's work, not cosmos.

The one case worth naming here: **receipt-style claims about `/sync`'s own behavior** (it re-read X, it misread Y, the tabulation caught Z) go in the chat receipt and never into persistent state.

---

## Attribution discipline

Apply `.cosmos/instructions/attribution-discipline.md` to every ownership, decision, and action-item call. Do not manufacture ownership by the operator's team for cross-team items that surface in a forum the operator merely attends; do not hedge on forums the operator's team owns. When synthesizing from a meeting's notes or a meeting-associated source, consult the meeting entity's `## My Role / Attendance Posture` first.

## Trend discipline

Apply the trend taxonomy in `.cosmos/instructions/trend-taxonomy.md`. Do not mark `Increasing` unless signal materially worsened. Do not mark `Resolved` without evidence of closure. Do not mark `New` if the entity already exists in persistent state.

## Output

`/sync` produces two outputs:

**First:** The Pre-Flight Source Declaration block (see above). This is always first. No exceptions.

**Second:** After synthesis and all file writes are complete, print the sync receipt to chat. The receipt has two parts: a roll-up of counts and signals (as before), then a **What Moved** block that lists the actual deltas this run produced. The What Moved block is mandatory on every run — it is the operator's verification layer.

```
Synced — YYYY-MM-DD HH:MM
Scope: <scope from pre-flight>  |  Force primary sources: <true|false>

Sources read: <count inbox> inbox notes, <count journal> journal files, <count primary> primary sources, <count persistent> persistent state files

Inbox processed: <count> (<count> archived, <count> kept active)
Risks: <new>, <updated>, <resolved>
Decisions: <new>, <updated>, <superseded>
Programs touched: <list>
People touched: <list>
Patterns: <any new pattern noted>

Home state: <"updated" if home notes processed, "not touched" if no domain:Home notes this run>
  Areas updated: <list, or "none">
  Goals updated: <list, or "none">

Notable signals:
- <one-line bullet per material change>

Decisions needing your attention:
- <if any surfaced this run>

---

## What Moved (delta from prior /sync at <YYYY-MM-DD HH:MM, or "—" if first run>)

### Trend changes
- <entity> — <old> → <new>; <one-clause reason>

### New entities created
- <path> — <one line>

### Entities archived / moved
- <path> → <archive path> — <one-clause reason>

### Persistent files updated
- <path> — <what materially moved>

### Outcomes verified (closed-loop check)
- <entity> — <Landed / Partial / Reopened / Still pending>; <one line>

### State freshness (always-live files not refreshed this run)
- <file> — not refreshed; <why>; as-of remains YYYY-MM-DD

### Inbox activity
- archived: <count> — <names>
- kept active: <count> — <why, if non-obvious>

### Out-of-scope (scoped runs only)
- <what was not touched because of scope>
```

**Omit any subsection with nothing to report.** Do not emit "none", "none due", or "no trend changes" — a heading with a null under it is scaffolding, not signal. A quiet run produces a short receipt, and that is correct.

Two exceptions worth stating even when quiet:

- A **Reopened / backfired** outcome always appears under Outcomes, even when it is also a trend change. A closure that did not hold is top-signal.
- An always-live file **not** refreshed on a default-scope run always appears under State freshness, so "not touched" is a visible call rather than a silent gap.

**Discipline for What Moved:**

- Every bullet must be tied to an actual write that happened this run. Do not list "considered" or "would-have" changes.
- "Updated" means a material edit — content moved, trend shifted, history appended with new signal. A pure frontmatter `last-updated:` bump is not material on its own; only mention it if there were no other edits to the file.
- If a file was read but not changed, do not list it.
- If a file was changed for hygiene only (e.g. stale section pruned but no new signal), say so explicitly so the operator can spot churn-without-signal.
- Trend changes go in their own section even if the file is also listed under "Persistent files updated" — trend movement is the highest-signal delta and should not be buried.
- This block IS the verification layer. If the operator reads the dashboard after a sync and the dashboard doesn't reflect what's claimed here, that's a synthesis bug worth catching immediately.
- **A "no material moves" report is itself a claim that must be verified.** Before emitting it, you must have actually re-read every journal file modified since the prior sync. If you skipped any modified file because of session memory or a harness "unchanged" signal, the claim is unverified — and almost always wrong, because live-meeting writeback is the most common source of post-prep journal modifications.

Keep the rest of the receipt tight. The dashboard is the persistent read; the chat report is the receipt + the verification delta.

## Cadence

`/sync` is daily, run 2-3× per day. The dashboard tracks its last run.

### Cadence row → file pattern mapping

When refreshing `work/dashboard.md`'s Cadence section, use this explicit mapping. For each row, find the newest file matching the pattern, parse the date from the MMDDYY prefix in the filename, and set that as `Last Run`. **You set `Last Run`; the `Status` column is then recomputed deterministically by the `cadence-status` skill — do not hand-compute it** (see "Recompute Status" below).

| Cadence row | Glob pattern | Date source |
|---|---|---|
| `/sync` | n/a — use the timestamp of this sync run | today |
| `/scan risks` | `journal/scans/risks/*-scan-risks.md` | MMDDYY prefix in filename |
| `/scan team` | `journal/scans/team/*-scan-team.md` | MMDDYY prefix in filename |
| `/scan patterns` | `journal/scans/patterns/*-scan-patterns.md` | MMDDYY prefix in filename |
| `/scan retro` | `journal/scans/retro/*-scan-retro.md` | MMDDYY prefix in filename |
| `/prep reflect` | `journal/personal/weekly-reflection/*-reflect.md` | MMDDYY prefix in filename |
| `/prep goal-plan` | `journal/personal/goal-plan/*-goal-plan.md` | MMDDYY prefix in filename |

**Home cadence rows** (in `home/dashboard.md` only — do not add these to `work/dashboard.md`):

| Cadence row | Glob pattern | Date source |
|---|---|---|
| `/prep life-reflect` | `journal/personal/life-reflect/*-life-reflect.md` | MMDDYY prefix in filename |
| `/prep life-goals` | `journal/personal/life-goals/*-life-goals.md` | MMDDYY prefix in filename |
| `/scan life-patterns` | `journal/scans/life-patterns/*-scan-life-patterns.md` | MMDDYY prefix in filename |

If a pattern matches zero files, set `Last Run = —` (the skill will set `Status = —`).

### Recompute Status (deterministic — MANDATORY)

After all `Last Run` values are updated, recompute the `Status` column with the bundled `cadence-status` skill — never by hand (the `overdue Nd` count and the interval mapping are exactly what hand-computation gets wrong):

```bash
python3 .claude/skills/cadence-status/compute_cadence.py --write work/dashboard.md home/dashboard.md
```

The skill rewrites every `Status` cell. The rule lives in the skill. A `?` result is a finding — the `Expected` string is not one the mapping recognizes, so fix the wording. Run without `--write` to preview.

If a cadence row exists in the dashboard table but is not in the mapping above, leave it alone — do not delete it, but flag it in the sync receipt as an untracked row so the operator can clean it up. Conversely, if a row in the mapping is missing from the dashboard's table, add it.

`/scan program <name>` is event-driven (per `CLAUDE.md`) and must not appear in the Cadence section. If it's currently in the dashboard's Cadence table from an older sync, remove it.
