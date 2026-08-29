#!/usr/bin/env python3
"""
resolve_meetings.py — turn a raw Google Calendar payload into a routed prep work order.

Claude fetches the calendar (the only step needing MCP) and saves the raw JSON.
Everything after that is deterministic and testable offline, which is the point:
routing decisions should not vary run to run.

What it does
  1. FILTER   drop what does not deserve a prep — focus blocks, declined events,
              zero-duration reminders, solo holds, build/deploy noise, broadcasts.
  2. CLASSIFY 1:1 vs. meeting. A 1:1 needs BOTH a `1:1` in the title AND exactly
              two non-resource attendees, one of them self. Neither test alone works.
              A 1:1 with a room booked has three attendees, so a naive `== 2` finds
              none of them; and anchoring on the slash instead of the `1:1` suffix
              parses "Atlas Program / Rollout Strategy" as a 1:1.
  3. ROUTE    resolve to a person or a work/meetings/ entity, and derive the output
              path. Never guesses: an unmatched meeting is REPORTED, not routed to a
              plausible-looking folder. Real calendars carry near-collisions — an
              "X Product / Program Weekly" alongside an "X Program Rollout", or four
              variants sharing the same token soup — and a silent kebab-case fallback
              would file meeting history into a wrong folder where nobody finds it.

Usage
  resolve_meetings.py <raw-calendar.json> [--date YYYY-MM-DD] [--root <vault>] [--json]
  resolve_meetings.py cal.json --date 2026-08-28 --json > work-order.json

Exit code is always 0; unrouted events are data, not errors.
"""

import sys
import os
import re
import json
import glob
import datetime

# ---------------------------------------------------------------------------
# TUNE THIS BLOCK FOR YOUR CALENDAR. The defaults are deliberately conservative;
# everything below is a heuristic about how YOUR organization names things.
# ---------------------------------------------------------------------------

# At or above this many human attendees, an event with no registered entity is a
# broadcast rather than a meeting you prep for. Note this only applies to events
# with NO work/meetings/ entity — a registered meeting is always prepped no matter
# how many people are invited, because your own curation is the better signal.
# Raise it if your org runs large working meetings; lower it if all-hands are small.
BROADCAST_ATTENDEES = 25

# Titles that are ops/build/deploy signal rather than meetings.
NOISE_RES = [
    re.compile(r"\bbuild\b", re.I),
    re.compile(r"\bdeploy\b", re.I),
    re.compile(r"^reminder\b", re.I),
    re.compile(r"\breminder:", re.I),
    re.compile(r"\bsmoke test\b", re.I),
    re.compile(r"\boffice hours\b", re.I),
]

ONE_ON_ONE_RE = re.compile(r"\b1\s*:\s*1\b", re.I)

# Decoration that appears in calendar titles but not in your work/meetings/ entity
# names, and so blocks matching. Add your own; order matters.
#
# The examples below are the shapes worth handling — a squad-code suffix, a team
# prefix, a "(formerly X)" rename, a punctuation-heavy abbreviation. Replace them
# with the ones your calendar actually uses:
#
#   "CMS Core Standup (Squad-1)"        -> strip the "(Squad-N)" suffix
#   "Content Systems: Cross System Sync" -> strip the team prefix
#   "Platform Weekly (formerly PCS)"     -> strip the rename note
#
TITLE_CLEANUPS = [
    (re.compile(r"\(formerly[^)]*\)", re.I), " "),        # rename note
    (re.compile(r"\([a-z]+-\d+\)", re.I), " "),           # squad/pod code suffix
    (re.compile(r"\(bi-wkly\)", re.I), " "),              # cadence note
    (re.compile(r"\s*&\s*status update\s*$", re.I), " "),  # trailing boilerplate
    (re.compile(r"\bcross[\s-]team\b", re.I), " crossteam "),  # hyphenation drift
]


def norm_title(s):
    """Lowercase, strip decoration, collapse to comparable tokens."""
    s = (s or "").strip()
    for rx, rep in TITLE_CLEANUPS:
        s = rx.sub(rep, s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return " ".join(s.split())


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower())
    return s.strip("-")


