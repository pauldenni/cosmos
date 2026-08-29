# /now

Orientation command. Run it anytime — first thing in the morning, after a long meeting block, coming back from travel, or whenever your brain is scattered and you can't figure out where to put your energy.

**This is the prosthetic.** It does the synthesis your brain doesn't always do automatically: pattern detection, cross-domain connection, ruthless prioritization. Read it in under 2 minutes. Then act.

No modes. No arguments. Just `/now`.

---

## What It Produces

A single compact artifact covering six things:

1. **Where You Are** — temporal grounding + today's calendar + near horizon
2. **The One Thing** — the single most critical professional reality right now
3. **What's Hot** — top 3 work items + top 2 personal items, action-framed
4. **The Connection** — cross-domain synthesis: what your brain isn't linking between work and personal life
5. **What's Slipping** — the one thing gone quiet
6. **Today's Move** — one action, imperative, specific

---

## Sources (read in this order)

1. **Google Calendar** — today's events via Calendar MCP (`mcp__689a26c9-3713-4a19-a9c5-79f900539ddb__list_events`). Fetch accepted + organized events for today. Note tentative events separately. Ignore declined.
2. **`inbox/*.md`** — all active notes (work and home domain)
3. **`work/dashboard.md`** — current work state and cadence
4. **`work/risks/*.md`** — all active risk files
5. **`work/programs/*.md`** — all active program files
6. **`work/decisions/*.md`** — all pending decisions
7. **`home/dashboard.md`** — current personal life state
8. **`home/areas/*.md`** — all life area files
9. **`home/goals/*.md`** — active personal goals
10. **`home/intentions/*.md`** — active intentions (if any)
11. **`journal/personal/life-reflect/`** — most recent life-reflect file (if any)
12. **`journal/personal/weekly-reflection/`** — most recent work reflect file (if any)
13. **`journal/personal/daily/`** — most recent prior `/now` file — what was flagged last time that's still unresolved?

**Do not read:** meeting notes, briefs, scans, primary sources (Google Docs, Confluence). Those are too detailed. `/now` synthesizes from persistent state files, calendar, inbox, and reflects only.

---

## Synthesis Instructions

### Where You Are

Temporal grounding — where are you in the week, sprint, or quarter? Name the near horizon (what matters in the next 3–7 days). Include 2–3 of today's most relevant calendar events (time + title). One line of personal context if relevant (trip this weekend, something significant at home).

**3–4 lines total. No more.**

---

### The One Thing

The single most critical professional reality right now. Not a list. Not "a few things to consider." One thing — the risk, decision, milestone, or dependency that has the highest consequence if not addressed.

- Name it specifically
- Say why it matters (one sentence)
- Say what needs to happen **today** because of it, if anything

**Maximum 3 sentences.**

**How to pick it:**
- Highest-severity active risk with unresolved leadership need
- OR most time-sensitive decision pending (past its needed-by date, or needed this week)
- OR program milestone at highest risk in the next 14 days
- When two things tie: pick the one where the operator has the most ability to influence today

---

### What's Hot

Work items (max 3) and personal items (max 2). **Action-framed — not status.** Not "Meridian is at risk" — "Meridian dogfooding issues need a scope decision this week."

Each item is one line: what's happening — what action it requires and when.

Only surface items where action is needed within the next 3–5 days. If something is stable and no decision or action is needed, omit it.

```
**Work**
- [item] — [action needed, by when if relevant]

**Personal**
- [item] — [action or what to notice]
```

---

### The Connection

**This is the most important section and the reason this command exists.**

Cross-domain synthesis. The non-obvious link between the personal and professional domains — the one the brain doesn't make automatically. Pick ONE connection and name it directly.

**What to look for:**

- **Energy transfer:** Personal health, sleep quality, or stress patterns that are likely degrading professional performance right now — or will soon
- **Time displacement:** Work demands creating gaps in personal life that are starting to compound
- **Correlated neglect:** Things slipping in both domains simultaneously — what does that pattern suggest?
- **Opportunity alignment:** A personal intention that could be acted on given current work conditions — or vice versa
- **Consequence preview:** Something true now that will matter in 2–3 weeks if not acknowledged

