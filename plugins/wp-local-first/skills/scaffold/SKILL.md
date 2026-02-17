---
name: scaffold
description: Create a new article directory with index.md frontmatter template. Takes a title or topic as argument.
---

# Scaffold Article

Create a new article from a title or topic.

## Input

```
/wp-local-first:scaffold How to Make Sourdough Bread
```

`$ARGUMENTS` is the article title or topic.

## Steps

### 1. Generate slug

Convert `$ARGUMENTS` to a URL-safe slug:
- Lowercase
- Replace spaces with hyphens
- Strip non-alphanumeric characters (except hyphens)
- Collapse multiple hyphens

### 2. Create directory

Create `content/<slug>/` if it doesn't exist. If it already exists, stop and tell the user.

### 3. Create index.md

Write `content/<slug>/index.md` with frontmatter:

```yaml
---
slug: <generated-slug>
title: <title from arguments>
excerpt: ""
status: draft
createdAt: <current UTC ISO 8601>
---

```

Leave the body empty below the frontmatter fences.

### 4. Report

Print the path to the created file.
