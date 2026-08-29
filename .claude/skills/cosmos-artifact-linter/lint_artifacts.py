#!/usr/bin/env python3
"""
cosmos-artifact-linter — validate rendered cosmos artifacts against the vault's
hard rules. ERRORs are deterministic violations; WARNs need human judgment.

Linking / structure checks
  [ERROR] wikilink-resolves   path-form wikilink [[work/risks/foo]] must point at an
                              existing file (<target>.md). The hard rule: a wikilink's
                              target must match a real filename exactly.
  [WARN]  wikilink-basename   basename-form [[Foo]] resolves to no .md in the vault
                              (possible broken link — or an intentional not-yet-created
                              entity / a non-file reference).
  [ERROR] bare-path           a specific vault .md path written in a `code span`
                              instead of a wikilink (globs, folders, URLs, and
                              placeholder paths like <name>/MMDDYY are fine).
  [ERROR] frontmatter-quote   a [[wikilink]] in YAML frontmatter not wrapped in quotes.
  [ERROR] table-blank-line    a table's first row not preceded by a blank line. Obsidian
                              (GFM) won't render a table that directly follows a paragraph
                              or bold label — it shows the raw `| ... |` source. Headings,
                              fences, and other table rows are fine as predecessors.
  [WARN]  scope-narration     cosmos-internal narration in a work artifact (the word
                              "cosmos", or a command-mechanism phrase) that isn't in an
                              allowed metadata context. Persistent state describes the
                              work, not cosmos's own machinery — review each hit.

Output-contract checks (see .cosmos/instructions/output-contract.md)
  [ERROR] word-cap            artifact body exceeds the cap for its type (§1).
  [ERROR] sentence-length     a sentence longer than MAX_SENTENCE_WORDS words (§2).
  [ERROR] banned-phrase       a hedge or filler opener (§3).
  [ERROR] trend-prose         trend rendered as a phrase instead of the 5-state enum (§3).
  [ERROR] placeholder         bare `-` bullet, TBD, empty table row, or _None._ (§4).
  [ERROR] linked-artifacts    a trailing `## Linked Artifacts` section (§8).
  [WARN]  repeated-content    two sentences in one file that state the same fact in
                              different words (§5). Paraphrased repetition is the
                              dominant bloat mechanism; this is the detector for it.
  [WARN]  history-unbounded   a `## History` section with more than MAX_HISTORY_ENTRIES
                              dated entries (§6).

Scope: checks run on rendered artifacts — by default work/, people/, home/, and journal/
(excluding journal/sync-log/). Infrastructure (.claude/, .cosmos/, CLAUDE.md),
templates, raw inbox capture, and archive/ are excluded by default; pass explicit
paths to lint anything.

Usage
  lint_artifacts.py                         # lint the default artifact set
  lint_artifacts.py work/ people/           # lint specific paths/dirs
  lint_artifacts.py --json work/org-health.md
  lint_artifacts.py --errors-only           # suppress WARNs
  lint_artifacts.py --stats                 # print per-file word count vs cap
Exit code: 1 if any ERROR, else 0.
"""

import sys
import os
import re
import glob
import json

VAULT_DIRS = ("work", "people", "home", "journal", "reference", "inbox", "archive",
              ".cosmos", ".claude")

DEFAULT_GLOBS = ["work/**/*.md", "people/**/*.md", "home/**/*.md", "journal/**/*.md"]
DEFAULT_EXCLUDE_DIRS = ("archive", "journal/sync-log", "reference/templates",
                        ".claude", ".cosmos", ".git", ".obsidian")

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
CODESPAN_RE = re.compile(r"`([^`]+)`")
PLACEHOLDER_RE = re.compile(r"<[^>]+>|MMDDYY|YYYY|MM-DD|<name>")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|")          # a markdown table row (leading + inner pipe)
# Predecessors a table may legitimately follow with no blank line (each closes its own
# block, so the table starts fresh and renders): a heading, the frontmatter / hr ---,
# or a fence line. A paragraph or bold label does NOT — that's the bug this catches.
TABLE_OK_PREV_RE = re.compile(r"^\s*(#{1,6}\s|---\s*$|```)")
HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.*)$")

