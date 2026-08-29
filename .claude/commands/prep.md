# /prep

Prepare for something coming up — a 1:1, a recurring meeting, weekly reflection, or next-cycle planning.

## Modes

```
/prep <person>          1:1 with that person
/prep <meeting>         named recurring meeting (e.g. weekly-product, weekly-pmo)
/prep calibration <person>   PM leveling assessment vs. the TPM career ladder
/prep reflect           weekly professional reflection (CoS voice, work-focused)
/prep goal-plan         next-cycle work goal proposal
/prep day today         orient for today — calendar + cosmos context for the day ahead
/prep day tomorrow      plan for tomorrow — calendar + cosmos context, prep checklist
/prep life-reflect      weekly personal life reflection (home-focused, honest personal audit)
/prep life-goals        personal goal planning across life areas (semi-annual)
```

`<person>` is matched against `people/*.md` filenames.
`<meeting>` is matched against `reference/templates/prep-<meeting>.md`. If no specific template exists, fall back to `prep-meeting.md`.
`calibration <person>` — the first token `calibration` selects the mode; the remainder is the person, matched against `people/*.md` (e.g. `/prep calibration alex`). This produces a leveling assessment, not a 1:1.

---

## Output contract

Prep artifacts obey `.cosmos/instructions/output-contract.md`. **Caps: 1:1 prep 400 words, meeting prep 400, reflect 500, life-reflect 500, day plan 400, calibration 600.**

Three rules matter most here, because prep is where they were violated worst:

- **One capture section.** A prep artifact ends with `## Notes` and nothing else. Do not emit separate empty `## Decisions Made`, `## Action Items`, `## Follow-Ups`, or `## Linked Artifacts` scaffolds.
- **State each ask once.** Do not restate the same ask in a summary, a framing section, a body section, a checklist, and a questions list. Name it once, at the altitude that helps the operator act, and embed the canonical `## Line` from its entity file elsewhere.
- **Empty sections are correct.** If there are no decisions awaiting this person's input, say so in one line or omit the section. Never invent content to fill a template.

**Before writing, self-check:** take the two or three biggest items in the artifact. Each must be stated in full exactly once. If the same three-clause description appears in three sections, collapse two to pointers.

---

## Core Principle: Read Sources, Not Aggregates

**The dashboard is an aggregate, not a source.** It reflects persistent files as of the last `/sync`. If `/sync` has not run since the latest 1:1 notes, inbox drops, or journal entries were written, the dashboard is stale, and a prep built from it carries that staleness forward.

**`work/dashboard.md` is read last, if at all, and only for cadence and history.** It is never the source of truth for risks, decisions, program status, or people observations. Those always come from their own files. This holds for every mode below and is not repeated per mode.

**Recency rule:** a journal or inbox note dated more recently than a persistent state file wins. Do not let a stale `work/risks/foo.md` override a same-day 1:1 note that changes the risk. the operator's own words, written today, are authoritative.

### Base read set

Every work-domain mode reads these, in order:

1. `inbox/*.md` — active notes relevant to the target; highest precedence on conflict
2. `journal/meetings/` — recent 1:1s and meeting notes in scope
3. `work/risks/`, `work/programs/`, `work/decisions/` — entities linked to the target
4. `work/org-health.md`, `work/ownership-map.md` — team and org context

Each mode below states only what it **adds to** or **replaces** in that set.

---

## Pre-Flight: Source Declaration (MANDATORY — FIRST OUTPUT)

Every `/prep` mode must print a source declaration block as its first output before generating the artifact. This is the same discipline as `/sync` — it makes the read scope visible and auditable before synthesis happens.

Get the listing from the bundled script rather than hand-writing shell commands:

```bash
python3 .claude/skills/cosmos-scheduler/list_sources.py
```

Then narrow its output to this prep's scope. **Do not improvise `find`/`ls` pipelines.** A command containing shell expansion can only ever be granted "allow once", so an unattended run stalls on it every time.

```
## /prep <mode> Pre-Flight — Source Declaration
**Date:** YYYY-MM-DD

### Inbox
[x] `inbox/<file>` — <one line>

### Journal (last 14 days, in scope)
[x] `journal/meetings/1on1s/<person>/<file>` — <person, date>
[x] `journal/<other in-scope artifact>` — <type, date>

### Persistent State
[x] `work/risks/<file>` · `work/programs/<file>` · `work/decisions/<file>` · `people/<file>`
[x] `work/org-health.md` · `work/ownership-map.md`

### Gaps
[ ] <source> — <why not read>

### Sync Freshness
**Last /sync:** <date>
**In-scope notes newer than last sync:** <none | list>
**Verdict:** <✓ Current | ◑ Reading N unsynced directly | ⚠ Recommend /sync first>
```

