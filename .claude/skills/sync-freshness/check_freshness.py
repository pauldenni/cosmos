#!/usr/bin/env python3
"""
sync-freshness — deterministic "is persistent state fresh for this work?" check.

Used by /prep and /brief. The semantic part — *which* files are in scope for this
prep/brief — is the caller's judgment. This script settles the deterministic part:
find the last /sync, and report which of the caller-supplied in-scope files were
modified after it (i.e. carry signal /sync hasn't propagated yet).

It does NOT make the final three-state verdict. It reports the facts and frames the
decision:
  0 newer                         -> ✓ Current
  >=1 newer, ordinary writeback   -> ◑ Reading N unsynced note(s) directly
  >=1 newer that introduces a NEW
    risk / changed decision /
    ownership change               -> ⚠ Recommend /sync first   (caller's call)

"Last /sync" = the sync-log file with the latest MMDDYY filename date (tie-break by
mtime); its mtime is the freshness threshold. No sync-log files -> never synced.

Usage
  check_freshness.py <in-scope files/globs ...>
  check_freshness.py --json inbox/060526-*.md journal/meetings/1on1s/alex/*.md
  check_freshness.py --sync-log-dir journal/sync-log <files ...>
"""

import sys
import os
import re
import glob
import json
import datetime

DEFAULT_SYNC_LOG_DIR = "journal/sync-log"
SYNC_NAME_RE = re.compile(r"(\d{2})(\d{2})(\d{2})-sync\.md$")


def find_last_sync(sync_log_dir):
    """Return (path, filename_date, mtime) for the latest sync-log, or None."""
    candidates = []
    for path in glob.glob(os.path.join(sync_log_dir, "*-sync.md")):
        m = SYNC_NAME_RE.search(os.path.basename(path))
        if not m:
            continue
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            fdate = datetime.date(2000 + yy, mm, dd)
        except ValueError:
            continue
        candidates.append((fdate, os.path.getmtime(path), path))
    if not candidates:
        return None
    # Latest filename date wins; tie-break on mtime.
    candidates.sort(key=lambda t: (t[0], t[1]))
    fdate, mtime, path = candidates[-1]
    return path, fdate, mtime


def expand(paths):
    out = []
    for p in paths:
        hits = glob.glob(p)
        if hits:
            out.extend(hits)
        else:
            out.append(p)  # report missing explicitly
    # De-dup while preserving order.
    seen = set()
    uniq = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def fmt_ts(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def main(argv):
    args = list(argv[1:])
    as_json = "--json" in args
    if as_json:
        args.remove("--json")
    sync_log_dir = DEFAULT_SYNC_LOG_DIR
    if "--sync-log-dir" in args:
        i = args.index("--sync-log-dir")
        sync_log_dir = args[i + 1]
        del args[i:i + 2]

    files = expand(args)
    last = find_last_sync(sync_log_dir)

    if last is None:
        result = {
            "last_sync": None,
            "verdict_hint": "RECOMMEND_SYNC",
            "reason": "no sync-log files found (never synced)",
            "files": [],
            "newer_count": None,
        }
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print("Last /sync: NONE — no files in {} (never synced).".format(sync_log_dir))
            print("Deterministic verdict: ⚠ Recommend /sync first (state has never been built).")
        return 0

    path, fdate, threshold = last
    rows = []
    newer = 0
    for f in files:
        if not os.path.isfile(f):
            rows.append({"file": f, "status": "MISSING", "mtime": None})
            continue
        mt = os.path.getmtime(f)
        is_newer = mt > threshold
        if is_newer:
            newer += 1
        rows.append({
            "file": f,
            "status": "NEWER" if is_newer else "CURRENT",
            "mtime": fmt_ts(mt),
        })

    result = {
        "last_sync": {"date": fdate.isoformat(), "file": path, "written": fmt_ts(threshold)},
        "files": rows,
        "newer_count": newer,
        "verdict_hint": "CURRENT" if newer == 0 else "UNSYNCED_PRESENT",
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return 0

    print("Last /sync: {} ({}, written {})".format(fdate.isoformat(), path, fmt_ts(threshold)))
    missing = [r for r in rows if r["status"] == "MISSING"]
    newer_rows = [r for r in rows if r["status"] == "NEWER"]
    current_rows = [r for r in rows if r["status"] == "CURRENT"]
    print("In-scope files checked: {}".format(len([r for r in rows if r["status"] != "MISSING"])))
    if newer_rows:
        print("  NEWER (unsynced):")
        for r in newer_rows:
            print("    - {}  ({})".format(r["file"], r["mtime"]))
    if current_rows:
        print("  CURRENT:")
        for r in current_rows:
            print("    - {}".format(r["file"]))
    if missing:
        print("  MISSING (not found — check the path):")
        for r in missing:
            print("    - {}".format(r["file"]))
    print("")
    if newer == 0:
        print("Deterministic verdict: ✓ Current — no in-scope file is newer than the last sync.")
    else:
        print("Deterministic verdict: {} in-scope file(s) newer than last sync.".format(newer))
        print("  -> ordinary writeback (1:1 / inbox / meeting): ◑ Reading {} unsynced note(s) directly.".format(newer))
        print("  -> if any introduces a NEW risk / changed decision / ownership change: ⚠ Recommend /sync first (your call).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