# ---------------------------------------------------------------- output contract

MAX_SENTENCE_WORDS = 25
MAX_HISTORY_ENTRIES = 4

# Sections that are a dated log rather than current-state prose. They are exempt
# from the body word cap and bounded by entry count instead.
#
# "Leadership Notes" belongs here because a person file is the system of record
# for that person's longitudinal record — /sync's bounded-growth rule migrates
# older org-health observations INTO it. Counting those dated entries against a
# 300-word body cap would evict the very history the design puts there.
DATED_LOG_SECTIONS = ("history", "leadership notes", "1:1 notes")

# People are the longitudinal home, so they keep more than an entity file does.
MAX_HISTORY_ENTRIES_PERSON = 8

# Ordered most-specific-first; first match wins.
WORD_CAPS = [
    (re.compile(r"^work/dashboard\.md$"), "dashboard", 600),
    (re.compile(r"^work/org-health\.md$"), "org-health", 600),
    # 500, not 400: this file is an enumeration, not prose. Its length tracks how
    # many things the org owns (9 owners x ~10 items), so a tight cap forces
    # dropping ownership assignments — the exact facts it exists to record. The
    # cap still guards against re-narration, which is what the contract is for.
    (re.compile(r"^work/ownership-map\.md$"), "ownership-map", 500),
    (re.compile(r"^work/executive-patterns\.md$"), "executive-patterns", 400),
    (re.compile(r"^work/programs/[^/]+\.md$"), "program", 500),
    (re.compile(r"^work/risks/[^/]+\.md$"), "risk", 300),
    (re.compile(r"^work/decisions/[^/]+\.md$"), "decision", 250),
    (re.compile(r"^work/goals/[^/]+\.md$"), "goal", 250),
    (re.compile(r"^journal/meetings/1on1s/"), "1on1-prep", 400),
    (re.compile(r"^journal/meetings/"), "meeting-prep", 400),
    (re.compile(r"^journal/briefs/.*short"), "brief-short", 150),
    (re.compile(r"^journal/briefs/.*svp"), "brief-svp", 400),
    (re.compile(r"^journal/briefs/.*vp"), "brief-vp", 300),
    (re.compile(r"^journal/scans/"), "scan", 600),
    (re.compile(r"^journal/personal/daily/.*-now\.md$"), "now", 250),
    (re.compile(r"^journal/personal/daily/.*-day\.md$"), "day-plan", 400),
    (re.compile(r"^journal/personal/weekly-reflection/"), "reflect", 500),
    (re.compile(r"^journal/personal/life-reflect/"), "life-reflect", 500),
    (re.compile(r"^journal/sync-log/"), "sync-log", 300),
    (re.compile(r"^journal/calibrations/"), "calibration", 600),
    (re.compile(r"^people/[^/]+\.md$"), "person", 300),
    (re.compile(r"^home/dashboard\.md$"), "home-dashboard", 400),
    (re.compile(r"^home/areas/[^/]+\.md$"), "home-area", 250),
]

BANNED_PHRASES = [
    "may want to consider", "it might be worth", "it could be argued",
    "seems to suggest", "appears to indicate", "it is important to note",
    "it's worth noting", "it is worth noting", "as mentioned above",
    "at the end of the day", "needless to say",
]
# Standalone hedge words — matched as whole words to avoid false hits.
BANNED_WORDS = ["perhaps", "potentially", "arguably"]

