---
name: rebuild-index
description: Scan all content/*/index.md frontmatters and rebuild _index.json. Useful for querying across all articles without parsing each file.
allowed-tools: Bash(python3:*) Bash(python:*)
---

# Rebuild Index

Scan all article frontmatters into a single JSON index file.

## Execution

Run the rebuild script:

```bash
python3 <plugin-dir>/skills/rebuild-index/scripts/rebuild_index.py --content-dir content --output _index.json
```

Where `<plugin-dir>` is the directory containing this skill (resolve relative to this SKILL.md file's location, two levels up).

Optional: pass `--fields slug,title,id,status` to whitelist specific frontmatter fields. Without `--fields`, all frontmatter fields are included.

## Output

Writes `_index.json` at the specified path:

```json
{
  "articles": [
    {"slug": "...", "title": "...", "id": 123, "...": "..."}
  ],
  "rebuiltAt": "2026-01-01T00:00:00Z"
}
```
