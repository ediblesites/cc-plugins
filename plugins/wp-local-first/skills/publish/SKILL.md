---
name: publish
description: Publish an article from content/<slug>/ to WordPress using wp-post. Parses JSON output and writes id back to frontmatter.
allowed-tools: Bash(wp-post:*) Read Edit
---

# Publish Article

Push a local article to WordPress using the `wp-post` CLI.

## Input

```
/wp-local-first:publish <slug>
```

`$ARGUMENTS` is the article slug (directory name under `content/`).

## Steps

### 1. Validate

- Read `content/<slug>/index.md` and confirm it exists with valid frontmatter.
- If missing, tell the user to run `/wp-local-first:scaffold <title>`.

### 2. Publish via wp-post

Run:

```bash
wp-post content/<slug>/index.md --markdown
```

`wp-post` handles image uploads, markdown-to-HTML conversion, and post creation/update via the WordPress REST API.

It outputs JSON on success:

```json
{"success": true, "id": 123, "title": "...", "url": "..."}
```

### 3. Update frontmatter (post-publish loop)

Parse the JSON output from `wp-post`:

1. Write `id` into the frontmatter (this is the WordPress post ID).
2. If the `slug` in the frontmatter differs from the slug WordPress resolved (check the returned `url`), update `slug` to match.

Use the `Edit` tool to update the frontmatter fields in `content/<slug>/index.md`.

### 4. Report

Tell the user the result: created vs updated, post ID, and live URL.

## Error handling

- Missing article directory: tell the user to run `/wp-local-first:scaffold <title>`
- `wp-post` not found: tell the user to install `wp-poster` (`npm install -g wp-post` or equivalent)
- `wp-post` errors: display the error output