# Multi-word trend phrases retired in favour of the 5-state enum.
TREND_PROSE = [
    "dependency concentration increasing", "ownership ambiguity persisting",
    "leadership bottleneck risk increasing", "escalation likelihood increasing",
    "delivery confidence improving", "delivery confidence weakening",
    "escalation pressure decreasing", "confidence increasing", "confidence weakening",
    "ownership maturing", "alignment degrading", "improving alignment",
    "reducing dependency risk", "manageable with current mitigation",
    "currently acceptable but fragile", "unresolved but contained",
    "stable but important", "no material movement", "gaining clarity",
]

PLACEHOLDER_LINE_RES = [
    (re.compile(r"^\s*[-*]\s*$"), "bare '-' placeholder bullet"),
    (re.compile(r"^\s*\|(\s*\|)+\s*$"), "empty table row"),
    (re.compile(r"^\s*_?None\.?_?\s*$", re.IGNORECASE), "'None.' filler line"),
    (re.compile(r"^\s*[-*]?\s*TBD\s*$", re.IGNORECASE), "TBD placeholder"),
]

STOPWORDS = set("""a an the and or but if then than that this these those of to in on at by for
with from as is are was were be been being it its it's has have had do does did not no so such
you your yours we our they their he she his her them us i me my will would can could should may
might must shall about into over under out up down off again further once here there when where
why how all any both each few more most other some only own same too very just also""".split())

# ---------------------------------------------------------------- narration

# Narration: the word cosmos, or a command-mechanism phrase. Kept tight to limit noise.
NARRATION_RES = [
    re.compile(r"\bcosmos\b", re.IGNORECASE),
    re.compile(r"\bpre-flight\b", re.IGNORECASE),
    re.compile(r"\btabulation\b", re.IGNORECASE),
    re.compile(r"re-read discipline", re.IGNORECASE),
    re.compile(r"journal re-read", re.IGNORECASE),
    re.compile(r"settings\.json|write-logger", re.IGNORECASE),
]
# Lines that are legitimate when/where metadata — skip narration check on them.
METADATA_SKIP_RES = [
    re.compile(r"via /sync", re.IGNORECASE),
    re.compile(r"\bLast Run\b", re.IGNORECASE),
    re.compile(r"\bLast Updated\b", re.IGNORECASE),
    re.compile(r"\bCadence\b", re.IGNORECASE),
    re.compile(r"^\s*\|"),                       # table row
    re.compile(r"Surfaced .* from", re.IGNORECASE),
]


# Output-contract checks (caps, sentence length, banned phrases) govern *live* state
# and *new* writes. Dated journal artifacts are immutable records of what was said at
# the time — rewriting history would be dishonest, so a default sweep leaves them alone.
# Passing a journal path explicitly (as /prep and /brief do after writing) opts it in.
LIVE_PREFIXES = ("work/", "people/", "home/")

# Human capture. the operator writes these himself in Obsidian; cosmos does not generate
# them and has no business rewriting his prose to fit a word cap. Same treatment
# inbox/ already gets.
#
# home/areas/ is here deliberately. /sync does write to it, but the operator also writes
# into it directly and in his own voice — first person, lowercase, unguarded. The
# home layer's whole point is that it is personal, and there is no upward audience
# to protect. Enforcing an executive word cap there would mean editing a man's
# private reflections for concision, which is not a tradeoff worth making.
# home/dashboard.md stays in scope: it is generated, and it is an orientation
# surface where length actually costs something.
HUMAN_CAPTURE = ("home/projects/", "home/travel/", "home/areas/", "home/intentions/")


def in_contract_scope(path, explicit):
    norm = os.path.normpath(path).replace(os.sep, "/")
    if norm.startswith(HUMAN_CAPTURE) or os.path.basename(norm) == "README.md":
        return False
    return norm in explicit or norm.startswith(LIVE_PREFIXES)


