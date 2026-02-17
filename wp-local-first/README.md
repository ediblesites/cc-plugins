# wp-local-first

A Claude Code plugin for local-first WordPress content management. Your markdown files are the source of truth - WordPress is a push target only.

## How it works

Each article lives as a self-contained directory:

```
content/<slug>/
  index.md          # frontmatter (YAML) + markdown body
  featured.webp     # featured image (optional)
  body-1.webp       # body images (optional)
```

The frontmatter carries `postId` (null until first publish) and `publishedUrl`. When you publish, the script pushes content + images to WordPress via REST API and writes the post ID back into the frontmatter. Subsequent publishes update rather than duplicate.

## Installation

```bash
claude --plugin-dir ./wp-local-first
```

Or add to a plugin marketplace for team distribution.

## Python dependencies

The publish and rebuild-index scripts require:

```
pyyaml
mistune
requests
```

Install with `pip install pyyaml mistune requests`.

## Skills

| Skill           | Description                                                    |
| --------------- | -------------------------------------------------------------- |
| `setup`         | Initialize project: content dir, WP config, gitignore, schema |
| `scaffold`      | Create a new article directory from a title                    |
| `publish`       | Push an article to WordPress (create or update)                |
| `rebuild-index` | Scan all frontmatters into `_index.json` for querying          |

### setup

```
/wp-local-first:setup
```

Creates the project scaffolding: `content/` directory, `config/wordpress.json` template, `.gitignore` entries, and `references/frontmatter-schema.md`.

### scaffold

```
/wp-local-first:scaffold How to Make Sourdough Bread
```

Creates `content/how-to-make-sourdough-bread/index.md` with frontmatter template.

### publish

```
/wp-local-first:publish my-article-slug
```

Uploads images (deduped by filename + size check), converts markdown to HTML, creates or updates the WP post, and writes `postId` back to frontmatter.

### rebuild-index

```
/wp-local-first:rebuild-index
```

Scans all `content/*/index.md` frontmatters into `_index.json`. Optionally filter fields with `--fields slug,title,postId`.

## WordPress requirements

- WordPress REST API enabled (default in WP 5+)
- Application password for authentication (Users > Profile > Application Passwords)
- Credentials stored in `config/wordpress.json` (gitignored)

## Design decisions

- **No database**: frontmatter is the state. `postId` writeback eliminates mapping tables.
- **Slug-prefixed image filenames**: avoids collisions when multiple articles have `featured.webp`.
- **Size-check dedup**: if a local image changes, the stale WP copy is deleted and re-uploaded.
- **Atomic writes**: frontmatter writeback uses tmp file + rename to prevent corruption.