def read_frontmatter(path):
    """Minimal YAML frontmatter reader — scalars and simple lists only.
    Avoids a pyyaml dependency (system python here is 3.9 without it)."""
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except Exception:
        return out
    if not lines or lines[0].strip() != "---":
        return out
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("\"'") for v in val[1:-1].split(",")]
                out[key] = [v for v in items if v]
            elif val:
                out[key] = val.strip("\"'")
            else:
                out[key] = []
            continue
        m = re.match(r"^\s+-\s+(.*)$", line)
        if m and key:
            v = m.group(1).strip().strip("\"'")
            if v:
                out.setdefault(key, [])
                if isinstance(out[key], list):
                    out[key].append(v)
    return out


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def person_slug(root, name, aliases):
    """Pick the 1:1 folder slug for a person.

    An EXISTING journal/meetings/1on1s/<slug>/ folder always wins. If someone's
    history lives in 1on1s/alex/ but their people file is "Alexander Chen",
    deriving "alexander" from the first name would silently start a second
    folder and orphan every prior note. Aliases are checked before the first
    name for the same reason."""
    candidates = [slugify(a) for a in aliases]
    if name.split():
        candidates.append(slugify(name.split()[0]))
    candidates = [c for c in candidates if c]

    for c in candidates:
        if os.path.isdir(os.path.join(root, "journal", "meetings", "1on1s", c)):
            return c
    return candidates[-1] if candidates else slugify(name)


def load_people(root):
    """Return list of {file, name, slug, aliases[], emails[]}."""
    people = []
    for path in sorted(glob.glob(os.path.join(root, "people", "*.md"))):
        fm = read_frontmatter(path)
        name = os.path.basename(path)[:-3]
        aliases = [a for a in as_list(fm.get("aliases"))]
        people.append({
            "file": os.path.relpath(path, root),
            "name": name,
            "slug": person_slug(root, name, aliases),
            "aliases": [a.lower() for a in aliases],
            "emails": [e.lower() for e in as_list(fm.get("emails"))],
        })
    return people


def load_meetings(root):
    """Return list of {file, name, journal_path, keys[]} for work/meetings/ entities."""
    out = []
    for path in sorted(glob.glob(os.path.join(root, "work", "meetings", "*.md"))):
        fm = read_frontmatter(path)
        name = os.path.basename(path)[:-3]
        keys = {norm_title(name)}
        if fm.get("meeting"):
            keys.add(norm_title(fm["meeting"]))
        for a in as_list(fm.get("aliases")):
            keys.add(norm_title(a))
        out.append({
            "file": os.path.relpath(path, root),
            "name": name,
            "journal_path": (fm.get("journal_path") or "").strip(),
            "keys": set(k for k in keys if k),
        })
    return out


def humans(ev):
    return [a for a in (ev.get("attendees") or []) if not a.get("resource")]


def self_attendee(ev):
    for a in (ev.get("attendees") or []):
        if a.get("self"):
            return a
    return None


def event_times(ev):
    """Return (start_iso, end_iso, all_day)."""
    s, e = ev.get("start") or {}, ev.get("end") or {}
    if s.get("date"):
        return s.get("date"), e.get("date"), True
    return s.get("dateTime"), e.get("dateTime"), False


