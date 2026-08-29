#!/usr/bin/env python3
"""
cadence-status — deterministic cadence Status for cosmos dashboards.

Recomputes the `Status` column of every `Command | Last Run | Expected | Status`
cadence table in a dashboard file, per the cosmos status rule. This is pure date
math that /sync otherwise does by hand each run — getting the `overdue Nd` count
or the interval mapping slightly wrong is the failure this removes.

Status rule (from CLAUDE.md)
  Last Run = —            -> Status = —
  days_since <= interval  -> Status = ✓
  days_since >  interval  -> Status = ⚠️ overdue Nd   where N = days_since - interval
  unknown Expected        -> Status = ?   (cadence string not recognized — a finding)

  days_since = today - Last Run

Expected -> interval_days
  daily 1 · weekly 7 · bi-weekly 14 · monthly 30 · quarterly 90 ·
  semi-annual / 2× per year / twice per year 180 · annual / yearly 365
  (substring match, case-insensitive; e.g. "daily (2-3× per day)" -> 1)

Usage
  compute_cadence.py work/dashboard.md home/dashboard.md      # report (non-destructive)
  compute_cadence.py --write work/dashboard.md                # rewrite Status in place
  compute_cadence.py --today 2026-06-05 work/dashboard.md     # pin "today" (testing)
  compute_cadence.py --json work/dashboard.md
"""

import sys
import os
import re
import json
import datetime

DASH_CHARS = {"", "-", "—", "–", "--", "n/a", "none"}

REQUIRED_COLS = ("command", "last run", "expected", "status")


def interval_days(expected):
    """Map an Expected string to interval days, or None if unrecognized."""
    e = expected.strip().lower()
    if not e:
        return None
    if "bi-weekly" in e or "biweekly" in e or "bi weekly" in e:
        return 14
    if "weekly" in e:
        return 7
    if "daily" in e:
        return 1
    if "month" in e:
        return 30
    if "quarter" in e:
        return 90
    if "semi" in e or "2×" in e or "2x" in e or "twice" in e or "2 per year" in e:
        return 180
    if "annual" in e or "year" in e:
        return 365
    return None


def parse_date(s):
    s = s.strip()
    if s.lower() in DASH_CHARS:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def compute_status(last_run_raw, expected_raw, today):
    """Return (status_string, info_dict)."""
    last_run = parse_date(last_run_raw)
    interval = interval_days(expected_raw)
    info = {
        "last_run": last_run.isoformat() if last_run else None,
        "interval_days": interval,
        "days_since": None,
        "overdue_days": None,
    }
    if last_run is None:
        return "—", info
    if interval is None:
        return "?", info
    days_since = (today - last_run).days
    info["days_since"] = days_since
    if days_since <= interval:
        return "✓", info
    overdue = days_since - interval
    info["overdue_days"] = overdue
    return "⚠️ overdue {}d".format(overdue), info


def split_row(line):
    """Split a markdown table row into raw cells (without the outer empties)."""
    # Keep it simple: split on '|', drop the leading/trailing empties created by
    # the border pipes. Preserves interior spacing in each returned cell.
    parts = line.split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return parts


def is_separator(cells):
    for c in cells:
        if set(c.strip()) - set("-: "):
            return False
    return bool(cells)


def find_header(cells):
    """If cells form a cadence header, return {colname: index}, else None."""
    norm = [c.strip().lower() for c in cells]
    if all(col in norm for col in REQUIRED_COLS):
        return {col: norm.index(col) for col in REQUIRED_COLS}
    return None


def process_file(path, today, write):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    rows_out = []
    changed = 0
    header = None
    new_lines = list(lines)

    for i, line in enumerate(lines):
        if "|" not in line:
            header = None
            continue
        cells = split_row(line)
        if not cells:
            header = None
            continue
        if is_separator(cells):
            continue
        maybe = find_header(cells)
        if maybe:
            header = maybe
            continue
        if header is None:
            continue
        # Data row under a known cadence header.
        if max(header.values()) >= len(cells):
            continue  # malformed row, skip safely
        command = cells[header["command"]].strip()
        last_run_raw = cells[header["last run"]].strip()
        expected_raw = cells[header["expected"]].strip()
        old_status = cells[header["status"]].strip()
        new_status, info = compute_status(last_run_raw, expected_raw, today)
        rows_out.append({
            "file": path, "command": command, "last_run_raw": last_run_raw,
            "expected": expected_raw, "old_status": old_status,
            "new_status": new_status, "changed": old_status != new_status,
            **info,
        })
        if old_status != new_status:
            changed += 1
        if write:
            # Rewrite just the status cell, preserving its original width if possible.
            raw_cells = line.split("|")
            # Map header index (in trimmed cell list) back to raw split index.
            offset = 1 if (raw_cells and raw_cells[0].strip() == "") else 0
            raw_idx = header["status"] + offset
            orig = raw_cells[raw_idx]
            cell = " {} ".format(new_status)
            if len(cell) < len(orig):
                cell = cell + " " * (len(orig) - len(cell))
            raw_cells[raw_idx] = cell
            new_lines[i] = "|".join(raw_cells)

    if write and changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(new_lines))

    return rows_out, changed


def main(argv):
    args = list(argv[1:])
    write = False
    as_json = False
    today = datetime.date.today()

    if "--write" in args:
        write = True
        args.remove("--write")
    if "--json" in args:
        as_json = True
        args.remove("--json")
    if "--today" in args:
        idx = args.index("--today")
        today = parse_date(args[idx + 1])
        del args[idx:idx + 2]
        if today is None:
            sys.stderr.write("ERROR: --today needs YYYY-MM-DD\n")
            return 2

    if not args:
        args = [p for p in ("work/dashboard.md", "home/dashboard.md") if os.path.isfile(p)]

    all_rows = []
    total_changed = 0
    for path in args:
        if not os.path.isfile(path):
            sys.stderr.write("ERROR: no such file: {}\n".format(path))
            continue
        rows, changed = process_file(path, today, write)
        all_rows.extend(rows)
        total_changed += changed

    if as_json:
        print(json.dumps(all_rows, indent=2, ensure_ascii=False))
        return 0

    if not all_rows:
        print("(no cadence tables found)")
        return 0

    print("today = {}{}".format(today.isoformat(), "   [--write applied]" if write else ""))
    for r in all_rows:
        flag = "  (changed from '{}')".format(r["old_status"]) if r["changed"] else ""
        print("{cmd}: last_run={lr} expected={exp} -> {st}{flag}".format(
            cmd=r["command"], lr=r["last_run_raw"] or "—",
            exp=r["expected"], st=r["new_status"], flag=flag))
    print("{} row(s), {} changed.".format(len(all_rows), total_changed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
