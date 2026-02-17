#!/usr/bin/env python3
"""
Scan all content/*/index.md frontmatters and build _index.json.
A derived, rebuildable artifact for querying across all articles.

Usage: python3 rebuild_index.py --content-dir content --output _index.json
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timezone

import yaml


def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file. Returns dict or None."""
    text = filepath.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return None

    parts = text.split('---', 2)
    if len(parts) < 3:
        return None

    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def build_index(articles_dir, fields=None):
    """Scan all article directories and build index list.

    If fields is provided, only include those frontmatter keys.
    Otherwise include all frontmatter fields.
    """
    articles_dir = Path(articles_dir)
    articles = []

    if not articles_dir.exists():
        return articles

    for index_file in sorted(articles_dir.glob('*/index.md')):
        fm = parse_frontmatter(index_file)
        if fm is None:
            print(f"Warning: skipping {index_file} (no valid frontmatter)", file=sys.stderr)
            continue

        if fields:
            entry = {}
            for field in fields:
                if field in fm:
                    val = fm[field]
                    if isinstance(val, (datetime, date)):
                        val = val.isoformat()
                    entry[field] = val
        else:
            entry = {}
            for key, val in fm.items():
                if isinstance(val, (datetime, date)):
                    val = val.isoformat()
                entry[key] = val

        # Ensure slug is set (fall back to directory name)
        if 'slug' not in entry:
            entry['slug'] = index_file.parent.name

        articles.append(entry)

    return articles


def atomic_write_json(path, data):
    """Write JSON atomically: write to .tmp then rename."""
    path = Path(path)
    tmp_path = path.with_suffix('.tmp')
    with open(tmp_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    os.rename(tmp_path, path)


def main():
    parser = argparse.ArgumentParser(description='Rebuild article index from frontmatters')
    parser.add_argument('--content-dir', default='content',
                        help='Path to content directory (default: content)')
    parser.add_argument('--output', default='_index.json',
                        help='Output JSON path (default: _index.json)')
    parser.add_argument('--fields', default=None,
                        help='Comma-separated list of frontmatter fields to include (default: all)')
    args = parser.parse_args()

    fields = None
    if args.fields:
        fields = [f.strip() for f in args.fields.split(',')]

    articles = build_index(args.content_dir, fields=fields)

    index_data = {
        'articles': articles,
        'rebuiltAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }

    atomic_write_json(args.output, index_data)

    print(f"Rebuilt {args.output}: {len(articles)} articles")
    return 0


if __name__ == '__main__':
    sys.exit(main())
