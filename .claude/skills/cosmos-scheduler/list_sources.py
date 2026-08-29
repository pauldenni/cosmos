#!/usr/bin/env python3
"""
list_sources.py — deterministic pre-flight source listing for /sync and /prep.

WHY THIS EXISTS. The pre-flight used to be prose instructions ("run a directory
listing of all required source locations"), so Claude improvised a different
compound shell pipeline every run — `for d in journal/scans/*/; do ...; done`
and friends. Two problems:

  1. Commands containing shell expansion can only ever be approved ONCE. Claude
     Code will not write a persistent permission rule for them, because it
     cannot bound what the expansion produces next time. An unattended run
     therefore stalls on a prompt that can never be permanently granted.
  2. The listing was non-deterministic — different globs, different windows,
     different results run to run, which is exactly what a pre-flight audit
     record must not be.

A script fixes both: `python3 .claude/skills/...` is a stable, allowlistable
command, and the listing is identical every run.

It also does the one genuinely error-prone bit by hand-check: finding archived
risks/decisions whose `## Outcome` is still pending verification with a
check-back date that has come due.

Usage
  list_sources.py [--root <vault>] [--days 14] [--today YYYY-MM-DD] [--json]
"""

import os
import re
import sys
import glob
import json
import datetime

DEFAULT_WINDOW_DAYS = 14
SKIP_NAMES = {".gitkeep", ".DS_Store", "README.md"}

DATE_PREFIX = re.compile(r"^(\d{2})(\d{2})(\d{2})-")
PENDING = re.compile(r"_Pending verification\s*[—-]\s*check back\s*(\d{4}-\d{2}-\d{2})_", re.I)


def rel(root, p):
    return os.path.relpath(p, root).replace(os.sep, "/")


def file_date(path):
    """Prefer the MMDDYY filename prefix — for a dated artifact that is the date
    that matters. Fall back to mtime for undated files."""
    m = DATE_PREFIX.match(os.path.basename(path))
    if m:
        mm, dd, yy = (int(x) for x in m.groups())
        try:
            return datetime.date(2000 + yy, mm, dd)
        except ValueError:
            pass
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(path))
    except OSError:
        return None


def md_files(root, pattern, recursive=True):
    out = []
    for p in glob.glob(os.path.join(root, pattern), recursive=recursive):
        if not p.endswith(".md") or not os.path.isfile(p):
            continue
        if os.path.basename(p) in SKIP_NAMES:
            continue
        out.append(p)
    return sorted(out)


def within(paths, today, days):
    cutoff = today - datetime.timedelta(days=days)
    keep = []
    for p in paths:
        d = file_date(p)
        if d and d >= cutoff:
            keep.append((d, p))
    return [p for _, p in sorted(keep, reverse=True)]


def newest(paths):
    dated = [(file_date(p) or datetime.date.min, p) for p in paths]
    return max(dated)[1] if dated else None


def pending_outcomes(root, today):
    """Archived risks/decisions whose Outcome is still pending and now due."""
    due = []
    for sub in ("archive/risks", "archive/decisions"):
        for p in md_files(root, os.path.join(sub, "*.md"), recursive=False):
            try:
                text = open(p, encoding="utf-8").read()
            except Exception:
                continue
            m = PENDING.search(text)
            if not m:
                continue
            try:
                check = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            if check <= today:
                due.append({"file": rel(root, p), "check_back": m.group(1)})
    return sorted(due, key=lambda d: d["check_back"])