Omit any section with nothing in it. Then state in one line that pre-flight is complete, and generate the artifact.

---

## Sync Freshness check (part of the pre-flight)

Answers "should I `/sync` before this prep?" with a signal-based verdict rather than a time-based guess.

**Why signal-based.** `/prep` reads sources directly, and the recency rule already means a newer journal note beats persistent state. A stale `/sync` therefore rarely degrades the prep. The real question is whether unincorporated signal exists *in this prep's scope*.

Run the `sync-freshness` skill with the in-scope file set the pre-flight already surfaced:

```bash
python3 .claude/skills/sync-freshness/check_freshness.py <in-scope files/globs ...>
```

Scope by mode: `<person>` and `calibration <person>` — their 1:1s, notes mentioning them, their owned entities. `<meeting>` — attendee notes plus the meeting's programs and risks. `reflect` and `goal-plan` — the whole portfolio.

**The three-state verdict is defined in the skill.** The script gives the facts; the ◑-versus-⚠ materiality call is yours.

**Recommend, never auto-run.** `/prep` stays read-only on persistent state. Do not trigger `/sync` from inside `/prep`.

---

## Inputs by Mode

### `/prep <person>`

**Adds to the base read set:**

- `journal/meetings/1on1s/<person>/` — last 3 files, most recent first
- `people/<person>.md` — the current people file
- Scope base items 3–4 to this person: risks and programs they own or are named in, decisions they decide or are mentioned in, their People Observations entry in org-health, their portfolio in the ownership map

Produce: context, open threads, topics worth raising, decisions awaiting their input. **400 words.** When a journal note and a persistent file conflict, the more recent journal note wins.

---

### `/prep calibration <person>`

A manager's evidence-based leveling assessment against the TPM career ladder — **not** a 1:1 prep and **not** upward output. For-your-eyes, blunt, analytical, like a `/scan` but person-focused. The argument after `calibration` is the person, matched against `people/*.md`.

**Read — in this order:**

1. `reference/org/pm-career-ladder.md` — the rubric. Every rating is *against this*. Resolve the person's **current level** from their `people/<person>.md` role/title and rate against *that level's* expectations (not the level above).
2. `reference/org/pm-calibration-template.md` — the structure to fill. Copy its sections verbatim; do not improvise the shape.
3. `people/<person>.md` — role, level, ownership areas, and the Leadership Notes arc.
4. `journal/meetings/1on1s/<person>/` — **all** files, full history, most recent first. Calibration is longitudinal — read the whole arc, not just the last 3. The trajectory and "change since last calibration" reads depend on it.
5. `journal/meetings/*` — other meetings this person led or materially shaped (evidence for Autonomy / Influence / People Impact).
6. `work/org-health.md` — People Observations, and any bottleneck / delegation / growth-lever signal on this person.
7. `work/ownership-map.md` — what they own (primary Scope-axis evidence).
8. `work/risks/*.md`, `work/programs/*.md`, `work/decisions/*.md` — what they own, decide, and carry (Autonomy, Influence, Technical Depth evidence).
9. `journal/personal/weekly-reflection/*` — the operator's own recorded observations about this person.
10. `journal/calibrations/*<person>*` — any prior calibration, for the change-since-last-calibration delta.

**Evidence discipline — mandatory.** Every five-axis and competency-cluster rating must cite specific evidence (a 1:1, a decision they owned, an artifact they produced, an org-health observation). If the record doesn't support a defensible rating, mark **Insufficient Evidence** — that is a valid finding (a calibration *data* gap to close), never a cell to guess. Apply the template's pattern check: 3+ axes *Above* → investigate promotion readiness; 3+ *Below* → calibration concern, find root cause; **2+ Insufficient Evidence → the calibration is not done** — say so explicitly and name what to close (1:1 history, peer input, direct observation).

