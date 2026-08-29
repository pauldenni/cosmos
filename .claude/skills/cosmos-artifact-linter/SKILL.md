---
name: cosmos-artifact-linter
description: Validate rendered cosmos artifacts against the vault's hard rules — word caps and sentence length from the output contract, no hedges or placeholder scaffolding, wikilink targets must resolve, frontmatter wikilinks must be quoted, and no cosmos-internal narration in work artifacts. Also flags facts restated across multiple sections. Use as a QA pass after /sync writes persistent state, after /prep or /brief writes an artifact, or on demand to sweep the whole vault. ERRORs are deterministic; WARNs need human judgment.
---

# Cosmos Artifact Linter

## What this is

A bundled script that checks rendered cosmos artifacts against the formatting and scope rules in `CLAUDE.md` — the rules a human can't reliably eyeball at scale. It separates **deterministic violations** (`ERROR`) from **judgment calls** (`WARN`).

## When to use it

- **QA after a write:** after `/sync` updates persistent state, or after `/prep`/`/brief` writes an artifact, lint the file(s) just written and fix any `ERROR` before finishing.
- **On-demand sweep:** run with no args to lint the whole artifact set (useful for clearing accumulated broken-wikilink debt).

## How to run it

```bash
# Lint the default artifact set (work/, people/, home/, journal/ minus sync-log)
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py

# Lint only specific files/dirs (e.g. what you just wrote)
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py work/risks/foo.md work/dashboard.md

# Errors only (suppress the judgment-call WARNs); JSON for machine use
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py --errors-only
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py --json work/
```

Exit code is `1` if any `ERROR` was found, else `0` (so it can gate a hook or CI).

## The checks

| Severity | Check | Rule |
|---|---|---|
| ERROR | `wikilink-resolves` | a path-form wikilink `[[work/risks/foo]]` must point at an existing file; a wikilink to a folder is malformed |
| WARN | `wikilink-basename` | a basename wikilink `[[Foo]]` resolves to no filename **or alias** in the vault — likely a broken link or a not-yet-created entity (review) |
| ERROR | `bare-path` | a specific vault `.md` path written in a `` `code span` `` instead of a wikilink (globs `*.md`, folders `inbox/`, URLs, and placeholder paths like `<name>`/`MMDDYY` are fine) |
| ERROR | `frontmatter-quote` | a `[[wikilink]]` in YAML frontmatter not wrapped in quotes |
| WARN | `scope-narration` | cosmos-internal narration in a work artifact (the word "cosmos", or a mechanism phrase like "pre-flight"/"tabulation") that isn't in an allowed metadata context — persistent state describes the work, not cosmos's machinery |

### Output-contract checks

These enforce `.cosmos/instructions/output-contract.md`.

| Severity | Check | Rule |
|---|---|---|
| ERROR | `word-cap` | artifact body exceeds the cap for its type (§1). Frontmatter, code fences, and `## History` are excluded from the count; wikilinks count as one word |
| ERROR | `sentence-length` | a sentence over 25 words (§2) |
| ERROR | `banned-phrase` | a hedge (`perhaps`, `may want to consider`) or filler opener (§3) |
| ERROR | `trend-prose` | trend written as a phrase (`delivery confidence weakening`) instead of the 5-state enum (§3) |
| ERROR | `placeholder` | bare `-` bullet, `TBD`, empty table row, or `_None._` — omit instead (§4) |
| ERROR | `linked-artifacts` | a trailing `## Linked Artifacts` section duplicating frontmatter links (§8) |
| WARN | `repeated-content` | two sentences in one file stating the same thing in different words (§5) |
| WARN | `repeated-fact` | a distinctive term carried through 5+ sections and 6+ lines — one fact retold at several altitudes (§5) |

`repeated-fact` is the detector for the dominant bloat mechanism. Repetition in this vault is *paraphrased*, not copy-pasted, so text-similarity misses it — but the distinctive terms recur even when the wording doesn't. Terms naming the artifact's own subject (the 1:1 counterpart, the program) are excluded, since those recur by definition.

`--stats` prints a word-count-vs-cap table for any path set, which is the fastest way to see what needs compacting.

## Scope of what it lints

- **Default targets:** rendered artifacts — `work/`, `people/`, `home/`, and `journal/` (excluding `journal/sync-log/`, which is run-history where cosmos narration is allowed).
- **Output-contract checks apply to live state and new writes only.** On a bare sweep they run on `work/`, `people/`, and `home/`. Dated journal artifacts are immutable records of what was true at the time, so a sweep leaves them alone — but naming one explicitly (as `/prep` and `/brief` do on the file they just wrote) opts it in. Linking and narration checks always run everywhere.
- **Excluded by default:** `.claude/`, `.cosmos/`, `CLAUDE.md` (infrastructure), `reference/templates/` (definitions), `inbox/` (raw capture — the operator writes freely there), and `archive/`. Pass explicit paths to lint any of them.
- Wikilink resolution and bare-path checks resolve against **all** vault files (including `archive/` and `reference/`), and basename links also resolve against entity `aliases:` frontmatter — so `[[Zach]]` (an alias of `[[Alex Chen]]`) is not flagged.

## Boundary

`ERROR`s are safe to treat as must-fix. `WARN`s — especially `scope-narration` — are review prompts, not verdicts: a cadence table row with `/sync`, a "via /sync" header stamp, or a wikilink to a `journal/scans/` folder are legitimate when/where metadata, not narration. The linter reports; the human decides on WARNs. It does not auto-fix.
