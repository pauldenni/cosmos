---
name: canonical-entity-index
description: Regenerate .cosmos/instructions/canonical-entity-index.md deterministically from the filesystem + CLAUDE.md frontmatter. Use as the final step of a /sync run that created, archived, or renamed any persistent entity (work/risks, work/programs, work/decisions, work/goals, people, people/teams, reference/systems, reference/domains, work/meetings). Replaces hand-rebuilding the index, which drifts (misses on-disk entities, drops frontmatter-only ones, scrambles People ordering).
---

# Canonical Entity Index Rebuild

## What this is

A bundled script that regenerates the canonical entity index from scratch — the index is a *derived view*, not a hand-maintained file, and rebuilding it by reading/typing drifts (entities on disk get missed, CLAUDE.md-frontmatter-only entities get dropped, the People ordering wanders). This implements the algorithm in `.cosmos/instructions/canonical-entity-index-rebuild.md` exactly and idempotently.

## When to use it

Run it as the **final step of a `/sync` run** when that run **created, archived, or renamed** a persistent entity file. Do **not** run it when `/sync` only edited the contents of an existing entity (no name change, no folder move).

## How to run it

```bash
# Preview the regenerated index (dry run, prints to stdout)
python3 .claude/skills/canonical-entity-index/rebuild_index.py

# See exactly what would change vs the current index
python3 .claude/skills/canonical-entity-index/rebuild_index.py --diff

# Overwrite .cosmos/instructions/canonical-entity-index.md
python3 .claude/skills/canonical-entity-index/rebuild_index.py --write
```

`--date YYYY-MM-DD` pins the "Last regenerated" line (used for reproducible tests; defaults to system date).

## What it does

- **Sections & sources** (active only — `archive/` is excluded):

  | Section | Disk source | Also merges from CLAUDE.md frontmatter |
  |---|---|---|
  | People | `people/*.md` (top-level) | `operator`, `svp`, `vp`, `director`, `manager`, `team_members` |
  | Programs | `work/programs/*.md` | `programs` |
  | Systems | `reference/systems/*.md` | `systems` |
  | Domains | `reference/domains/*.md` | `domains` |
  | Teams | `people/teams/*.md` | — |
  | Meetings | `work/meetings/*.md` | — |
  | Risks | `work/risks/*.md` | — |
  | Decisions | `work/decisions/*.md` | — |
  | Goals | `work/goals/*.md` | — |

- **People order:** operator first, then the leadership chain (`svp`, `vp`, `director`, `manager`, skipping any that are empty), then everyone else alphabetically (case-insensitive). All other sections are alphabetical (case-insensitive).
- **Dedupe** is case-insensitive; disk spelling wins. Frontmatter values are stripped of `[[ ]]` and quotes. An empty section renders `_(none yet)_`.
- **Idempotent:** running it twice produces the same file (only the date line tracks the day).

## Notes

- It includes names **as-is** even if they violate `canonical-naming.md` (e.g. a risk file in TitleCase) — surfacing the inconsistency in the index makes it visible. It does not silently rename. (Catching naming violations is the artifact-linter's job, not this one.)
- If `CLAUDE.md` frontmatter is missing or malformed, it falls back to filesystem-only and continues — it never blocks on a parse failure.
- It overwrites the index; it never appends.
