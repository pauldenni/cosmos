#!/usr/bin/env python3
"""
canonical-entity-index — regenerate .cosmos/instructions/canonical-entity-index.md
deterministically from the filesystem + CLAUDE.md frontmatter.

The index is a DERIVED view, not a hand-maintained file. Generating it by hand
drifts (entities on disk get missed, frontmatter-only entities get dropped, People
ordering wanders). This script implements the algorithm in
.cosmos/instructions/canonical-entity-index-rebuild.md exactly and idempotently.

Sections & sources (active only — archive/ is excluded):
  People    people/*.md (top-level)        + CLAUDE.md operator/svp/vp/director/manager/team_members
  Programs  work/programs/*.md             + CLAUDE.md programs
  Systems   reference/systems/*.md         + CLAUDE.md systems
  Domains   reference/domains/*.md         + CLAUDE.md domains
  Teams     people/teams/*.md
  Meetings  work/meetings/*.md
  Risks     work/risks/*.md
  Decisions work/decisions/*.md
  Goals     work/goals/*.md

People order: operator first, then leadership chain (svp, vp, director, manager,
skipping empties), then everyone else alphabetical (case-insensitive). All other
sections: alphabetical (case-insensitive). Dedupe is case-insensitive; disk
spelling wins. Empty section -> "_(none yet)_".

Usage
  rebuild_index.py                 # print generated index to stdout (dry run)
  rebuild_index.py --write         # overwrite .cosmos/instructions/canonical-entity-index.md
  rebuild_index.py --diff          # unified diff vs the current index
  rebuild_index.py --date 2026-06-05   # pin the "Last regenerated" date (testing)
"""

import sys
import os
import re
import glob
import datetime
import difflib

INDEX_PATH = ".cosmos/instructions/canonical-entity-index.md"
CLAUDE_PATH = "CLAUDE.md"

SCALAR_KEYS = ("operator", "svp", "vp", "director", "manager")
LIST_KEYS = ("team_members", "programs", "systems", "domains")

# (section title, folder glob) for disk-sourced names. People/Programs/Systems/
# Domains also merge frontmatter (handled separately).
DISK_SOURCES = [
    ("People", "people/*.md"),
    ("Programs", "work/programs/*.md"),
    ("Systems", "reference/systems/*.md"),
    ("Domains", "reference/domains/*.md"),
    ("Teams", "people/teams/*.md"),
    ("Meetings", "work/meetings/*.md"),
    ("Risks", "work/risks/*.md"),
    ("Decisions", "work/decisions/*.md"),
    ("Goals", "work/goals/*.md"),
]

SECTION_ORDER = ["People", "Programs", "Systems", "Domains", "Teams",
                 "Meetings", "Risks", "Decisions", "Goals"]

SKIP_BASENAMES = {"README", "_index"}


def clean_name(value):
    """Strip quotes and [[ ]] wikilink wrappers from a frontmatter value."""
    v = value.strip().strip('"').strip("'").strip()
    if v.startswith("[[") and v.endswith("]]"):
        v = v[2:-2].strip()
    return v


def disk_names(pattern):
    out = []
    for path in glob.glob(pattern):
        base = os.path.basename(path)
        if not base.endswith(".md"):
            continue
        name = base[:-3]
        if name in SKIP_BASENAMES or name.startswith("."):
            continue
        out.append(name)
    return out


def parse_claude_frontmatter(path):
    """Return dict: scalar keys -> str (may be ''), list keys -> [str]."""
    result = {k: "" for k in SCALAR_KEYS}
    for k in LIST_KEYS:
        result[k] = []
    if not os.path.isfile(path):
        return result
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    if not lines or lines[0].strip() != "---":
        return result
    current_list = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        # List item under the current list key.
        m_item = re.match(r"\s+-\s+(.*)$", line)
        if m_item and current_list:
            name = clean_name(m_item.group(1))
            if name:
                result[current_list].append(name)
            continue
        # key: value  (or key: with nothing)
        m_kv = re.match(r"([A-Za-z_]+)\s*:\s*(.*)$", line)
        if m_kv:
            key, val = m_kv.group(1), m_kv.group(2)
            if key in LIST_KEYS:
                current_list = key
                # A list key may also carry an inline value on rare formats.
                if val.strip():
                    name = clean_name(val)
                    if name:
                        result[key].append(name)
                continue
            current_list = None
            if key in SCALAR_KEYS:
                result[key] = clean_name(val)
            continue
        # Any other line ends an open list context.
        current_list = None
    return result