def collect(root, today, days):
    inbox = [p for p in md_files(root, "inbox/*.md", recursive=False)]

    one_on_ones = within(md_files(root, "journal/meetings/1on1s/**/*.md"), today, days)
    other_meetings = within(
        [p for p in md_files(root, "journal/meetings/**/*.md")
         if "/1on1s/" not in p.replace(os.sep, "/")], today, days)

    scans = {}
    for d in sorted(glob.glob(os.path.join(root, "journal/scans/*/"))):
        mode = os.path.basename(d.rstrip("/"))
        n = newest(md_files(root, os.path.join("journal/scans", mode, "*.md"), recursive=False))
        if n:
            scans[mode] = rel(root, n)

    def newest_rel(pattern):
        n = newest(md_files(root, pattern))
        return rel(root, n) if n else None

    return {
        "date": today.isoformat(),
        "window_days": days,
        "inbox": [rel(root, p) for p in inbox],
        "journal": {
            "1on1s": [rel(root, p) for p in one_on_ones],
            "other_meetings": [rel(root, p) for p in other_meetings],
            "scans_newest_per_mode": scans,
            "brief_newest": newest_rel("journal/briefs/**/*.md"),
            "reflect_newest": newest_rel("journal/personal/weekly-reflection/*.md"),
            "life_reflect_newest": newest_rel("journal/personal/life-reflect/*.md"),
            "sync_log_newest": newest_rel("journal/sync-log/*.md"),
        },
        "work": {
            "core": [f for f in ("work/dashboard.md", "work/org-health.md",
                                 "work/ownership-map.md", "work/executive-patterns.md")
                     if os.path.isfile(os.path.join(root, f))],
            "programs": [rel(root, p) for p in md_files(root, "work/programs/*.md", recursive=False)],
            "risks": [rel(root, p) for p in md_files(root, "work/risks/*.md", recursive=False)],
            "decisions": [rel(root, p) for p in md_files(root, "work/decisions/*.md", recursive=False)],
            "goals": [rel(root, p) for p in md_files(root, "work/goals/*.md", recursive=False)],
            "meetings": [rel(root, p) for p in md_files(root, "work/meetings/*.md", recursive=False)],
        },
        "people": [rel(root, p) for p in md_files(root, "people/*.md", recursive=False)],
        "home": {
            "dashboard": "home/dashboard.md" if os.path.isfile(os.path.join(root, "home/dashboard.md")) else None,
            "areas": [rel(root, p) for p in md_files(root, "home/areas/*.md", recursive=False)],
            "goals": [rel(root, p) for p in md_files(root, "home/goals/*.md", recursive=False)],
            "intentions": [rel(root, p) for p in md_files(root, "home/intentions/*.md", recursive=False)],
        },
        "outcomes_due": pending_outcomes(root, today),
    }


def render(d):
    L = []
    add = L.append
    add("### Inbox")
    for f in d["inbox"]:
        add("[x] `%s`" % f)
    if not d["inbox"]:
        add("_inbox is empty_")

    j = d["journal"]
    add("")
    add("### Journal — 1:1s (last %d days)" % d["window_days"])
    for f in j["1on1s"] or []:
        add("[x] `%s`" % f)
    if not j["1on1s"]:
        add("_none in window_")

    add("")
    add("### Journal — Other meetings (last %d days)" % d["window_days"])
    for f in j["other_meetings"] or []:
        add("[x] `%s`" % f)
    if not j["other_meetings"]:
        add("_none in window_")

    add("")
    add("### Journal — Scans / Briefs / Personal")
    for mode, f in sorted(j["scans_newest_per_mode"].items()):
        add("[x] `%s`  (newest %s scan)" % (f, mode))
    for label, key in (("brief", "brief_newest"), ("reflect", "reflect_newest"),
                       ("life-reflect", "life_reflect_newest"), ("last sync", "sync_log_newest")):
        if j[key]:
            add("[x] `%s`  (newest %s)" % (j[key], label))

    w = d["work"]
    add("")
    add("### Existing Persistent State")
    for f in w["core"]:
        add("[x] `%s`" % f)
    for label, key in (("programs", "programs"), ("risks", "risks"), ("decisions", "decisions"),
                       ("goals", "goals"), ("meetings", "meetings")):
        add("[x] `work/%s/` — %d file(s)" % (label, len(w[key])))
    add("[x] `people/` — %d file(s)" % len(d["people"]))

    h = d["home"]
    if h["dashboard"] or h["areas"] or h["goals"] or h["intentions"]:
        add("")
        add("### Home State")
        if h["dashboard"]:
            add("[x] `%s`" % h["dashboard"])
        for label in ("areas", "goals", "intentions"):
            if h[label]:
                add("[x] `home/%s/` — %d file(s)" % (label, len(h[label])))

    if d["outcomes_due"]:
        add("")
        add("### Outcomes due for verification")
        for o in d["outcomes_due"]:
            add("[x] `%s` — check back was %s" % (o["file"], o["check_back"]))

    return "\n".join(L)


def main(argv):
    args = list(argv[1:])
    as_json = "--json" in args
    if as_json:
        args.remove("--json")

    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]

    days = DEFAULT_WINDOW_DAYS
    if "--days" in args:
        i = args.index("--days")
        days = int(args[i + 1])
        del args[i:i + 2]

    today = datetime.date.today()
    if "--today" in args:
        i = args.index("--today")
        today = datetime.date.fromisoformat(args[i + 1])
        del args[i:i + 2]

    data = collect(root, today, days)
    print(json.dumps(data, indent=2, ensure_ascii=False) if as_json else render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
