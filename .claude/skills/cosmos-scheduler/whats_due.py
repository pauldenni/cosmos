#!/usr/bin/env python3
"""
whats_due.py — decide deterministically which cosmos commands should run now.

This is the "run /sync as needed, not when you remember" half of the scheduler.
It composes the two skills that already exist rather than reimplementing them:

  sync-freshness/check_freshness.py  -> is there unincorporated signal?
  cadence-status/compute_cadence.py  -> what is past its expected interval?

Why signal-based for /sync. A clock-based sync fires when nothing changed and
stays quiet right after three notes get written. The real trigger is whether
anything in the vault is newer than the last sync. Age is only a backstop, so
state cannot silently rot when the operator writes nothing for a day.

Ordering matters: /sync always precedes /prep in the emitted plan, so preps
consume fresh state rather than yesterday's.

Usage
  whats_due.py [--root <vault>] [--max-sync-age-hours N] [--json]
"""

import sys
import os
import re
import json
import glob
import subprocess
import datetime

DEFAULT_MAX_SYNC_AGE_HOURS = 12

# Files whose modification implies unincorporated signal.
SIGNAL_GLOBS = [
    "inbox/*.md",
    "journal/meetings/**/*.md",
    "journal/personal/**/*.md",
]

SKILLS = ".claude/skills"


def run_json(root, script, args):
    path = os.path.join(root, SKILLS, script)
    if not os.path.isfile(path):
        return None
    try:
        out = subprocess.run([sys.executable, path] + args + ["--json"],
                             cwd=root, capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    if not out.stdout.strip():
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def expand(root, patterns):
    hits = []
    for pat in patterns:
        hits.extend(glob.glob(os.path.join(root, pat), recursive=True))
    return sorted(set(os.path.relpath(h, root) for h in hits if os.path.isfile(h)))


def sync_decision(root, max_age_hours):
    files = expand(root, SIGNAL_GLOBS)
    fresh = run_json(root, "sync-freshness/check_freshness.py", files)

    if not fresh or not fresh.get("last_sync"):
        return {"due": True, "reason": "no sync log found — never synced", "newer": []}

    newer = [f["file"] for f in fresh.get("files", []) if f.get("status") == "NEWER"]

    written = fresh["last_sync"].get("written")
    age_hours = None
    if written:
        try:
            last = datetime.datetime.strptime(written, "%Y-%m-%d %H:%M")
            age_hours = (datetime.datetime.now() - last).total_seconds() / 3600.0
        except ValueError:
            pass

    if newer:
        return {"due": True,
                "reason": "{} file(s) newer than last sync".format(len(newer)),
                "newer": newer[:20], "age_hours": age_hours}

    if age_hours is not None and age_hours > max_age_hours:
        return {"due": True,
                "reason": "last sync was {:.0f}h ago (backstop is {}h)".format(
                    age_hours, max_age_hours),
                "newer": [], "age_hours": age_hours}

    return {"due": False,
            "reason": "no unincorporated signal; last sync {:.0f}h ago".format(age_hours or 0),
            "newer": [], "age_hours": age_hours}


def overdue_commands(root):
    """Cadence rows past their interval, from both dashboards."""
    targets = [p for p in ("work/dashboard.md", "home/dashboard.md")
               if os.path.isfile(os.path.join(root, p))]
    if not targets:
        return []
    rows = run_json(root, "cadence-status/compute_cadence.py", targets) or []
    out = []
    for r in rows:
        cmd = (r.get("command") or "").strip().strip("`")
        if not cmd or cmd == "/sync":
            continue          # /sync is decided by signal, not by cadence age
        if (r.get("overdue_days") or 0) > 0:
            out.append({"command": cmd,
                        "overdue_days": r["overdue_days"],
                        "last_run": r.get("last_run"),
                        "expected": r.get("expected"),
                        "source": r.get("file")})
    out.sort(key=lambda r: r["overdue_days"], reverse=True)
    return out


def build_plan(root, max_age_hours, today):
    sync = sync_decision(root, max_age_hours)
    overdue = overdue_commands(root)

    plan = []
    if sync["due"]:
        plan.append({"command": "/sync", "why": sync["reason"], "priority": 1})

    # Weekly reflect is cadence-driven but worth naming explicitly: Friday is when
    # the week is actually reviewable.
    for row in overdue:
        pri = 2 if row["command"].startswith("/prep") else 3
        plan.append({"command": row["command"],
                     "why": "overdue {}d (expected {}, last run {})".format(
                         row["overdue_days"], row["expected"], row["last_run"]),
                     "priority": pri})

    return {
        "date": today.isoformat(),
        "weekday": today.strftime("%A"),
        "sync": sync,
        "overdue": overdue,
        "plan": sorted(plan, key=lambda p: p["priority"]),
    }


def main(argv):
    args = list(argv[1:])
    as_json = "--json" in args
    if as_json:
        args.remove("--json")

    # Same reasoning as resolve_meetings.py: derive the vault from this script's
    # location, not cwd, so a scheduled run from an arbitrary directory still works.
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]

    max_age = DEFAULT_MAX_SYNC_AGE_HOURS
    if "--max-sync-age-hours" in args:
        i = args.index("--max-sync-age-hours")
        max_age = float(args[i + 1])
        del args[i:i + 2]

    result = build_plan(root, max_age, datetime.date.today())

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("What's due — {} ({})\n".format(result["date"], result["weekday"]))
    s = result["sync"]
    print("/sync: {} — {}".format("DUE" if s["due"] else "not due", s["reason"]))
    for f in s.get("newer", [])[:10]:
        print("    newer: {}".format(f))
    if len(s.get("newer", [])) > 10:
        print("    ... and {} more".format(len(s["newer"]) - 10))

    if result["overdue"]:
        print("\nOverdue cadence:")
        for r in result["overdue"]:
            print("  {:<22} overdue {:>3}d  (expected {}, last {})".format(
                r["command"], r["overdue_days"], r["expected"], r["last_run"]))

    print("\nPlan, in order:")
    if not result["plan"]:
        print("  nothing due")
    for p in result["plan"]:
        print("  {}  — {}".format(p["command"], p["why"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