def dedupe(names):
    """Case-insensitive dedupe; first occurrence's spelling wins."""
    seen = {}
    for n in names:
        key = n.lower()
        if key not in seen:
            seen[key] = n
    return seen


def render_entry(name):
    return "- [[{}]]".format(name)


def build_index(today, fm, sources):
    sections = {}

    # Disk names per section.
    disk = {title: disk_names(pat) for title, pat in sources}

    # People: operator + chain first, then everyone else alphabetical.
    people_all = list(disk.get("People", []))
    people_all += fm.get("team_members", [])
    for k in SCALAR_KEYS:
        if fm.get(k):
            people_all.append(fm[k])
    people_map = dedupe(people_all)

    chain = []
    chain_keys_lower = set()
    for k in SCALAR_KEYS:  # operator handled first explicitly below
        pass
    ordered_chain_keys = ["operator", "svp", "vp", "director", "manager"]
    for k in ordered_chain_keys:
        v = fm.get(k)
        if v and v.lower() in people_map and v.lower() not in chain_keys_lower:
            chain.append(people_map[v.lower()])
            chain_keys_lower.add(v.lower())
    rest = sorted([disp for low, disp in people_map.items()
                   if low not in chain_keys_lower], key=str.lower)
    sections["People"] = chain + rest

    # Merge frontmatter into Programs / Systems / Domains; others disk-only.
    fm_merge = {"Programs": "programs", "Systems": "systems", "Domains": "domains"}
    for title in SECTION_ORDER:
        if title == "People":
            continue
        names = list(disk.get(title, []))
        if title in fm_merge:
            names += fm.get(fm_merge[title], [])
        m = dedupe(names)
        sections[title] = sorted(m.values(), key=str.lower)

    # Render.
    lines = []
    lines.append("# Canonical Entity Index")
    lines.append("")
    lines.append("This file is the source of truth for entity names in your cosmos "
                 "vault. It is regenerated automatically by cosmos commands — do not "
                 "edit by hand. To add an entity, create the entity file (e.g. "
                 "`work/programs/<name>.md`) or update `CLAUDE.md` frontmatter, and "
                 "the next command run will pick it up.")
    lines.append("")
    lines.append("Last regenerated: {} by /sync".format(today))
    for title in SECTION_ORDER:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("# {}".format(title))
        lines.append("")
        entries = sections[title]
        if entries:
            for name in entries:
                lines.append(render_entry(name))
        else:
            lines.append("_(none yet)_")
    return "\n".join(lines) + "\n"


def main(argv):
    args = list(argv[1:])
    write = "--write" in args
    show_diff = "--diff" in args
    for f in ("--write", "--diff"):
        if f in args:
            args.remove(f)
    today = datetime.date.today().isoformat()
    if "--date" in args:
        i = args.index("--date")
        today = args[i + 1]
        del args[i:i + 2]

    fm = parse_claude_frontmatter(CLAUDE_PATH)
    content = build_index(today, fm, DISK_SOURCES)

    if show_diff:
        current = ""
        if os.path.isfile(INDEX_PATH):
            with open(INDEX_PATH, "r", encoding="utf-8") as fh:
                current = fh.read()
        diff = difflib.unified_diff(
            current.splitlines(True), content.splitlines(True),
            fromfile=INDEX_PATH + " (current)", tofile=INDEX_PATH + " (rebuilt)")
        sys.stdout.writelines(diff)
        return 0

    if write:
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        with open(INDEX_PATH, "w", encoding="utf-8") as fh:
            fh.write(content)
        sys.stderr.write("wrote {}\n".format(INDEX_PATH))
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
