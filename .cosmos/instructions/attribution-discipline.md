# Attribution Discipline

Shared rules for deciding **who owns what** during synthesis. Referenced by
`/sync` and `/prep` (and applicable to `/brief` and `/scan`). Goal: never
manufacture ownership by the operator's team/domain where it doesn't exist, and
never under-capture ownership on forums the operator's team genuinely owns.

## Core principle

A topic appearing in a meeting, doc, or thread is **not** evidence that the
operator's team owns it. Before attributing an owner, decision, or action item
to the operator or their team, require at least one of:

- a system or deliverable owned by the operator's team is **directly named**, or
- a person on the operator's team is named as the owner/actor, or
- the operator **explicitly captures** it as their team's item in notes.

If none hold, treat the item as **awareness / cross-team**, and when it might
matter, flag it `possible relevance — confirm` rather than asserting ownership.
Do not invent an owner, and do not recommend names from the operator's team for
work that isn't theirs.

Equally, on forums the operator's team owns: **do not hedge.** Attribute owned
decisions and action items confidently. Under-attribution on a forum the
operator owns is as wrong as over-attribution on a cross-team one.

## Meeting attendance posture

Each `work/meetings/<meeting>.md` entity may carry a `## My Role / Attendance
Posture` block describing the operator's role in that meeting and explicit
synthesis guidance (informational vs. owned vs. mixed). **Consult it before
attributing anything drawn from that meeting.**

- **Note → entity by folder:** a `journal/meetings/<folder>/` note maps to the
  meeting entity whose `journal_path` is `<folder>`. (The `meeting:` frontmatter
  value is an unreliable join key — formats vary; use the folder, falling back
  to `meeting` / `aliases` / filename.)
- **Primary source → entity by `source:`** URL or name match against the entity.
  If matched, apply that entity's posture to attribution from that source.
- Apply the posture's synthesis guidance to every ownership / decision /
  action-item call drawn from that meeting's notes or source.

If a meeting has no posture block, fall back to the core principle above.
