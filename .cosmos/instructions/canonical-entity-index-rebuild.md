# Canonical Entity Index Rebuild

`.cosmos/instructions/canonical-entity-index.md` is a derived view, not a hand-maintained file. It is regenerated from the filesystem (and `CLAUDE.md` for leadership-chain names that may not yet have notes on disk).

This file specifies the regeneration algorithm. **The algorithm is implemented by the bundled `canonical-entity-index` skill (`.claude/skills/canonical-entity-index/rebuild_index.py`) — run that script rather than hand-executing the steps below.** This document remains the authoritative spec the script implements. `/sync` MUST execute this rebuild as the final step of its run whenever it creates, archives, or renames a persistent entity. No other command writes the index — `/prep`, `/brief`, and `/scan` are read-only on persistent state.

---

# When to run

Run the rebuild at the end of a `/sync` run when that run:
- created a new entity file (a new `work/risks/<name>.md`, `work/programs/<name>.md`, `work/decisions/<name>.md`, `work/goals/<name>.md`, `people/<name>.md`, `people/teams/<name>.md`, `reference/systems/<name>.md`, `reference/domains/<name>.md`, or `work/meetings/<name>.md`)
- archived an entity (move from active folder to `archive/`)
- renamed an entity

Do NOT run the rebuild when `/sync` only updates the contents of an existing entity file (no name change, no folder move).

---

# Algorithm

1. **Collect entity names from disk.** For each section, list `*.md` basenames (without extension) from the corresponding folder, excluding anything under `archive/`:

   | Section   | Source folder                          |
   |-----------|----------------------------------------|
   | People    | `people/*.md` (top-level only — exclude `people/teams/`) |
   | Programs  | `work/programs/*.md`                   |
   | Systems   | `reference/systems/*.md`               |
   | Domains   | `reference/domains/*.md`               |
   | Teams     | `people/teams/*.md`                    |
   | Meetings  | `work/meetings/*.md`                   |
   | Risks     | `work/risks/*.md`                      |
   | Decisions | `work/decisions/*.md`                  |
   | Goals     | `work/goals/*.md`                      |

2. **Merge in entities referenced in `CLAUDE.md` frontmatter** (these may not yet have notes on disk — the wizard seeds names there before any entity files exist):

   - People: values of `operator`, `svp`, `vp`, `director`, `manager`, and each item in `team_members`
   - Programs: each item in `programs`
   - Systems: each item in `systems`
   - Domains: each item in `domains`

   Strip surrounding `[[` / `]]` and quotes when reading frontmatter values.

3. **Dedupe** within each section (case-insensitive match on the canonical name).

4. **Sort** each section alphabetically (case-insensitive). Exception: keep `operator` first in the People section, then leadership chain (`svp`, `vp`, `director`, `manager`) before direct reports.

5. **Render** the file using the template below. Use exact section order. Each entry: `- [[Canonical Name]]`. If a section is empty, write `_(none yet)_` instead of an empty list.

6. **Write** to `.cosmos/instructions/canonical-entity-index.md`. Overwrite — do not append.

---

# Output Template

```md
# Canonical Entity Index

This file is the source of truth for entity names in your cosmos vault. It is regenerated automatically by cosmos commands — do not edit by hand. To add an entity, create the entity file (e.g. `work/programs/<name>.md`) or update `CLAUDE.md` frontmatter, and the next command run will pick it up.

Last regenerated: YYYY-MM-DD by /sync

---

# People

- [[Operator Name]]
- [[SVP]]
- [[VP]]
- [[Director]]
- [[Manager]]
- [[Direct Report 1]]
- [[Direct Report 2]]

---

# Programs

- [[Program Name]]

---

# Systems

- [[System Name]]

---

# Domains

- [[Domain Name]]

---

# Teams

- [[Team Name]]

---

# Meetings

- [[Meeting Name]]

---

# Risks

- [[risk-canonical-name]]

---

# Decisions

- [[decision-canonical-name]]

---

# Goals

- [[goal-canonical-name]]
```

---

# Notes

- The rebuild is idempotent. Running it twice in a row produces the same file.
- If the rebuild encounters an entity name that violates `canonical-naming.md` (e.g. a risk file in TitleCase), include it as-is — surfacing the inconsistency in the index makes it visible. Do not silently rename.
- If `CLAUDE.md` frontmatter is missing or malformed, fall back to filesystem-only and continue. Do not block on parse failures.
- Archive folders (`archive/risks/`, `archive/programs/`, `archive/inbox/`, etc.) are intentionally excluded — the index reflects active entities only.
