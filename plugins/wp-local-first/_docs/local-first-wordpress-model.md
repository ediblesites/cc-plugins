# Local-first WordPress content model

## Core principle

The local filesystem is the source of truth. WordPress is a push target only - you never pull from it. Every article lives as a self-contained directory, and a publish script pushes content + images to WordPress via its REST API.

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
- `postId` - WP post ID, null until first publish, set by the publish script
- `publishedUrl` - full URL on the live site, set by the publish script
- `status` - content lifecycle state
- `createdAt`, `lastModified` - timestamps

**Project-specific** (define whatever your content needs):
- Title, description, taxonomy, keywords, content metadata - whatever fields your project requires

The body below the frontmatter is standard markdown.

## Publish flow (local to WordPress)

The publish script takes a slug and does:

1. Parse `index.md` into frontmatter + body
2. Check/upload images to WP media library. Dedup by filename to avoid re-uploading
3. Convert markdown to HTML
4. Create or update the WP post via REST API (create if `postId` is null, update if set)
5. **Write back** `postId` and `publishedUrl` into the frontmatter

The writeback is the critical design decision. After first publish, the local file knows its WP post ID and can update rather than duplicate on subsequent publishes. No separate mapping table needed.

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
2. **A frontmatter schema** that includes `postId` (null until first publish) and `publishedUrl`
3. **A publish script** that:
   - Reads frontmatter + body
   - Uploads images via WP REST API `/media` endpoint (with dedup by filename)
   - Converts markdown to HTML
   - POSTs to `/posts` (create) or PUTs to `/posts/<postId>` (update) via WP REST API
   - Writes `postId` and `publishedUrl` back into the frontmatter file
4. **WordPress config**: base URL, username, application password stored in a gitignored config file
5. **An index rebuilder** (optional) that scans all frontmatters into a single JSON for querying
