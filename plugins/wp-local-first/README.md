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

The frontmatter carries `id` (the WordPress post ID, absent until first publish). When you publish, `wp-post` pushes content + images to WordPress via REST API and the skill writes the post ID back into the frontmatter. Subsequent publishes update rather than duplicate.

## Prerequisites

- **`wp-post` CLI** from the [wp-poster](https://github.com/ediblesites/wp-poster) package — handles image uploads, markdown-to-HTML conversion, and WordPress REST API calls
- **Python 3** with `pyyaml` — used by the rebuild-index skill

Install Python dependency:

```
pip install pyyaml
```

## Installation

```bash
claude --plugin-dir ./wp-local-first
```

Or add to a plugin marketplace for team distribution.

## Skills

| Skill           | Description                                                    |
| --------------- | -------------------------------------------------------------- |
| `setup`         | Initialize project: content dir, WP config, gitignore, schema |
| `scaffold`      | Create a new article directory from a title                    |
| `publish`       | Push an article to WordPress (create or update via wp-post)    |
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

Runs `wp-post` to upload images, convert markdown to HTML, and create or update the WP post. Writes `id` back to frontmatter on success.

### rebuild-index

```
/wp-local-first:rebuild-index
```

Scans all `content/*/index.md` frontmatters into `_index.json`. Optionally filter fields with `--fields slug,title,id`.

## WordPress requirements

- WordPress REST API enabled (default in WP 5+)
- Application password for authentication (Users > Profile > Application Passwords)
- Credentials stored in `config/wordpress.json` (gitignored)

## Design decisions

- **No database**: frontmatter is the state. `id` writeback eliminates mapping tables.
- **wp-post as engine**: all WordPress interaction (image uploads, HTML conversion, REST API calls) is delegated to `wp-post`, avoiding duplicated logic.
- **Slug-prefixed image filenames**: avoids collisions when multiple articles have `featured.webp`.
