---
name: inbox-archive-tabulation
description: Deterministically decide which cosmos inbox notes are archive-eligible by counting checkbox state inside each note's `## Follow-Up Needed` section and reading its frontmatter `status`. Use during the /sync pre-flight (Step 1b), before any inbox note is archived, or whenever you need a trustworthy archive/hold verdict for inbox/*.md. Replaces reading-interpretation of checkboxes, which is error-prone and has caused incorrect archival decisions.
---

# Inbox Archive Tabulation

## What this is

A bundled script that computes archive-eligibility for cosmos inbox notes **deterministically**, instead of by reading interpretation. cosmos's archival rules hinge on the exact checkbox state inside the `## Follow-Up Needed` section plus the note's frontmatter `status` — and eyeballing those has produced wrong calls in the past. This script is the source of truth for that decision.

## When to use it

- **Always** during `/sync` Pre-Flight **Step 1b**, across all active inbox notes, before archiving anything.
- Any time you need to answer "is this inbox note safe to archive?" for one or more `inbox/*.md` files.

## How to run it

```bash
python3 .claude/skills/inbox-archive-tabulation/tabulate_followups.py inbox/*.md
```

Add `--json` for machine-readable output. With no arguments it defaults to `inbox/*.md` relative to the current directory. `README.md`, `.gitkeep`, and `.DS_Store` are skipped automatically.

Paste the human output verbatim into the `### Inbox task state (deterministic tabulation)` section of the `/sync` pre-flight block.

## How to read the output

```
060426-Daily Notes.md: status=active checked=2 blocking=1 placeholder=0 -> HOLD (1 open task)
    - [ ] do security training tomorrow/Friday
```

Each line gives the frontmatter `status`, the three counts, and a verdict. Open tasks are listed beneath HOLD (and ARCHIVE-when-complete) verdicts so they can be surfaced in the receipt.

### Checkbox classification (inside `## Follow-Up Needed` only — boxes elsewhere are ignored)

| Class | Pattern | Effect |
|---|---|---|
| **checked** | `- [x] …` (any text; `[x]` or `[X]`) | completed |
| **blocking** | `- [ ] <non-empty text>` | an open task **with content** → blocks archival |
| **placeholder** | `- [ ]` (empty / whitespace only) | unfilled placeholder → does **not** block |

Indented checkboxes (`  - [ ] …`) and `*` bullets are counted; the section ends at the next level-1 or level-2 heading.

### Verdicts → action

| Verdict | Condition | Action in `/sync` |
|---|---|---|
| `NO_ACTION (already archived)` | `status: archived` | skip |
| `ARCHIVE (status: complete)` | `status: complete` | archive regardless of open tasks; surface any open tasks in the receipt as "unfinished at archive" without inferring why |
| `HOLD` | `status: active` + ≥1 blocking task | **never archive** — the open task with content is the operator's signal the note still has business |
| `ARCHIVE-ELIGIBLE (synthesize first)` | `status: active` + 0 blocking tasks | archive **after** the note is fully incorporated into persistent state |

## The boundary of what this decides

The script settles the **deterministic** half: status + checkbox state → eligible / hold. It does **not** decide whether an eligible note has been *fully synthesized* — that judgment stays with `/sync`. A note marked `ARCHIVE-ELIGIBLE` is only moved to `archive/inbox/` once its signal has actually been written into persistent state.

**The tabulation wins.** If narrative reading and this script disagree on checkbox state, the script is correct — re-run it and re-verify before publishing the receipt. Reading interpretation is not a valid basis for the archival decision.