def collect_targets(args):
    paths = []
    if args:
        for a in args:
            if os.path.isdir(a):
                paths.extend(glob.glob(os.path.join(a, "**", "*.md"), recursive=True))
            else:
                hits = glob.glob(a, recursive=True)
                paths.extend(hits if hits else [a])
    else:
        for g in DEFAULT_GLOBS:
            paths.extend(glob.glob(g, recursive=True))
    out = []
    seen = set()
    for p in paths:
        norm = os.path.normpath(p)
        if any(part == ".md" for part in [norm]) and not norm.endswith(".md"):
            continue
        if not norm.endswith(".md"):
            continue
        if any(norm == d or norm.startswith(d + os.sep) for d in DEFAULT_EXCLUDE_DIRS):
            continue
        if norm not in seen and os.path.isfile(norm):
            seen.add(norm)
            out.append(norm)
    return sorted(out)


def parse_aliases(path):
    """Return lowercased aliases from a file's YAML frontmatter `aliases:` list."""
    out = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except Exception:
        return out
    if not lines or lines[0].strip() != "---":
        return out
    in_aliases = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if re.match(r"aliases\s*:", line):
            in_aliases = True
            # inline form: aliases: [Zach, z-dub]
            inline = line.split(":", 1)[1].strip()
            if inline.startswith("["):
                for part in inline.strip("[]").split(","):
                    a = part.strip().strip("\"'")
                    if a:
                        out.append(a.lower())
                in_aliases = False
            continue
        if in_aliases:
            m = re.match(r"\s+-\s+(.*)$", line)
            if m:
                a = m.group(1).strip().strip("\"'")
                if a:
                    out.append(a.lower())
            elif line.strip() and not line.startswith(" "):
                in_aliases = False
    return out


def build_vault_index():
    """Return (pathset, names) where pathset = relative paths w/o ext, and names =
    set of resolvable basenames + aliases (lowercased)."""
    pathset = set()
    names = set()
    for d in VAULT_DIRS:
        for p in glob.glob(os.path.join(d, "**", "*.md"), recursive=True):
            norm = os.path.normpath(p)
            no_ext = norm[:-3]
            pathset.add(no_ext)
            names.add(os.path.basename(no_ext).lower())
            for alias in parse_aliases(norm):
                names.add(alias)
    return pathset, names


def strip_target(raw):
    """Strip alias (|...), heading (#...), trailing .md from a wikilink target.
    Obsidian table cells escape the alias pipe as ``\\|`` so it doesn't terminate
    the column — normalize that before splitting."""
    raw = raw.replace("\\|", "|")
    t = raw.split("|", 1)[0].split("#", 1)[0].strip()
    if t.endswith(".md"):
        t = t[:-3]
    return t


def looks_like_vault_file(span):
    s = span.strip()
    if "://" in s:                       # URL
        return False
    if "*" in s:                         # glob
        return False
    if PLACEHOLDER_RE.search(s):         # pattern/placeholder, not a real file
        return False
    if not s.endswith(".md"):            # folder-only or non-file
        return False
    first = s.split("/", 1)[0]
    # Infra (.claude/.cosmos) is referenced in code spans by convention — CLAUDE.md
    # itself points at command/instruction sources this way; they are never wikilinked.
    if first in (".claude", ".cosmos"):
        return False
    return first in VAULT_DIRS


def artifact_type(path):
    """Return (type_name, cap) for a vault-relative path, or (None, None)."""
    norm = os.path.normpath(path).replace(os.sep, "/")
    for rx, name, cap in WORD_CAPS:
        if rx.search(norm):
            return name, cap
    return None, None


