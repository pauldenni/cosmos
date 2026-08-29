# Primary Sources

The highest-signal documents `/sync` pulls from. Read this file at the start of a `/sync` run.

**This file starts empty. Add your own sources below.** Until you do, `/sync` runs on inbox and journal signal only, which works — the primary sources are what make it see beyond what you personally wrote down.

Each entry needs a link, a `Reading:` hint, and what it is useful for.

## Reading hints

```
Reading:
  start: top       # top = newest content first; bottom = newest last
  depth: 4 weeks   # N weeks | N entries | N slides
```

For Confluence parents whose weekly notes are separate child pages:

```
Reading:
  structure: child-pages
  depth: 2 weeks
```

With `structure: child-pages`, fetch the parent via Atlassian MCP, extract child page links, sort by date descending, and read only those inside the depth window. `start:` is ignored.

**If a hint is present, use it.** If absent, flag it in the sync receipt and fall back to: Google Docs — top, 4 weeks; Google Slides — top, 20 slides; Confluence single-page — latest dated section by heading scan. There is no fallback for `child-pages`; it must be declared.

Discard content outside the depth window unless it carries an unresolved risk or decision still active today. Never read a whole document that exceeds limits.

## Tool selection — mandatory

Never use WebFetch for these. It cannot reach Google or Confluence and returns 401.

| Source | Tool |
|---|---|
| Google Docs / Slides | Google Drive MCP — `read_file_content` |
| Confluence | Atlassian MCP — `getConfluencePage` or `fetch` |
| Google Calendar | Google Calendar MCP — `list_events` |

Google Docs file ID: `https://docs.google.com/document/d/<FILE_ID>/edit` → pass `<FILE_ID>`.

## Adding a source

`/sync` adds a stub here automatically when it reads an inbox or meeting note whose frontmatter has `save-source: true` and a `source:` URL. It leaves the `Reading:` and `Use for:` fields as `<fill in>` for you to complete — it will not guess them.

To add one by hand, copy this shape:

---

## <Source Name>

<url>

Reading:
  start: top
  depth: 4 weeks

Use for: <what signal this source carries — decisions · risks · ownership · delivery confidence · alignment gaps>

---

Pick sources where decisions actually get made and status actually changes. A document nobody updates is not a primary source; it is a liability, because `/sync` will keep reading it and finding nothing.