Produce: a filled calibration artifact copying the template — five-axis assessment, competency clusters, trajectory, promotion readiness, development plan, recommendation — with every rating evidence-cited. It is a working draft; note at the top whether it is a **dry-run** (template/signal test) or a **calibration of record**, defaulting to a working draft the operator finalizes. This is an internal management artifact — the cosmos-vs-work scope rule still applies (no command/tool narration in the artifact).

---

### `/prep <meeting>`

**Read — in this order:**

1. `inbox/*.md` — active notes tagged with relevant programs or attendees
2. `journal/meetings/<meeting-type>/` — most recent entry matching this meeting
3. `journal/meetings/1on1s/<person>/` — recent notes for attendees (per-person subfolders), if relevant
4. `reference/templates/prep-<meeting>.md` (specific) or `prep-meeting.md` (generic)
5. `work/programs/*.md` — programs relevant to this meeting's attendees/topic
6. `work/risks/*.md` — risks relevant to this meeting
7. `work/decisions/*.md` — decisions pending for this meeting's attendees
8. **Configured Primary Sources** — scan `.cosmos/instructions/primary-sources.md` for any source whose name contains keywords from the meeting argument (e.g. `/prep weekly cms` matches "Weekly CMS Product Sync"). If a match is found, pull from it using the appropriate tool per the Source Access Protocol. If multiple sources match, pull all of them. If no match is found, skip silently.

**Apply attribution discipline.** Read the resolved meeting entity's `## My Role / Attendance Posture` block (the same entity used for folder resolution) and apply `.cosmos/instructions/attribution-discipline.md` to all ownership, decision, and action-item attribution in the artifact. Do not manufacture ownership by the operator's team for cross-team items that merely appear on the agenda; do not hedge on forums the operator's team owns. If the entity has no posture block, apply the core principle in that file.

Produce: agenda, decisions needed, risks to surface, action carryover. **400 words.**

---

### `/prep reflect`

**Read — in this order:**

1. `inbox/*.md` — all active notes
2. `journal/meetings/1on1s/` — all 1:1 files from the last 14 days across all person subfolders, every one
3. `journal/meetings/` — all other meeting files from the last 14 days
4. `journal/scans/` — most recent file per subdirectory
5. `journal/briefs/` — most recent file
6. `journal/personal/weekly-reflection/` — last 2 reflection files (for longitudinal continuity)
7. `work/org-health.md` — people observations and recurring patterns
8. `work/ownership-map.md` — current ownership state
9. `work/risks/*.md` — all active risk files (read each one, not a summary)
10. `work/programs/*.md` — all program files

Read `work/dashboard.md` for the Cadence section only, to note what is overdue.

**Voice and intent:** `/prep reflect` is a Chief of Staff assessment written *to* the operator, *about* the operator. Not a personal journal prompt, not a summary of what happened, and not a postmortem on cosmos. It is a direct, evidence-based analysis of how the operator worked this week — where he was effective, where he fell short, what patterns are recurring, what he should do differently, and what uncomfortable truth he needs to hear.

The CoS role means:
- **Write in second person.** "You did X." "The pattern here is Y." "This is the third time Z has slipped."
- **Be specific and evidence-based.** Every observation ties to something that actually happened — a decision made, a commitment kept or broken, a conversation avoided, a structural fix built. No generalizations.
- **Do not soften things that need to be said.** The CoS's value is in saying what a peer won't. Name the avoidance. Name the time misallocation. Name what's genuinely improving with equal specificity.
- **Do not narrate cosmos's own failures in the reflection.** If cosmos produced inaccurate output this week, note it only to the extent it affected the operator's ability to operate — one sentence, no more. This document is about the operator's professional development, not a tool postmortem.
- **Build longitudinally.** The Progress Markers section is the running arc — what's genuinely improving over multiple weeks, what keeps recurring despite the operator's awareness of it. This is where the reflection becomes more valuable over time.

**The reflection is only as honest as its sources.** If a 1:1 note from today says something different from a risk file that hasn't been synced yet, the 1:1 note is the truth. Surface the conflict briefly if relevant — don't silently choose the stale version.

Produce: a CoS assessment in **500 words**. It should read like a direct conversation with a trusted advisor who has done their homework.

Write only the sections with something real to say. A quiet week produces a short reflection, and that is an honest result — not a failure to fill the template.

---

### `/prep goal-plan`

**Read — in this order:**