Name it. Specifically. Not "work stress is affecting personal life" — that's noise. "The Meridian pressure over the last three weeks maps exactly to the drop in your personal cadence. This isn't a coincidence — it's a pattern. The next thing to drop will be relationships, not creative." That's signal.

**Be honest. Name it even if it's uncomfortable. That is why this section exists.**

**2–4 sentences maximum.**

---

### What's Slipping

The one thing that has gone quiet. Not the most urgent thing — the most *neglected*. Could be work or personal.

**Where to look:**
- Risk files with no History entry in >14 days while still marked active/unresolved
- Decisions past their needed-by date with no movement recorded
- Life areas with no inbox signal in >2 weeks
- Goals (work or personal) with no trajectory update in >2 weeks
- The most recent prior `/now` file — was something called out there that's *still* unaddressed?
- Overdue cadence rows in `work/dashboard.md` or `home/dashboard.md`

Name it without judgment. Present it as information: "X hasn't moved in N days." No shame. Just the fact.

**1–2 sentences.**

---

### Today's Move

One action. Not a list. The single highest-leverage thing available today — work or personal.

Write it as a **direct imperative sentence**. Starts with a verb. Specific enough to act on without rereading anything.

Not: "You might want to reach out to Dana about the entitlements decision."
Yes: "Send Dana the entitlements decision framing by EOD — it's been waiting on you for 8 days."

The move should be:
- Specific (names a person, decision, file, or action)
- Completable today
- Connected to either The One Thing or What's Slipping

---

## Voice Rules (non-negotiable)

Every `/now` output must follow these. They are not style preferences.

These extend `.cosmos/instructions/output-contract.md`, which sets the hedge ban, the 25-word sentence cap, and the no-placeholder rule for every artifact. `/now` adds:

1. **Cap: 250 words.** If the output runs long, cut — do not summarize.
2. **The Connection must be specific.** Name the pattern, the evidence, and the consequence. A vague cross-domain observation is not synthesis.
3. **Today's Move is imperative.** Starts with a verb. Ends with enough specificity to act on.
4. **No padded sections.** If nothing is slipping, write "Nothing in critical neglect right now." One line. Do not invent something.
5. **No executive framing.** This is a brain reload, not a briefing. Write to the operator as a person.
6. **Respect the Scope rule in `CLAUDE.md`.** `/now` orients the operator to their life and work, never to cosmos's own state.

---

## Output

Print the artifact directly to chat. Write it simultaneously to `journal/personal/daily/MMDDYY-now.md`. Do not print a "writing file..." message — write silently. After the artifact, add one line:

```
↳ saved to journal/personal/daily/MMDDYY-now.md
```

If a `/now` file already exists for today, **refresh it in place** — do not create a duplicate. The refreshed version reflects the current moment.

**Folder creation:** If `journal/personal/daily/` does not exist, create it before writing.

### Output template:

```markdown
---
type: now
date: YYYY-MM-DD
time: HH:MM
tags:
  - now
  - daily
---

# /now — [Weekday], [Month DD]

## Where You Are
[3–4 lines: week/sprint context, near horizon, today's calendar, any personal context]

## The One Thing
[2–3 sentences: what, why it matters, what to do today because of it]

## What's Hot
**Work**
- [item] — [action, timing]
- [item] — [action, timing]
- [item] — [action, timing]

**Personal**
- [item] — [action or notice]

## The Connection
[2–4 sentences. The cross-domain link. Specific. Honest.]

## What's Slipping
[1–2 sentences. The quiet neglect. No judgment.]

## Today's Move
> [One imperative sentence.]

---
*Sources: calendar · work state · home state · reflects*
```

---

## Output path

```
/now    →    journal/personal/daily/MMDDYY-now.md
```