def split_sentences(text):
    """Split prose into sentences on . ! ? followed by whitespace. Avoids splitting
    on decimals (3.5), single-letter initials, and common abbreviations.

    Inline emphasis is stripped FIRST. cosmos prose is full of bolded sentences
    ending `...directly named.** Then surface it normally.` — with the markers left
    in, the terminator is followed by `*` rather than whitespace, the split never
    happens, and two ordinary sentences get reported as one over-long one."""
    text = re.sub(r"\*\*|__|(?<!\w)[*_](?!\w)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    protected = re.sub(r"(?<=\b[A-Z])\.(?=\s)", "\x00", text)          # initials: J. Smith
    protected = re.sub(r"(?<=\d)\.(?=\d)", "\x01", protected)          # decimals: 3.5
    for abbr in ("e.g.", "i.e.", "etc.", "vs.", "approx.", "Dr.", "Mr.", "Ms."):
        protected = protected.replace(abbr, abbr.replace(".", "\x02"))
    parts = re.split(r"(?<=[.!?])\s+", protected)
    return [p.replace("\x00", ".").replace("\x01", ".").replace("\x02", ".").strip()
            for p in parts if p.strip()]


def count_words(s):
    """Word count with each wikilink/embed collapsed to a single token."""
    s = EMBED_RE.sub(" LINK ", s)
    s = WIKILINK_RE.sub(" LINK ", s)
    s = re.sub(r"[#*_>`|]", " ", s)
    return len([w for w in s.split() if re.search(r"[A-Za-z0-9]", w)])


def content_words(s):
    s = EMBED_RE.sub(" ", s)
    s = WIKILINK_RE.sub(lambda m: " " + m.group(1).split("/")[-1] + " ", s)
    words = re.findall(r"[a-z0-9]+", s.lower())
    return set(w for w in words if w not in STOPWORDS and len(w) > 2)


def body_analysis(lines, fm_end):
    """Return (body_word_count, prose_units, history_entry_count).

    prose_units are (lineno, text) for non-table, non-heading, non-fence prose —
    the surface the sentence-length and repetition checks run on. Words inside
    `## History` are excluded from the body count (bounded separately, §6)."""
    total = 0
    prose = []
    history_entries = 0
    in_fence = False
    in_history = False
    section = "(top)"
    for idx, line in enumerate(lines):
        lineno = idx + 1
        if lineno <= fm_end:
            continue
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue

        h = HEADING_RE.match(line)
        if h:
            title = h.group(2).strip()
            if len(h.group(1)) <= 3:
                section = title
            if title.lower().startswith(DATED_LOG_SECTIONS):
                in_history = True
            elif len(h.group(1)) <= 2:
                in_history = False
            if in_history and len(h.group(1)) >= 3:
                history_entries += 1
            continue

        if in_history:
            # `- **YYYY-MM-DD** — ...` is the §6 form; bare and italic dates are
            # tolerated so older files still get counted toward the bound.
            if re.match(r"^\s*[-*]\s+[*_]{0,2}\d{4}-\d{2}-\d{2}", line):
                history_entries += 1
            continue

        total += count_words(line)
        if TABLE_ROW_RE.match(line):
            continue
        prose.append((lineno, stripped, section))
    return total, prose, history_entries


# A "distinctive term" is something a reader would recognise as the same fact:
# a proper noun, an acronym or ticket id, a percentage, or a date fragment.
TERM_RES = [
    re.compile(r"\b[A-Z][a-z]{3,}\b"),            # Atlas, Channels, Collections
    re.compile(r"\b[A-Z]{2,}[A-Z0-9-]*\b"),       # PROJ-3321, SRE, CMS
    re.compile(r"\b\d+%"),                        # 15%
    re.compile(r"\b\d{1,2}/\d{1,2}\b"),           # 9/7
]
# Capitalised words that are almost always sentence-initial prose or generic org
# vocabulary rather than a specific fact. Without this the check drowns in noise.
TERM_STOP = set("""this that these those there their they them then when where what which while
with without after before because being been have has had here however since such than that's
your yours you'll about above across against among around during into over under again both each
more most other some only same very just also first second third next last need needs
january february march april june july august september october november december
one two three four five six seven eight nine ten eleven twelve
product program team teams engineering design weekly monthly quarterly sync review meeting
work note notes update updates status current open closed pending active
decision decisions risk risks owner owners ownership goal goals
what where when which while still also only just even
""".split())

# Acronyms that are ambient org vocabulary, not a fact being restated.
TERM_STOP_UPPER = set("PM PMO SVP VP EM UX QA API CMS SRE PRD TPM HR IC EOD EOW TBD OOO".split())


def operator_tokens():
    """The vault owner's own name, from CLAUDE.md frontmatter `operator:`.

    The owner is named in nearly every artifact by definition, so their name is
    never evidence of a repeated fact. Read rather than hardcoded — a hardcoded
    name silently does nothing in anyone else's vault."""
    try:
        with open("CLAUDE.md", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except Exception:
        return set()
    if not lines or lines[0].strip() != "---":
        return set()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"operator\s*:\s*(.+)$", line)
        if m:
            # The value may be plain (Jordan Reyes) or a quoted wikilink
            # ("[[Jordan Reyes]]") — the setup wizard emits the latter. Strip
            # quotes and brackets before splitting, or the tokens come out as
            # "[[jordan" and "reyes]]" and match nothing.
            name = re.sub(r"[\[\]\"']", " ", m.group(1)).strip()
            return set(t.lower() for t in re.split(r"[\s._-]+", name) if len(t) > 1)
    return set()


TERM_STOP |= operator_tokens()

MIN_REPEAT_SECTIONS = 5
MIN_REPEAT_LINES = 6


def distinctive_terms(text, exclude=()):
    out = set()
    for rx in TERM_RES:
        for m in rx.finditer(text):
            t = m.group(0)
            low = t.lower()
            if low in TERM_STOP or t in TERM_STOP_UPPER or low in exclude:
                continue
            out.add(t)
    return out


def subject_tokens(path):
    """Tokens naming what the artifact is *about* — the 1:1 counterpart, the program,
    the meeting. These recur by definition and are not repetition defects."""
    stem = os.path.basename(path)[:-3].lower()
    stem = re.sub(r"^\d{6}-", "", stem)
    parts = re.split(r"[-_\s]+", stem)
    parts += re.split(r"[/\\]", os.path.dirname(path).lower())
    return set(p for p in parts if len(p) > 2)


def check_output_contract(path, lines, fm_end):
    """Deterministic checks from .cosmos/instructions/output-contract.md."""
    findings = []
    type_name, cap = artifact_type(path)
    words, prose, history_entries = body_analysis(lines, fm_end)

    # §1 word cap
    if cap is not None and words > cap:
        findings.append((1, "ERROR", "word-cap",
                         "{} body is {} words, cap is {} ({} over)".format(
                             type_name, words, cap, words - cap)))

    # §6 bounded history
    limit = MAX_HISTORY_ENTRIES_PERSON if type_name == "person" else MAX_HISTORY_ENTRIES
    if history_entries > limit:
        findings.append((1, "WARN", "history-unbounded",
                         "dated log has {} entries, keep {} and archive the rest".format(
                             history_entries, limit)))

    # §8 no trailing Linked Artifacts section
    for idx, line in enumerate(lines):
        if idx + 1 <= fm_end:
            continue
        h = HEADING_RE.match(line)
        if h and h.group(2).strip().lower().startswith("linked artifacts"):
            findings.append((idx + 1, "ERROR", "linked-artifacts",
                             "'## Linked Artifacts' re-lists links already in frontmatter and body — remove it"))

    # §4 placeholders, §2 sentence length, §3 banned phrases
    in_fence = False
    for idx, line in enumerate(lines):
        lineno = idx + 1
        if lineno <= fm_end:
            continue
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue

        for rx, label in PLACEHOLDER_LINE_RES:
            if rx.match(line):
                findings.append((lineno, "ERROR", "placeholder",
                                 "{} — omit the line or the section instead".format(label)))
                break

        low = CODESPAN_RE.sub(" ", stripped).lower()
        for phrase in BANNED_PHRASES:
            if phrase in low:
                findings.append((lineno, "ERROR", "banned-phrase",
                                 "hedge/filler '{}' — state the finding directly".format(phrase)))
        for word in BANNED_WORDS:
            if re.search(r"\b" + word + r"\b", low):
                findings.append((lineno, "ERROR", "banned-phrase",
                                 "hedge '{}' — state the finding, or label it Confidence: Low".format(word)))
        for phrase in TREND_PROSE:
            if phrase in low:
                findings.append((lineno, "ERROR", "trend-prose",
                                 "'{}' — use the 5-state enum (New/Increasing/Stable/Decreasing/Resolved)".format(phrase)))

    # §2 sentence length, on prose only
    for lineno, text, _section in prose:
        body = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", text)
        body = re.sub(r"^>\s*", "", body)
        for sent in split_sentences(body):
            n = count_words(sent)
            if n > MAX_SENTENCE_WORDS:
                findings.append((lineno, "ERROR", "sentence-length",
                                 "sentence is {} words, max is {} — split it".format(
                                     n, MAX_SENTENCE_WORDS)))

    # §5a near-duplicate sentences (literal restatement)
    cands = []
    for lineno, text, _section in prose:
        for sent in split_sentences(text):
            cw = content_words(sent)
            if len(cw) >= 6:
                cands.append((lineno, sent, cw))
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i][2], cands[j][2]
            union = len(a | b)
            if union and len(a & b) / float(union) >= 0.5:
                findings.append((cands[j][0], "WARN", "repeated-content",
                                 "restates line {} in different words — state it once, embed it elsewhere".format(
                                     cands[i][0])))
                break

    # §5b the same fact re-derived across sections. This is the dominant bloat
    # mechanism and it is invisible to text-similarity: the wording differs every
    # time, but the distinctive terms do not. A term carried through four or more
    # sections means one fact is being retold at four altitudes.
    subject = subject_tokens(path)
    term_sections = {}
    term_lines = {}
    for lineno, text, section in prose:
        for term in distinctive_terms(text, exclude=subject):
            term_sections.setdefault(term, set()).add(section)
            term_lines.setdefault(term, []).append(lineno)
    for term, sections in sorted(term_sections.items()):
        if len(sections) >= MIN_REPEAT_SECTIONS and len(term_lines[term]) >= MIN_REPEAT_LINES:
            findings.append((term_lines[term][0], "WARN", "repeated-fact",
                             "'{}' appears in {} sections ({} lines) — detail it once, embed or link it elsewhere".format(
                                 term, len(sections), len(term_lines[term]))))

    return findings


