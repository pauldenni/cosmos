# Obsidian Linking Rules

All references to persistent operational entities MUST use Obsidian wikilinks.

Use wikilinks for:
- people
- programs
- systems
- domains
- teams
- meetings
- risks
- decisions
- persistent operational artifacts

Examples:
- `[[Director Name]]`
- `[[Alice]]`
- `[[Bob]]`
- `[[Carol]]`
- `[[Dan]]`
- `[[Atlas]]`
- `[[Bridge]]`
- `[[Helios Migration]]`
- `[[Rollout]]`
- `[[Legacy CMS]]`
- `[[Search Service]]`
- `[[Content API]]`
- `[[Weekly Product Sync]]`
- `[[PMO Product Engineering Sync]]`
- `[[cross-team-friction]]`
- `[[alice-overload-risk]]`
- `[[asset-permissions-model]]`

Do NOT use plain-text references when a persistent entity exists or should exist.

When creating new persistent operational artifacts, choose stable canonical names so future notes can link to them consistently.

Recommended naming:
- People: `[[First Name]]` or `[[Full Name]]` when ambiguity exists
- Programs: Title Case, such as `[[Bridge]]`
- Systems: canonical system name, such as `[[Legacy CMS]]`
- Risks: default to kebab-case, such as `[[cross-team-friction]]`
- Decisions: default to kebab-case, such as `[[asset-permissions-model]]`

When a file already exists on disk with a different format, wikilinks must match the filename exactly — follow the file, do not normalize.

Operational artifacts should form a navigable graph inside Obsidian.

When adding frontmatter references, use wikilinks as strings:

```yaml
owner: "[[Alice]]"
program: "[[Bridge]]"
related_risks:
  - "[[cross-team-friction]]"
linked_decisions:
  - "[[asset-permissions-model]]"
```
