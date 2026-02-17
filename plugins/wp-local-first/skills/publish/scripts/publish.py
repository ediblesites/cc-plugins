#!/usr/bin/env python3
"""
Push article from content/<slug>/ to WordPress.
Handles image uploads, post creation/update, and frontmatter writeback.

Usage: python3 publish.py --content-dir content --config config/wordpress.json <slug>
"""

import json
import re
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone

import yaml
import mistune
import requests


def load_wp_config(config_path):
    """Load WordPress credentials from config JSON file."""
    config_path = Path(config_path)
    if not config_path.exists():
        print(f"ERROR: WordPress config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def parse_article(content_dir, slug):
    """Read and parse content/<slug>/index.md into (frontmatter, body_markdown)."""
    article_path = Path(content_dir) / slug / 'index.md'
    if not article_path.exists():
        print(f"ERROR: Article not found: {article_path}", file=sys.stderr)
        sys.exit(1)

    text = article_path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        print(f"ERROR: No frontmatter in {article_path}", file=sys.stderr)
        sys.exit(1)

    parts = text.split('---', 2)
    if len(parts) < 3:
        print(f"ERROR: Malformed frontmatter in {article_path}", file=sys.stderr)
        sys.exit(1)

    fm = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return fm, body


def write_frontmatter_back(content_dir, slug, fm, body):
    """Write updated frontmatter + body back to index.md atomically."""
    article_path = Path(content_dir) / slug / 'index.md'
    tmp_path = article_path.with_suffix('.tmp')

    fm_text = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)

    content = f"---\n{fm_text}---\n\n{body}\n"
    tmp_path.write_text(content, encoding='utf-8')
    os.rename(tmp_path, article_path)


def find_images_in_markdown(body, article_dir):
    """Find image references in markdown that point to local files."""
    images = []
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', body):
        alt_text, img_path = match.group(1), match.group(2)
        if not img_path.startswith(('http://', 'https://')):
            full_path = article_dir / img_path
            if full_path.exists():
                images.append({
                    'alt': alt_text,
                    'relative_path': img_path,
                    'full_path': full_path,
                    'markdown': match.group(0),
                })
    return images


