# CLAUDE.md

## Repo structure

A Claude Code **plugin marketplace**. Catalog lives at `.claude-plugin/marketplace.json`.

```
.claude-plugin/marketplace.json   # marketplace catalog (lists all plugins)
plugins/<plugin-name>/            # each plugin is self-contained here
  .claude-plugin/plugin.json      # plugin manifest (name, version, description)
  skills/<skill-name>/SKILL.md    # skill definitions (slash commands)
  skills/<skill-name>/scripts/    # backing scripts (Python, etc.)
```

Some plugins are local (source is a relative path under `plugins/`), others may reference external GitHub repos in the marketplace catalog.

## Plugin versioning

Always bump the version in a plugin's `.claude-plugin/plugin.json` and the matching entry in `.claude-plugin/marketplace.json` when making any change to that plugin's files.

## Markdown style

When creating markdown tables, align vertical bars for human readability.