def lint_file(path, pathset, names, errors_only, contract_scope=True):
    findings = []
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    # Frontmatter span.
    fm_end = -1
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_end = i
                break

    in_fence = False
    for idx, line in enumerate(lines):
        lineno = idx + 1
        stripped = line.strip()

        # Fenced code block toggle (skip contents for all checks).
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        in_frontmatter = 0 < lineno <= fm_end

        # --- frontmatter: wikilinks must be quoted ---
        if in_frontmatter:
            if "[[" in line and '"[[' not in line and "'[[" not in line:
                findings.append((lineno, "ERROR", "frontmatter-quote",
                                 "wikilink in frontmatter must be wrapped in quotes"))
            continue  # don't run body checks on frontmatter lines

        # --- table must be preceded by a blank line ---
        # Fires on the first row of a table only (predecessor isn't itself a table row).
        if TABLE_ROW_RE.match(line):
            prev = lines[idx - 1] if idx > 0 else ""
            if prev.strip() and not TABLE_ROW_RE.match(prev) and not TABLE_OK_PREV_RE.match(prev):
                findings.append((lineno, "ERROR", "table-blank-line",
                                 "table row not preceded by a blank line — Obsidian renders it as raw text"))

        # Separate inline code spans from prose.
        code_spans = CODESPAN_RE.findall(line)
        prose = CODESPAN_RE.sub(" ", line)

        # --- bare vault file path in a code span ---
        for span in code_spans:
            if looks_like_vault_file(span):
                findings.append((lineno, "ERROR", "bare-path",
                                 "`{}` is a vault file path in a code span — use a wikilink".format(span.strip())))

        # --- wikilink resolution (prose only) ---
        for m in WIKILINK_RE.finditer(prose):
            target = strip_target(m.group(1))
            if not target:
                continue
            if "/" in target:
                if target not in pathset:
                    if os.path.isdir(target):
                        findings.append((lineno, "ERROR", "wikilink-resolves",
                                         "[[{}]] is a folder, not a file — link a specific file or use a code span".format(m.group(1))))
                    else:
                        findings.append((lineno, "ERROR", "wikilink-resolves",
                                         "[[{}]] does not resolve to an existing file".format(m.group(1))))
            else:
                if target.lower() not in names:
                    findings.append((lineno, "WARN", "wikilink-basename",
                                     "[[{}]] resolves to no file or alias in the vault".format(m.group(1))))

        # --- scope-rule narration (WARN) ---
        if not any(r.search(line) for r in METADATA_SKIP_RES):
            for nr in NARRATION_RES:
                m = nr.search(prose)
                if m:
                    findings.append((lineno, "WARN", "scope-narration",
                                     "cosmos-internal reference '{}' in a work artifact — review (may be legitimate metadata)".format(m.group(0))))
                    break

    if contract_scope:
        findings.extend(check_output_contract(path, lines, fm_end))

    if errors_only:
        findings = [f for f in findings if f[1] == "ERROR"]
    return sorted(findings, key=lambda f: (f[0], f[1]))