1. `inbox/*.md` — active notes
2. `journal/meetings/1on1s/` — recent 1:1s (last 14 days) across all person subfolders
3. `journal/personal/weekly-reflection/` — last 2 reflection files
4. `journal/scans/` — most recent retro scan if available
5. `work/goals/*.md` — all current goal files
6. `work/programs/*.md` — program status for goal context
7. `work/executive-patterns.md` — longitudinal patterns relevant to goal-setting
8. `work/org-health.md` — team health as a goal input

Produce: carryover analysis, retiring goals, proposed new goals, dependency notes.

---

### `/prep life-reflect`

Weekly personal life reflection. Home-focused. Entirely different voice and purpose from `/prep reflect` — this is not a professional assessment, it is a personal audit of how you're living.

**Read — in this order:**

1. `inbox/*.md` — active notes tagged `domain: Home` or listed under `domains: [Home]`
2. `home/dashboard.md` — current life area state and cadence
3. `home/areas/*.md` — all life area files
4. `home/goals/*.md` — all active personal goals
5. `home/intentions/*.md` — all active intentions
6. `journal/personal/life-reflect/` — last 2 life-reflect files (for longitudinal continuity; if none exist, proceed without them)

**Do not read:** `work/` files, `people/` files, `work/dashboard.md`, meeting notes, briefs, or scan files. This reflection is exclusively about the personal life domain.

**Voice and intent:** `/prep life-reflect` is written as an honest, trusted-friend voice — direct and specific, but warmer than the CoS professional voice used in `/prep reflect`. It is about the life the operator is living outside of work: relationships, health, creativity, rest, personal growth. Not productivity. Not performance.

- Write in second person ("you"). "You showed up for X." "You've been avoiding Y for three weeks now."
- Be specific. Every observation should be tied to something observable — a pattern, a habit, a gap between stated values and actual time allocation.
- Do not soften things that need saying. Name the avoidance, the drift, the thing left undone.
- Do not frame this in professional terms. "Leadership trajectory" and "org signal" are not relevant here. This is about the person, not the professional.
- Build longitudinally. The Progress Markers section should get richer over time. If this is the first run, note that the longitudinal arc is just beginning.

**If home state is sparse (first run or few prior reflects):** generate the artifact with honest placeholder reads based on whatever home inbox notes exist. Seed the life area sections as best you can. Note in the chat reply that the reflection will get sharper as home signal accumulates.

Produce: a life-reflect artifact in **500 words**. Write only the sections with something real to say.

---

### `/prep life-goals`

Personal goal planning across all life areas. Semi-annual cadence. Produces a structured goal proposal for the operator's personal life — not their work goals.

**Read — in this order:**

1. `inbox/*.md` — active notes tagged `domain: Home`
2. `home/dashboard.md` — current life area state
3. `home/areas/*.md` — all life area files for current-state context
4. `home/goals/*.md` — all current personal goals (active and recently archived)
5. `journal/personal/life-reflect/` — last 3 life-reflect files (for honest baseline)
6. `journal/personal/life-goals/` — most recent prior life-goals artifact (for carry-over analysis)
7. `journal/scans/life-patterns/` — most recent life-patterns scan, if any

**Do not read:** work state files. This is exclusively about personal life goals.

**Voice and intent:** Forward-looking, personal. The goal is to help the operator be deliberate about what he's building in their life, not just what he's building at work. Frame goals around outcomes and quality of life, not outputs or metrics. Be willing to name the goal that's conspicuously missing from the list.

Produce: a `prep-life-goals.md` artifact with carryover analysis, retiring goals, proposed goals by life area, capacity reality check.

---

### `/prep day <today|tomorrow>`

**Target date:** resolve `today` to the current date, `tomorrow` to current date + 1 day.

Read:
- **Google Calendar MCP** — fetch all events for the target date. Do not use WebFetch.
- `people/*.md` — for every attendee who has a cosmos entity
- `work/risks/*.md` and `work/decisions/*.md` — linked to those attendees or their programs
- `work/programs/*.md` — linked to those attendees
- Recent `journal/meetings/` entries for these meetings or attendees (last 7 days)
- Active `inbox/*.md` tagged with any attendee or linked program
- Existing day artifact at the target path — if present, refresh in place

**Calendar event classification:**

| Classification | Handling |
|---|---|
| Accepted / organized by you | Primary — include with full context block |
| Tentative / no response | List separately under "Needs Response" — flag as unactioned |
| Declined | Omit |
| All-day events | Include in a separate "All-Day / Blocks" section at the top |