def duration_minutes(ev):
    s, e, all_day = event_times(ev)
    if all_day or not s or not e:
        return None
    try:
        ds = datetime.datetime.fromisoformat(s)
        de = datetime.datetime.fromisoformat(e)
        return int((de - ds).total_seconds() // 60)
    except ValueError:
        return None


def screen(ev):
    """Return a reason string if this event should NOT get a prep, else None."""
    title = (ev.get("summary") or "").strip()
    etype = ev.get("eventType") or "DEFAULT"

    if ev.get("status") == "cancelled":
        return "cancelled"
    if etype in ("FOCUS_TIME", "OUT_OF_OFFICE", "WORKING_LOCATION", "BIRTHDAY"):
        return "focus/OOO block ({})".format(etype)

    me = self_attendee(ev)
    if me and me.get("responseStatus") == "declined":
        return "declined"

    s, e, all_day = event_times(ev)
    if all_day:
        return "all-day block"

    dur = duration_minutes(ev)
    if dur is not None and dur <= 0:
        # 3 of these exist on this calendar and they break naive duration math.
        return "zero-duration reminder"

    n = len(humans(ev))
    if n <= 1:
        # DEFAULT-typed personal holds, e.g. "P+ Weekly Executive Roundup" (1 attendee).
        return "solo hold ({} attendee)".format(n)

    return None


def screen_unmatched(ev):
    """Second-stage filter, applied ONLY to events with no work/meetings/ entity.

    Attendee count alone is a bad discriminator in this org: "Atlas Program /
    Rollout Strategy" has 76 attendees and is a tracked meeting with its own
    entity and journal history, while a 90-person all-hands does not.
    So a registered entity wins outright — the operator's own curation is the signal, and
    size only decides among events he never registered."""
    title = (ev.get("summary") or "").strip()
    n = len(humans(ev))

    for rx in NOISE_RES:
        if rx.search(title):
            return "ops/broadcast noise"
    if n >= BROADCAST_ATTENDEES:
        return "unregistered broadcast ({} attendees)".format(n)
    return None


def is_one_on_one(ev):
    title = (ev.get("summary") or "").strip()
    if not ONE_ON_ONE_RE.search(title):
        return False
    h = humans(ev)
    return len(h) == 2 and any(a.get("self") for a in h)


def operator_identity(ev, people):
    """Who is the vault owner, as (person_or_None, set_of_name_tokens)?

    Derived from the calendar's own `self: true` attendee — never hardcoded.
    Falls back to the localpart of that address so the title heuristic still has
    something to exclude when no people/ file matches the operator."""
    me = self_attendee(ev)
    if not me:
        return None, set()
    email = (me.get("email") or "").lower()
    for p in people:
        if email and email in p["emails"]:
            return p, set(t.lower() for t in p["name"].split()) | set(p["aliases"])
    local = email.split("@")[0]
    tokens = set(t for t in re.split(r"[._-]+", local) if len(t) > 1)
    name = (me.get("displayName") or "")
    tokens |= set(t.lower() for t in name.split() if len(t) > 1)
    return None, tokens


def match_person(ev, people):
    """Resolve the 1:1 counterpart. Email is authoritative when people files carry
    `emails:` — the same human can appear under several corporate domains, so a
    domain-naive match is unreliable. Title token is the fallback."""
    others = [a for a in humans(ev) if not a.get("self")]
    if others:
        email = (others[0].get("email") or "").lower()
        for p in people:
            if email and email in p["emails"]:
                return p, "email"
        # localpart heuristic: firstname.lastname@ -> "firstname lastname"
        local = email.split("@")[0]
        guess = " ".join(re.split(r"[._-]+", local)).lower()
        for p in people:
            if guess and guess == p["name"].lower():
                return p, "email-localpart"

    # Title fallback: "Jordan/Alex 1:1" -> drop the operator's token, keep the other.
    _, mine = operator_identity(ev, people)
    title = (ev.get("summary") or "")
    stem = ONE_ON_ONE_RE.sub("", title).strip()
    tokens = [t.strip().lower() for t in re.split(r"[/&+]", stem) if t.strip()]
    for tok in tokens:
        if tok in mine:
            continue
        for p in people:
            if tok in p["aliases"] or tok == p["slug"]:
                if not (mine & (set(t.lower() for t in p["name"].split()) | set(p["aliases"]))):
                    return p, "title"
    return None, None


def match_meeting(ev, meetings):
    key = norm_title(ev.get("summary"))
    if not key:
        return None, None
    for m in meetings:
        if key in m["keys"]:
            return m, "exact"
    # Containment both ways, longest key first so the most specific entity wins.
    cands = []
    for m in meetings:
        for k in m["keys"]:
            if len(k) >= 8 and (k in key or key in k):
                cands.append((len(k), m))
    if cands:
        cands.sort(key=lambda t: t[0], reverse=True)
        best_len = cands[0][0]
        winners = {id(m): m for l, m in cands if l == best_len}
        if len(winners) == 1:
            return cands[0][1], "fuzzy"
        return None, "ambiguous"
    return None, None


def resolve(payload, target_date, root):
    people = load_people(root)
    meetings = load_meetings(root)
    preps, skipped, unrouted = [], [], []

    stamp = target_date.strftime("%m%d%y")

    for ev in payload.get("events") or []:
        title = (ev.get("summary") or "").strip()
        s, e, all_day = event_times(ev)

        if s and not all_day:
            try:
                if datetime.datetime.fromisoformat(s).date() != target_date:
                    continue
            except ValueError:
                pass

        reason = screen(ev)
        if reason:
            skipped.append({"title": title, "reason": reason, "start": s})
            continue

        if is_one_on_one(ev):
            person, how = match_person(ev, people)
            if not person:
                unrouted.append({"title": title, "start": s,
                                 "why": "1:1 detected but no people/ file matched the attendee"})
                continue
            slug = person["slug"]
            preps.append({
                "kind": "1on1",
                "target": person["name"],
                "matched_by": how,
                "command": "/prep {}".format(slug),
                "output_path": "journal/meetings/1on1s/{}/{}-{}-1on1.md".format(slug, stamp, slug),
                "person_file": person["file"],
                "title": title, "start": s, "end": e,
                "attendees": len(humans(ev)),
            })
            continue

        entity, how = match_meeting(ev, meetings)
        if not entity:
            # No entity: now size and noise patterns decide.
            reason = screen_unmatched(ev)
            if reason:
                skipped.append({"title": title, "reason": reason, "start": s})
                continue
            unrouted.append({"title": title, "start": s,
                             "why": "ambiguous — matches more than one work/meetings/ entity"
                                    if how == "ambiguous" else
                                    "no work/meetings/ entity matches this title"})
            continue
        if not entity["journal_path"]:
            unrouted.append({"title": title, "start": s,
                             "why": "entity {} has no journal_path".format(entity["file"])})
            continue

        folder = entity["journal_path"].rstrip("/")
        preps.append({
            "kind": "meeting",
            "target": entity["name"],
            "matched_by": how,
            "command": "/prep {}".format(slugify(entity["name"])),
            "output_path": "{}/{}-{}.md".format(folder, stamp, os.path.basename(folder)),
            "entity_file": entity["file"],
            "title": title, "start": s, "end": e,
            "attendees": len(humans(ev)),
        })

    preps.sort(key=lambda p: p["start"] or "")
    skipped.sort(key=lambda p: p["start"] or "")
    return {
        "date": target_date.isoformat(),
        "preps": preps,
        "skipped": skipped,
        "unrouted": unrouted,
        "counts": {"prep": len(preps), "skipped": len(skipped), "unrouted": len(unrouted)},
    }


def main(argv):
    args = [a for a in argv[1:]]
    as_json = "--json" in args
    if as_json:
        args.remove("--json")

    # Default the vault root to this script's own location (.claude/skills/<name>/ ->
    # root), not cwd. Under a scheduled task cwd is not the vault, and a cwd-relative
    # default fails SILENTLY: people/ and work/meetings/ come back empty, so every
    # meeting lands in `unrouted` and every 1:1 goes unmatched. A wrong answer that
    # looks like a real answer is the worst failure mode here.
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]

    target = None
    if "--date" in args:
        i = args.index("--date")
        target = datetime.date.fromisoformat(args[i + 1])
        del args[i:i + 2]

    if not args:
        print("usage: resolve_meetings.py <raw-calendar.json> [--date YYYY-MM-DD] "
              "[--root <vault>] [--json]", file=sys.stderr)
        return 2

    with open(args[0], "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if target is None:
        target = datetime.date.today()

    result = resolve(payload, target, root)

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    c = result["counts"]
    print("Work order for {} — {} prep(s), {} skipped, {} unrouted\n".format(
        result["date"], c["prep"], c["skipped"], c["unrouted"]))

    if result["preps"]:
        print("PREP:")
        for p in result["preps"]:
            t = (p["start"] or "")[11:16]
            print("  {:>5}  {:<8} {:<34} -> {}".format(
                t, p["kind"], p["target"][:34], p["output_path"]))
    if result["unrouted"]:
        print("\nUNROUTED (reported, never guessed):")
        for u in result["unrouted"]:
            print("  {:>5}  {:<44} {}".format((u["start"] or "")[11:16], u["title"][:44], u["why"]))
    if result["skipped"]:
        print("\nSKIPPED:")
        for s in result["skipped"]:
            print("  {:>5}  {:<44} {}".format((s["start"] or "")[11:16], s["title"][:44], s["reason"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