def print_stats(targets):
    rows = []
    for path in targets:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        fm_end = -1
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    fm_end = i
                    break
        type_name, cap = artifact_type(path)
        words, _, _ = body_analysis(lines, fm_end)
        rows.append((path, type_name or "-", words, cap))
    rows.sort(key=lambda r: (r[3] is not None and r[2] > r[3], r[2]), reverse=True)
    print("{:<62} {:<16} {:>6} {:>6} {:>6}".format("FILE", "TYPE", "WORDS", "CAP", "OVER"))
    for path, tname, words, cap in rows:
        over = "" if cap is None else (str(words - cap) if words > cap else "ok")
        print("{:<62} {:<16} {:>6} {:>6} {:>6}".format(
            path[-62:], tname, words, cap if cap is not None else "-", over))


def main(argv):
    args = list(argv[1:])
    as_json = "--json" in args
    errors_only = "--errors-only" in args
    stats = "--stats" in args
    for f in ("--json", "--errors-only", "--stats"):
        if f in args:
            args.remove(f)

    targets = collect_targets(args)

    if stats:
        print_stats(targets)
        return 0

    pathset, names = build_vault_index()

    # An explicitly-named target always gets the full output-contract check; a bare
    # sweep applies it to live state only (see LIVE_PREFIXES).
    explicit = set(os.path.normpath(t).replace(os.sep, "/") for t in targets) if args else set()

    all_findings = {}
    n_err = n_warn = 0
    for path in targets:
        fnd = lint_file(path, pathset, names, errors_only,
                        contract_scope=in_contract_scope(path, explicit))
        if fnd:
            all_findings[path] = fnd
            for _, sev, _, _ in fnd:
                if sev == "ERROR":
                    n_err += 1
                else:
                    n_warn += 1

    if as_json:
        out = {"files": {p: [{"line": ln, "severity": sv, "check": ck, "message": msg}
                             for (ln, sv, ck, msg) in f] for p, f in all_findings.items()},
               "errors": n_err, "warnings": n_warn, "files_scanned": len(targets)}
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 1 if n_err else 0

    for path in sorted(all_findings):
        for (ln, sev, ck, msg) in all_findings[path]:
            print("{}:{}: [{}] {}: {}".format(path, ln, sev, ck, msg))
    print("")
    print("Scanned {} file(s): {} error(s), {} warning(s).".format(len(targets), n_err, n_warn))
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