**Per-meeting context block** (for each accepted or organized event):
- Time, title, attendees
- Cosmos context for attendees with `people/` entities: role, ownership areas, active risks
- Active risks or decisions linked to programs those attendees own or are involved in
- Whether a prep artifact already exists in `journal/meetings/` for this meeting today — link it if yes, surface the `/prep` command if no
- Open inbox notes tagged with any attendee or linked program

**Cross-day synthesis** (after all meeting blocks):
- Programs or risks that surface across multiple meetings — note count and why it matters
- Decisions that could be progressed today given who you're seeing
- People appearing in multiple meetings — flag patterns worth noting

**Prep checklist** (at the end):
A clean list of `/prep` commands for meetings with no artifact yet. One line per meeting.

**Tone:**
- `today` — orientation mode: check what prep already exists, surface what's coming soon, lighter on planning
- `tomorrow` — planning mode: heavier synthesis, forward-looking, emphasizes what to prepare and what decisions to walk in ready to make

---

## Output file paths

```
/prep <person>        → journal/meetings/1on1s/<person>/MMDDYY-<person>-1on1.md
/prep <meeting>       → journal/meetings/<meeting>/MMDDYY-<meeting>.md
/prep calibration <person> → journal/calibrations/MMDDYY-<person>-calibration.md
/prep reflect         → journal/personal/weekly-reflection/MMDDYY-reflect.md
/prep goal-plan       → journal/personal/goal-plan/MMDDYY-goal-plan.md
/prep day today       → journal/personal/daily/MMDDYY-day.md  (MMDDYY = today's date)
/prep day tomorrow    → journal/personal/daily/MMDDYY-day.md  (MMDDYY = tomorrow's date)
/prep life-reflect    → journal/personal/life-reflect/MMDDYY-life-reflect.md
/prep life-goals      → journal/personal/life-goals/MMDDYY-life-goals.md
```

**Folder creation:** If the output subfolder does not yet exist, create it before writing the file. This applies to `weekly-reflection/`, `goal-plan/`, `calibrations/`, and any `journal/meetings/<meeting>/` folder derived for a new recurring meeting.

**Meeting folder resolution — mandatory before writing.** Meeting names can be ambiguous (e.g. "cms product weekly" and "content systems weekly" sound similar but are different meetings with different audiences, owners, and journal folders). Before deriving the subfolder from the meeting argument, check `work/meetings/` for an entity file whose `meeting`, `aliases`, or filename matches the argument. If a match is found with a `journal_path` field, use that path as the output folder — do not derive it from the argument alone. If no match is found, derive the folder name from the argument in kebab-case as a fallback.

If a file for today already exists at the target path, refresh it in place — do not create a duplicate.

---

## After prep

The artifact opens in Obsidian. The user adds their own topics, runs the meeting or reflection, writes notes inline. The file is *both* the prep and the eventual notes — same file, lived in throughout the day.

When the user later runs `/sync`, signal from those notes propagates to persistent state. If new signal surfaced during prep that should be in persistent state (a risk, a decision, a changed ownership), flag it in the chat reply so the user can decide whether to run `/sync` immediately.

**QA the artifact before finishing** by linting the file you just wrote with the bundled `cosmos-artifact-linter` skill — fix any `ERROR` (broken wikilinks, bare vault paths, unquoted frontmatter wikilinks):

```bash
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py <the prep file you wrote>
```

---

## What not to do

- **Do not generate the artifact before completing the pre-flight.**
- **Do not resolve a journal-vs-persistent-file conflict by choosing the persistent file.** The more recent journal note is the truth. Surface the conflict rather than silently picking one.
- **Do not synthesize from memory of files read earlier in the session.** Re-read at generation time. The context window is not a substitute for the current file on disk.
- **Do not manufacture ownership for the operator's team** on items that merely appear in a meeting the operator attends. Per `.cosmos/instructions/attribution-discipline.md`, require a directly-named system, person, or deliverable — and conversely, do not hedge on forums their team owns.
- **Do not write the reflection in first person.** It is a CoS assessment written to the operator: "Where You Were Strong", not "What I Did Well".
- **Do not pad to fill a template.** An empty section is a finding. Inventing content to fill it destroys the signal.
- **Respect the Scope rule in `CLAUDE.md`.** Prep artifacts describe the work, never cosmos's own machinery.
