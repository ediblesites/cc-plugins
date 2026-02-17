# Local-first WordPress content model

## Core principle

The local filesystem is the source of truth. WordPress is a push target only - you never pull from it. Every article lives as a self-contained directory, and the `wp-post` CLI pushes content + images to WordPress via its REST API.

## Directory structure per article

```
content/<slug>/
  index.md          # frontmatter (YAML) + markdown body
  featured.webp     # featured image (optional)
  body-1.webp       # body images (optional)
```

One directory per article, always containing `index.md`, optionally containing images.

## Frontmatter as structured state

The `index.md` file starts with YAML frontmatter between `---` fences. The frontmatter carries two categories of fields:

**Required for the pattern** (these make it work):
- `slug` - directory name, used as identifier
- `id` - WP post ID, absent until first publish, written by the publish skill
- `status` - content lifecycle state

**Project-specific** (define whatever your content needs):
- Title, excerpt, taxonomy, keywords, content metadata - whatever fields your project requires

The body below the frontmatter is standard markdown.

## Publish flow (local to WordPress)

The publish skill runs `wp-post` and does:

1. Call `wp-post content/<slug>/index.md --markdown`
2. `wp-post` parses frontmatter + body, uploads images, converts markdown to HTML, and creates or updates the WP post via REST API (create if `id` is absent, update if present)
3. `wp-post` returns JSON: `{"success": true, "id": 123, "title": "...", "url": "..."}`
4. The publish skill writes `id` back into the frontmatter

The `id` writeback is the critical design decision. After first publish, the local file knows its WP post ID and can update rather than duplicate on subsequent publishes. No separate mapping table needed.

## Derived index (optional)

A rebuild script scans all `content/*/index.md` frontmatters and extracts a subset of fields into a single JSON file. This is a gitignored, rebuildable artifact useful for querying across all articles without parsing every frontmatter each time. Schema:

```json
{
  "articles": [
    {"slug": "...", "title": "...", "...": "..."}
  ],
  "rebuiltAt": "..."
}
```

## What you need to replicate this pattern

1. **A content directory** with one subdirectory per article, each containing `index.md` (frontmatter + body) and any images
2. **A frontmatter schema** that includes `id` (absent until first publish)
3. **The `wp-post` CLI** (from the wp-poster package) to handle image uploads, markdown conversion, and WordPress REST API calls
4. **WordPress config**: base URL, username, application password stored in a gitignored config file
5. **An index rebuilder** (optional) that scans all frontmatters into a single JSON for querying
