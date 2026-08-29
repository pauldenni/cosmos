# Output Contract

Every cosmos artifact obeys this file. Commands and templates link here. They do not restate these rules.

The `cosmos-artifact-linter` skill enforces the deterministic parts. An ERROR blocks the write.

---

## 1. Word caps

Caps are hard. Count body words. Do not count frontmatter, tables of links, or embedded lines.

| Artifact | Path | Cap |
|---|---|---|
| Dashboard | `work/dashboard.md` | 600 |
| Org health | `work/org-health.md` | 600 |
| Ownership map | `work/ownership-map.md` | 500 |
| Executive patterns | `work/executive-patterns.md` | 400 |
| Program | `work/programs/*.md` | 500 |
| Risk | `work/risks/*.md` | 300 |
| Decision | `work/decisions/*.md` | 250 |
| Goal | `work/goals/*.md` | 250 |
| 1:1 prep | `journal/meetings/1on1s/**` | 400 |
| Meeting prep | `journal/meetings/**` | 400 |
| Brief — short | `journal/briefs/**short**` | 150 |
| Brief — vp | `journal/briefs/**vp**` | 300 |
| Brief — svp | `journal/briefs/**svp**` | 400 |
| Scan — any mode | `journal/scans/**` | 600 |
| Now | `journal/personal/daily/*-now.md` | 250 |
| Day plan | `journal/personal/daily/*-day.md` | 400 |
| Reflect | `journal/personal/weekly-reflection/*` | 500 |
| Life reflect | `journal/personal/life-reflect/*` | 500 |
| Sync log | `journal/sync-log/*.md` | 300 |
| Person | `people/*.md` | 300 |
| Home area | `home/areas/*.md` | 250 |
| Home dashboard | `home/dashboard.md` | 400 |

If the content does not fit, cut content. Do not compress by deleting spaces, stacking clauses, or dropping articles. A cap is a signal that the artifact is carrying facts that belong somewhere else.

**Caps are tunable, and one kind of file legitimately needs a higher one.** An artifact that is a pure *enumeration* — `work/ownership-map.md` is the clearest case — grows with the size of the org, not with wordiness. Capping it too tightly forces dropping the very assignments it exists to record. Raise the cap for those; never raise one just because prose ran long.

`## History` blocks are exempt from the body cap but bounded separately (§6).

---

## 2. Sentences

- One idea per sentence.
- **Maximum 25 words per sentence.** This is an ERROR, not a guideline.
- Active voice. Subject first. Present tense for current state, past tense for events.
- One term per concept. If a system is called Search, it is called Search every time. Do not vary wording for style.
- No sentence may contain more than one semicolon or more than two commas.

---

## 3. Banned constructions

**Hedges.** Do not use: `may want to consider`, `it might be worth`, `perhaps`, `potentially`, `it could be argued`, `arguably`, `seems to suggest`, `appears to indicate`.

State the finding, or state that the signal is weak and label it `Confidence: Low`.

**Filler openers.** Do not use: `It is important to note that`, `It's worth noting`, `As mentioned above`, `At the end of the day`, `In terms of`.

**Narration.** Do not name cosmos or its commands in synthesis prose. See the Scope rule in `CLAUDE.md`.

**Trend prose.** The 5-state enum is the only vocabulary for trend: `New`, `Increasing`, `Stable`, `Decreasing`, `Resolved`. Render it as a token in a table cell or a `trend:` field. Never expand it into a phrase like "dependency concentration increasing" or "delivery confidence weakening".

**Confidence prose.** Render as the bare label `High`, `Medium`, or `Low`. Never write the definition.

---

## 4. Empty sections

An empty section is correct output. It is evidence that nothing happened.

- If a section has no content, write one short line saying so, or omit the section.
- Never invent content to fill a section.
- Never emit a placeholder: no bare `-`, no `TBD`, no `| | | |` table rows, no `_None._`.

Omission beats a placeholder. A reader scanning for signal should not have to skip past scaffolding.

---

## 5. Single home, one wording

Every fact has exactly one file where it is stated in full.

| Fact | System of record |
|---|---|
| Risk detail | `work/risks/<risk>.md` |
| Decision detail | `work/decisions/<decision>.md` |
| Program detail | `work/programs/<program>.md` |
| Who owns what | `work/ownership-map.md` |
| Org-health trend | `work/org-health.md` |
| Per-run history | `journal/sync-log/MMDDYY-sync.md` |

### The `## Line` mechanism

Every risk, decision, program, and goal file carries a `## Line` section: **one sentence, 25 words maximum**, that states the thing canonically.

```md
## Line
Search capacity headroom has no owner above CMS Product; it rolled back the Collections cutover and is unstarted on three entity migrations.
```

Every other artifact that needs this fact **embeds it** rather than restating it:

```md
![[work/risks/search-capacity-headroom#Line]]
```

Obsidian renders the embed inline. The fact has one wording, in one file, and updating it updates every artifact that carries it.

**This is the rule that fixes the repetition problem.** Measured before this contract: three asks in one 1:1 prep, each restated six to nine times in different words, at a cost of roughly 700 words for a 30-word ask.

### Altitude, not repetition

An item may legitimately *surface* in more than one place at different altitudes — an Executive Summary names it, a watchlist flags it. Surfacing is a pointer or an embed. It is never a second paragraph that re-derives the same fact in fresh words.

**Self-check before writing any artifact:** take the two or three biggest items. For each, confirm it is stated in full in exactly one place, and that every other appearance is an embed, a wikilink, or a single clause.

---

## 6. Bounded history

Files grow forever unless bounded. Measured before this contract: `work/programs/Atlas.md` was 88% dated changelog; `work/risks/collections-migration-slip.md` was 71% `## History`.

- A `## History` section keeps the **4 most recent dated entries**.
- Each entry is **one line of regular text**, never a heading: `- **YYYY-MM-DD** — <what changed, max 25 words>`. A heading wrapping a single sentence renders as a section title and makes the log look like structure rather than a log.
- When a 5th entry is added, the oldest moves to the matching file under `archive/`.
- Per-run detail belongs in `journal/sync-log/`, not in the entity file.

---

## 7. Capture sections

A prep artifact carries **one** capture section: `## Notes`.

Do not emit `## Decisions Made`, `## Action Items`, and `## Follow-Ups` as separate empty scaffolds. Measured before this contract: 68% of `## Decisions Made` sections and 33% of `## Notes` sections shipped empty, and 22 files carried a blank action-items table.

Decisions and actions recorded in `## Notes` are picked up by `/sync` and routed to their system of record.

---

## 8. Links

Render every vault reference as an Obsidian wikilink. Path-form preferred:

```md
[[work/risks/search-capacity-headroom]]
```

Never use a bare path in a code span. In frontmatter, quote the wikilink:

```yaml
related_risks:
  - "[[work/risks/search-capacity-headroom]]"
```

Do not add a trailing `## Linked Artifacts` section that re-lists links already present in frontmatter and body. That section is removed.

---

## 9. Precedence

If this file conflicts with a command file or a template, **this file wins**. Fix the other file.
