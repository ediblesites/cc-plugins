---
name: publish
description: Publish an article from content/<slug>/ to WordPress via REST API. Uploads images, creates or updates the post, writes postId back to frontmatter.
allowed-tools: Bash(python3:*) Bash(python:*)
---

# Publish Article

Push a local article to WordPress.

## Input

```
/wp-local-first:publish <slug>
```

`$ARGUMENTS` is the article slug (directory name under `content/`).

## Execution

Run the publish script:

```bash
python3 <plugin-dir>/skills/publish/scripts/publish.py --content-dir content --config config/wordpress.json $ARGUMENTS
```

Where `<plugin-dir>` is the directory containing this skill (resolve relative to this SKILL.md file's location, two levels up).

The script:
1. Parses `content/<slug>/index.md` (frontmatter + body)
2. Uploads featured image and body images to WP media library (dedup by filename + size check)
3. Converts markdown to HTML
4. Creates post (if `postId` is null) or updates existing post via WP REST API
5. Writes `postId`, `publishedUrl`, and `lastModified` back into the frontmatter

## Error handling

- Missing `config/wordpress.json`: tell the user to run `/wp-local-first:setup`
- Missing article directory: tell the user to run `/wp-local-first:scaffold <title>`
- WP API errors: the script prints the status code and response body
