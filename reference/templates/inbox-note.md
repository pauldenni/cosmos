---
type: inbox-note
status: active # active | complete | archived
note-type: observation
date: <% tp.date.now("YYYY-MM-DD") %>
source:
save-source: false
supersedes_source: false
owner: ""
programs: []
systems: []
domains: []
people: []
related_risks: []
related_decisions: []
related_updates: []
meetings: []
tags:
  - inbox
---
<% tp.file.rename(tp.date.now("MMDDYY") + "-" + tp.file.title) %>

<!--
No word cap — this is raw human capture, not synthesized output. The caps in
.cosmos/instructions/output-contract.md apply to what cosmos writes, not to what
you type here. Write as long or as short as the observation deserves.

The empty `- [ ]` under Follow-Up Needed is a typing target, not a placeholder —
the inbox-archive-tabulation skill reads an unchecked box with no text as
unfilled and does not treat it as a blocking task. An unchecked box WITH text
holds this note in the inbox until you check it or set `status: complete`.

Set `domains: [Home]` to route this note to home/ persistent state instead of
work/.
-->

## What I Observed / Learned

## Follow-Up Needed

- [ ] 

## Linked Notes

```dataview
TABLE file.mtime AS "Last Edited"
FROM [[]]
WHERE file.name != this.file.name
SORT file.mtime DESC
```
