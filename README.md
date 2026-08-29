# cosmos

An AI-assisted Chief of Staff operating system for leaders and operators, running on Claude Code inside an Obsidian vault.

This is a **fresh v2 install** — the full operating system with no content. Every folder is empty and waiting.

---

## The loop

**You write → `/sync` propagates → `/now`, `/prep`, `/brief`, `/scan` consume.**

You write notes anywhere in the vault. The file existing is the signal. `/sync` reads what you wrote plus your configured sources, distills, and updates persistent state — it is the only command that writes persistent state. Everything else reads it and produces its own artifact.

| Command | Does |
|---|---|
| `/now` | Orient in under two minutes. Calendar, inbox, work state, home state. |
| `/sync` | Propagate signal into persistent state. Run 2–3× daily. |
| `/prep <thing>` | Prepare for a 1:1, meeting, reflection, or planning cycle. |
| `/brief <level>` | Upward output — `vp`, `svp`, `short`. |
| `/scan <mode>` | Internal diagnostic — `risks`, `team`, `patterns`, `retro`, `program`, `life-patterns`. |

---

## What's in here

```
CLAUDE.md                     the operating instructions Claude loads automatically
.claude/commands/             the 5 commands
.claude/skills/               6 skills — deterministic Python, not prose
.cosmos/instructions/         rules the commands reference
.cosmos/hooks/                write-logger
reference/templates/          33 output templates
reference/org/                PM career ladder + calibration template
```

### The skills

Everything error-prone or deterministic is a script, not an instruction. This is deliberate: prose instructions produce different results every run.

| Skill | Settles |
|---|---|
| `cosmos-scheduler` | What should run now, and prep for which meetings |
| `cosmos-artifact-linter` | Word caps, sentence length, placeholders, repeated facts |
| `sync-freshness` | Is state stale for this prep? |
| `cadence-status` | Which cadences are overdue |
| `inbox-archive-tabulation` | Which inbox notes are safe to archive |
| `canonical-entity-index` | The entity name index, rebuilt from disk |

---

## Setup

### 1. Open it

Open this folder as an Obsidian vault, and open it in Claude Code. `CLAUDE.md` loads automatically.

### 2. Tell it who you are

Edit the YAML frontmatter at the top of `CLAUDE.md` — your name, role, org, chain, team, programs, systems, domains. That frontmatter seeds the entity index.

Then:

```bash
python3 .claude/skills/canonical-entity-index/rebuild_index.py --write
```

### 3. Add your sources

Edit `.cosmos/instructions/primary-sources.md`. It ships empty with the format documented. Add the documents where decisions actually get made — a doc nobody updates is a liability, not a source.

Requires the Google Drive and/or Atlassian connectors. Without them, `/sync` still works on inbox and journal signal alone.

### 4. Start writing

Drop notes in `inbox/`. Run `/sync`. That's the whole ritual.

---

## The output contract

`.cosmos/instructions/output-contract.md` is the authority on length and style, and it wins over any command file or template.

It exists because of a measured failure. In the vault this was extracted from, artifacts had grown 4–10× too long: a 30-word ask restated six times across six sections of one 1:1 prep, a "dashboard" at 4,048 words, a program file that was 88% changelog. The cause was structural — every template had 6–13 mandatory sections and no word budget, so **length tracked template shape rather than how much actually happened**.

What the contract enforces:

- **Hard word caps** per artifact type. 1:1 prep 400, dashboard 600, brief 150–400, scan 600, `/now` 250.
- **25-word sentences.** One idea each.
- **Empty sections are correct.** Never invent content to fill a template. Never emit a placeholder `-`.
- **One canonical wording.** Every risk, decision, and program carries a `## Line` — one ≤25-word sentence. Everything else embeds `![[work/risks/x#Line]]` rather than re-deriving it in fresh words.
- **Bounded history.** `## History` keeps 4 dated entries; older ones move to `archive/`.

The linter makes this real:

```bash
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py --errors-only
python3 .claude/skills/cosmos-artifact-linter/lint_artifacts.py --stats
```

Caps are tunable in that one file. Raise one for a pure *enumeration* whose length tracks org size, not wordiness — never just because prose ran long.

---

## Automation (optional)

Two desktop scheduled tasks can run the loop for you:

- **morning** — sync if due → prep today's meetings → `/now`
- **evening** — sync if due → prep *tomorrow's* meetings → run overdue scans / weekly reflection

Prep the night before is what covers mornings that are booked solid from 09:00.

Ask Claude to create them, pointing at these scripts:

```bash
python3 .claude/skills/cosmos-scheduler/whats_due.py          # is /sync actually due?
python3 .claude/skills/cosmos-scheduler/resolve_meetings.py   # calendar -> routed prep work order
python3 .claude/skills/cosmos-scheduler/list_sources.py       # the pre-flight listing
```

`/sync` is **signal-triggered, not clock-triggered** — due when something is newer than the last sync, with an age backstop. A clock-based rule fires when nothing changed and stays quiet right after you write three notes.

### Four things that will bite you

Learned the hard way; all four are already handled in this install.

1. **Never let a task improvise shell commands.** A command containing shell expansion (`for d in journal/scans/*/`) can only ever be granted *"allow once"* — Claude Code will not write a persistent permission rule for it, so an unattended run stalls forever on a prompt nobody is awake to answer. That's why the pre-flight listing is `list_sources.py` and not a prose instruction.

2. **Pin the model per task.** Scheduled tasks default to whatever your account default is, often Sonnet. `model:` in a task's `SKILL.md` is **silently ignored**. Set it in the task's Edit form in the UI. `/sync` is cross-entity synthesis under a word contract — model quality shows.

3. **Pre-approve the tools.** Run each task manually once and choose "always allow". Approvals persist on the task.

4. **claude.ai connectors can't go in `.mcp.json`.** Google Calendar/Drive/Gmail and Slack are account-level connectors, not Claude Code MCP servers. They are unreachable from headless `claude -p` — even with `claude setup-token`, which explicitly cannot fetch them. In-app scheduled tasks *can* reach them. That is why the automation runs in the app rather than from cron.

### Scripts resolve their own root

Every bundled script derives the vault path from its own location, not `cwd`. A `cwd`-relative default fails **silently** under a scheduled task — `people/` and `work/meetings/` come back empty, so every meeting lands in "unrouted" and it looks like a real answer. Keep it that way if you add scripts.

---

## Scope rule

cosmos is the system you use to do your work. It is not the work.

Artifacts describe your actual work — programs, people, risks, decisions. They never narrate cosmos itself: not its commands, not its discipline rules, not its failures. Freshness stamps and cadence tables are metadata and stay. "Tracked by cosmos" is narration and goes.

The test: would this sentence make sense to a successor who inherited your role but not your cosmos?