def upload_image(wp_config, image_path, alt_text='', slug=None):
    """Upload image to WordPress media library. Returns (media_id, media_url).

    If slug is provided, prefix the filename to avoid collisions between articles
    (e.g. featured.webp -> my-article-featured.webp).
    """
    api_url = f"{wp_config['baseURL']}/media"
    auth = (wp_config['username'], wp_config['applicationPassword'])

    filename = f"{slug}-{image_path.name}" if slug else image_path.name
    ext = filename.lower()
    if ext.endswith(('.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    elif ext.endswith('.webp'):
        mime_type = 'image/webp'
    else:
        mime_type = 'image/png'

    with open(image_path, 'rb') as f:
        response = requests.post(
            api_url,
            auth=auth,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': mime_type,
            },
            data=f,
        )

    if response.status_code == 201:
        data = response.json()
        return data['id'], data['source_url']
    else:
        print(f"WARNING: Image upload failed for {filename}: {response.status_code}", file=sys.stderr)
        return None, None


def check_image_exists(wp_config, filename, slug=None, local_size=None):
    """Check if image already exists in WP media library by filename.

    If slug is provided, search for the slug-prefixed version.
    If local_size is provided, compare against the WP file size. When they
    differ the remote entry is stale - delete it and return (None, None) so the
    caller re-uploads.
    """
    if slug:
        filename = f"{slug}-{filename}"
    api_url = f"{wp_config['baseURL']}/media"
    auth = (wp_config['username'], wp_config['applicationPassword'])

    response = requests.get(api_url, auth=auth, params={'search': filename, 'per_page': 1})
    if response.status_code == 200:
        results = response.json()
        for item in results:
            if item.get('source_url', '').endswith(filename):
                if local_size is not None:
                    remote_size = (item.get('media_details') or {}).get('filesize')
                    if remote_size is not None and remote_size != local_size:
                        requests.delete(
                            f"{api_url}/{item['id']}",
                            auth=auth,
                            params={'force': True},
                        )
                        return None, None
                return item['id'], item['source_url']
    return None, None


def convert_markdown_to_html(body):
    """Convert markdown body to HTML using mistune."""
    return mistune.html(body)


def create_or_update_post(wp_config, fm, html_content, featured_media_id=None):
    """Create or update WordPress post. Returns (post_id, post_url)."""
    auth = (wp_config['username'], wp_config['applicationPassword'])

    payload = {
        'title': fm.get('title', ''),
        'content': html_content,
        'excerpt': fm.get('metaDescription', ''),
        'status': fm.get('status', 'publish'),
        'slug': fm.get('slug', ''),
    }

    if fm.get('categoryId'):
        payload['categories'] = [fm['categoryId']]

    if featured_media_id:
        payload['featured_media'] = featured_media_id

    post_id = fm.get('postId')

    if post_id:
        url = f"{wp_config['baseURL']}/posts/{post_id}"
        response = requests.put(url, json=payload, auth=auth)
        expected = 200
    else:
        url = f"{wp_config['baseURL']}/posts"
        response = requests.post(url, json=payload, auth=auth)
        expected = 201

    if response.status_code == expected:
        data = response.json()
        return data['id'], data['link']
    else:
        print(f"ERROR: WordPress API {response.status_code}: {response.text[:200]}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Publish article to WordPress')
    parser.add_argument('slug', help='Article slug (directory name under content/)')
    parser.add_argument('--content-dir', default='content',
                        help='Path to content directory (default: content)')
    parser.add_argument('--config', default='config/wordpress.json',
                        help='Path to WordPress config JSON (default: config/wordpress.json)')
    args = parser.parse_args()

    slug = args.slug
    content_dir = Path(args.content_dir)
    wp_config = load_wp_config(args.config)

    # 1. Parse article
    fm, body = parse_article(content_dir, slug)
    article_dir = content_dir / slug

    # 2. Upload featured image
    featured_media_id = None
    featured_img = None
    if fm.get('images') and isinstance(fm['images'], dict):
        featured_img = fm['images'].get('featured')
    if not featured_img:
        featured_img = fm.get('featuredImage')
    if featured_img:
        featured_path = article_dir / featured_img
        if featured_path.exists():
            fid, furl = check_image_exists(wp_config, featured_path.name, slug=slug,
                                           local_size=featured_path.stat().st_size)
            if not fid:
                fid, furl = upload_image(wp_config, featured_path, fm.get('title', ''), slug=slug)
            featured_media_id = fid

    # 3. Upload body images and replace paths
    images = find_images_in_markdown(body, article_dir)
    image_url_map = {}
    for img in images:
        filename = img['full_path'].name
        media_id, media_url = check_image_exists(wp_config, filename, slug=slug,
                                                 local_size=img['full_path'].stat().st_size)
        if not media_id:
            media_id, media_url = upload_image(wp_config, img['full_path'], img['alt'], slug=slug)
        if media_url:
            image_url_map[img['relative_path']] = media_url

    # 4. Replace relative image paths with WP URLs
    html_body = body
    for rel_path, wp_url in image_url_map.items():
        html_body = html_body.replace(f']({rel_path})', f']({wp_url})')

    # 5. Convert to HTML
    html_content = convert_markdown_to_html(html_body)

    # 6. Create or update post
    is_new = not fm.get('postId')
    post_id, post_url = create_or_update_post(wp_config, fm, html_content, featured_media_id)

    # 7. Write postId and publishedUrl back to frontmatter
    fm['postId'] = post_id
    fm['publishedUrl'] = post_url
    fm['lastModified'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    write_frontmatter_back(content_dir, slug, fm, body)

    action = 'Created' if is_new else 'Updated'
    print(f"{action}: {fm.get('title', slug)}")
    print(f"  Post ID: {post_id}")
    print(f"  URL: {post_url}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
