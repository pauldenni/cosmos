# cosmos Canonical Naming Rules

cosmos uses canonical names so every generated note can link cleanly inside Obsidian.

The goal is to prevent duplicate graph nodes like:

- `[[Bridge]]`
- `[[bridge]]`
- `[[The Bridge Program]]`
- `[[Bridge Initiative]]`

Use one canonical name for each operational entity and reuse it everywhere.

---

# Core Rule

If an entity is persistent, link it with an Obsidian wikilink using its canonical name.

Use:

```md
[[Canonical Name]]
```

Do not use plain text when the entity exists or should exist as a note.

---

# Entity Types

cosmos should treat the following as first-class entities:

- people
- programs
- systems
- domains
- teams
- meetings
- risks
- decisions
- recurring artifacts

---

# Canonical Naming by Entity Type

## People

Use the person's first name when there is no ambiguity.

Examples:

```md
[[Beverly]]
[[Worf]]
[[Tasha]]
[[Dan]]
[[Eve]]
[[Deanna]]
[[Picard]]
```

Use full name only when ambiguity exists or when the person is external / less frequently referenced.

Example:

```md
[[Director Name]]
```

Do not mix short and full names for the same person.

Choose once and reuse everywhere.

---

## Programs

Use Title Case.

Examples:

```md
[[Atlas]]
[[Bridge]]
[[Helios Migration]]
[[Rollout]]
[[Personalization]]
[[Search]]
[[Curation]]
```

Avoid variants like:

```md
[[atlas]]
[[Atlas Rollout Program]]
[[The Bridge Initiative]]
```

unless those are truly separate programs.

---

## Systems

Use the canonical system/product/platform name.

Examples:

```md
[[Legacy CMS]]
[[Search Service]]
[[Content API]]
[[Platform UI]]
```

Prefer the name people actually use in meetings.

Do not create alternate spellings unless the distinction matters.

---

## Domains

Use Title Case.

Examples:

```md
[[Content Modeling]]
[[Ingest & Publishing]]
[[Editorial Tools]]
[[Live & Video]]
[[Search & Discovery]]
[[Personalization & Recommendations]]
[[Platform APIs]]
[[Platform Health]]
```

Domains describe ownership areas, not individual projects.

---

## Teams

Use the team's common display name.

Examples:

```md
[[Alpha]]
[[Beta]]
[[Gamma]]
[[Delta]]
[[PMO]]
[[Product]]
[[Design]]
[[Engineering]]
```

---

## Meetings

Use stable, recognizable meeting names in Title Case.

Examples:

```md
[[Weekly Product Sync]]
[[PMO Product Engineering Sync]]
[[Atlas Product & Design Sync]]
[[Atlas Curation Weekly Sync]]
[[Atlas Scrum of Scrums]]
[[Cross-System Sync]]
```

Do not include dates in meeting entity names.

Dated meeting notes can still include dates in filenames, but the meeting entity should remain stable.

---

## Risks

Default to kebab-case when Claude creates a new risk file. Human-named risks can use any readable format — the rule is that the wikilink target must match the filename on disk exactly.

Examples (default form):

```md
[[cross-team-friction]]
[[beverly-overload-risk]]
[[rollout-sequencing-risk]]
[[asset-permissions-alignment-risk]]
[[single-threaded-ownership-risk]]
```

Risk names should be:
- stable
- specific
- reusable over time
- not overly verbose

Avoid only when truly ambiguous or unstable:

```md
[[Risk around Beverly being overloaded again]]
[[bridge risk 5-6-26]]
```

---

## Decisions

Default to kebab-case when Claude creates a new decision file. Human-named decisions can use any readable format — the rule is that the wikilink target must match the filename on disk exactly.

Examples (default form):

```md
[[asset-permissions-model]]
[[entity-migration-approach]]
[[site-assignment-rollout-sequencing]]
[[asset-scope-shared-vs-platform-specific]]
```

Decision names should describe the decision topic, not the final answer.

Avoid date-stamping decision names unless there are multiple distinct decision events.

---

## Recurring Artifacts

Use stable names for living artifacts.

Examples:

```md
[[Leadership Dashboard]]
[[Org Health]]
[[Ownership Map]]
[[Executive Brief]]
```

When referencing actual files, prefer wikilinks to the note title.

---

# Frontmatter Rules

Use wikilinks as strings in frontmatter.

Example:

```yaml
type: risk
status: active
severity: high
trend: increasing
owner: "[[Beverly]]"
program: "[[Bridge]]"
systems:
  - "[[Legacy CMS]]"
  - "[[Content API]]"
related_decisions:
  - "[[asset-permissions-model]]"
```

For multiple values, use YAML lists:

```yaml
owners:
  - "[[Beverly]]"
  - "[[Worf]]"
programs:
  - "[[Atlas]]"
  - "[[Bridge]]"
```

---

# Link Display Rules

Use aliases when the sentence needs more readable text.

Example:

```md
[[beverly-overload-risk|Beverly overload risk]]
```

Use aliases sparingly.

The canonical target should remain stable.

---

# File Location Recommendations

Recommended folders:

```txt
people/
people/teams/
work/programs/
work/risks/
work/decisions/
work/goals/
work/meetings/
reference/systems/
reference/domains/
```

Entity notes should live in the matching folder.

Example:

```txt
people/Beverly.md
work/programs/Bridge.md
reference/systems/Legacy CMS.md
reference/domains/Content Modeling.md
people/teams/Beta.md
work/meetings/Weekly Product Sync.md
work/risks/cross-team-friction.md
work/decisions/asset-permissions-model.md
```

---

# Naming Decision Rules

When Claude is unsure what canonical name to use:

1. Prefer an existing note name if one exists.
2. Prefer the term used most often in source material.
3. Prefer shorter stable names over long descriptive names.
4. Avoid creating multiple names for the same entity.
5. If ambiguity remains, create a clear canonical note and list aliases inside it.

---

# Alias Handling

If alternate names exist, capture them in the entity note frontmatter.

Example:

```yaml
aliases:
  - Bridge Program
  - Cross-System Bridge
  - PTV Bridge
```

This allows Obsidian to resolve alternate references while preserving a canonical note.

---

# Canonical Entity Index

Maintain an index at:

```txt
.cosmos/instructions/canonical-entity-index.md
```

This file should list canonical names for people, programs, systems, domains, teams, meetings, risks, and decisions.

Claude should check this index before inventing new entity names.

---

# Command Behavior

All cosmos commands should:

- use canonical wikilinks for persistent entities
- check existing notes and the canonical index before creating new names
- avoid duplicate graph nodes
- create new canonical names only when needed
- add aliases when source material uses alternate names
- preserve canonical names once established

---

# Examples

## Bad

```md
Beverly is still carrying too much Bridge context.
```

## Good

```md
[[Beverly]] is still carrying too much [[Bridge]] context.
```

---

## Bad

```md
Linked risk: bridge friction risk
```

## Good

```md
Linked risk: [[cross-team-friction]]
```

---

## Bad

```yaml
owner: Beverly
program: bridge
```

## Good

```yaml
owner: "[[Beverly]]"
program: "[[Bridge]]"
```
