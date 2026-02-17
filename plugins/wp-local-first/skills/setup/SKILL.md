---
name: setup
description: Initialize a project for local-first WordPress publishing. Creates content directory, WordPress config template, gitignore entries, and frontmatter schema reference.
---

# Setup

Initialize the current project for local-first WordPress content management.

## Steps

### 1. Create content directory

Create `content/` at the project root if it doesn't exist.

### 2. Create WordPress config

Create `config/wordpress.json` with this template:

```json
{
  "baseURL": "https://your-site.com/wp-json/wp/v2",
  "username": "your-username",
  "applicationPassword": "xxxx xxxx xxxx xxxx xxxx xxxx"
}
```

Print a message telling the user to fill in their credentials. The application password is generated in WordPress under Users > Profile > Application Passwords.

### 3. Update .gitignore

Add these entries to `.gitignore` (create the file if needed, append if it exists). Do not duplicate entries that already exist:

```
config/wordpress.json
_index.json
```

### 4. Create frontmatter schema reference

Create `references/frontmatter-schema.md` with this content:

```markdown
# Frontmatter Schema

Required fields for the local-first WordPress pattern:

---
slug: example-article
title: Example Article Title
excerpt: A short description for SEO and excerpts
status: draft
createdAt: 2026-01-01T00:00:00Z
---

## Field reference

| Field     | Source   | Description                                 |
| --------- | -------- | ------------------------------------------- |
| slug      | scaffold | URL-safe identifier, matches directory name |
| title     | manual   | Article title                               |
| excerpt   | manual   | SEO meta description, used as WP excerpt    |
| id        | publish  | WordPress post ID, absent until published   |
| status    | manual   | Content lifecycle state (draft, publish)    |
| createdAt | scaffold | ISO 8601 creation timestamp                 |

The `id` field is written into frontmatter by the publish skill after wp-post returns a successful response.

Add project-specific fields below the required ones (e.g. categories, tags, featured_image).
```

### 5. Report

Print a summary of what was created and remind the user to:
1. Fill in `config/wordpress.json` with their WordPress credentials
2. Ensure `wp-post` CLI is installed (from the wp-poster package)
3. Add project-specific fields to the frontmatter schema
