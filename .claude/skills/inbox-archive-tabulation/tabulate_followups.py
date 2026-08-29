#!/usr/bin/env python3
"""
inbox-archive-tabulation — deterministic archive-eligibility for cosmos inbox notes.

Counts checkbox state inside each note's `## Follow-Up Needed` section, reads the
frontmatter `status`, and emits an archive-eligibility verdict per the cosmos
archival rules. This exists because reading-interpretation of checkbox state is
error-prone and has produced incorrect archival decisions — the count is the answer.

Verdicts
  NO_ACTION               status: archived — already processed, skip
  ARCHIVE                 status: complete — always archive; any open tasks are
                          surfaced as "unfinished at archive" without inferring why
  HOLD                    status: active + >=1 blocking task — never archive
  ARCHIVE_IF_SYNTHESIZED  status: active + 0 blocking tasks — archive once the note
                          is fully incorporated into persistent state (the synthesis
                          gate is /sync's judgment, not this script's)

Checkbox classification (inside ## Follow-Up Needed only — boxes elsewhere are ignored)
  checked       - [x] ...            any text, case-insensitive ([x] or [X])
  blocking      - [ ] <text>         an unchecked task WITH content -> blocks archival
  placeholder   - [ ]                empty / whitespace only -> does NOT block

Usage
  tabulate_followups.py inbox/*.md
  tabulate_followups.py --json inbox/*.md
  tabulate_followups.py                 # defaults to inbox/*.md relative to cwd
"""

import sys
import os
import re
import glob
import json

# Files in inbox/ that are never notes.
SKIP_BASENAMES = {"README.md", ".gitkeep", ".DS_Store"}

# A markdown heading at level 1 or 2 ends the Follow-Up Needed section.
# (### and deeper are treated as content inside the section.)
HEADING_END_RE = re.compile(r"^#{1,2}\s")
FOLLOWUP_HEADING_RE = re.compile(r"^#{1,6}\s*Follow-Up Needed\s*$", re.IGNORECASE)

CHECKED_RE = re.compile(r"^\s*[-*]\s+\[[xX]\]")
UNCHECKED_RE = re.compile(r"^\s*[-*]\s+\[ \]\s?(.*)$")


def parse_frontmatter_status(lines):
    """Return the lowercased `status:` value from YAML frontmatter, or 'active'
    if absent (active is the cosmos default)."""
    if not lines or lines[0].strip() != "---":
        return "active"
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"\s*status\s*:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip("\"'").lower()
    return "active"


def extract_followup_section(lines):
    """Return the list of lines inside the first `## Follow-Up Needed` section,
    or [] if the heading is absent."""
    out = []
    in_section = False
    for line in lines:
        if not in_section:
            if FOLLOWUP_HEADING_RE.match(line):
                in_section = True
            continue
        if HEADING_END_RE.match(line):
            break
        out.append(line)
    return out


def tabulate(section_lines):
    """Count checked / blocking / placeholder boxes; return counts + blocking texts."""
    checked = 0
    blocking = 0
    placeholder = 0
    blocking_items = []
    for line in section_lines:
        if CHECKED_RE.match(line):
            checked += 1
            continue
        m = UNCHECKED_RE.match(line)
        if m:
            text = m.group(1).strip()
            if text:
                blocking += 1
                blocking_items.append(text)
            else:
                placeholder += 1
    return checked, blocking, placeholder, blocking_items


def verdict_for(status, blocking):
    if status == "archived":
        return "NO_ACTION"
    if status == "complete":
        return "ARCHIVE"
    # status == active (or unknown -> treated as active default)
    if blocking >= 1:
        return "HOLD"
    return "ARCHIVE_IF_SYNTHESIZED"


def analyze(path):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    status = parse_frontmatter_status(lines)
    section = extract_followup_section(lines)
    checked, blocking, placeholder, blocking_items = tabulate(section)
    return {
        "file": path,
        "basename": os.path.basename(path),
        "status": status,
        "has_followup_section": bool(section) or any(
            FOLLOWUP_HEADING_RE.match(l) for l in lines
        ),
        "checked": checked,
        "blocking": blocking,
        "placeholder": placeholder,
        "blocking_items": blocking_items,
        "verdict": verdict_for(status, blocking),
    }


VERDICT_LABEL = {
    "NO_ACTION": "NO ACTION (already archived)",
    "ARCHIVE": "ARCHIVE (status: complete)",
    "HOLD": "HOLD",
    "ARCHIVE_IF_SYNTHESIZED": "ARCHIVE-ELIGIBLE (synthesize first)",
}


def print_human(results):
    for r in results:
        label = VERDICT_LABEL[r["verdict"]]
        suffix = ""
        if r["verdict"] == "HOLD":
            n = r["blocking"]
            suffix = " ({} open task{})".format(n, "" if n == 1 else "s")
        print(
            "{bn}: status={st} checked={c} blocking={b} placeholder={p} -> {lab}{sfx}".format(
                bn=r["basename"], st=r["status"], c=r["checked"], b=r["blocking"],
                p=r["placeholder"], lab=label, sfx=suffix,
            )
        )
        # Surface the open tasks for HOLD, and for ARCHIVE (complete) so /sync can
        # report them as "unfinished at archive".
        if r["blocking_items"] and r["verdict"] in ("HOLD", "ARCHIVE"):
            for item in r["blocking_items"]:
                print("    - [ ] {}".format(item))


def main(argv):
    args = list(argv[1:])
    as_json = False
    if "--json" in args:
        as_json = True
        args.remove("--json")

    if args:
        paths = []
        for a in args:
            # Allow shells that don't expand the glob, plus explicit file lists.
            expanded = glob.glob(a)
            paths.extend(expanded if expanded else [a])
    else:
        paths = sorted(glob.glob("inbox/*.md"))

    results = []
    for p in paths:
        if os.path.basename(p) in SKIP_BASENAMES:
            continue
        if not p.endswith(".md") or not os.path.isfile(p):
            continue
        try:
            results.append(analyze(p))
        except Exception as e:  # noqa: BLE001 — report and continue
            sys.stderr.write("ERROR reading {}: {}\n".format(p, e))

    results.sort(key=lambda r: r["basename"])

    if as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("(no inbox notes found)")
        else:
            print_human(results)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
