"""
Prune old non-auto and historical stories from NewsPulse/NewsSeconds.
Retains the most recent N articles (default 150) covering the active automotive niche,
deletes orphaned static folders in dist/stories and dist/news, and regenerates sitemaps.
"""
import os
import sys
import json
import shutil
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
import site_generator

def get_folder_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def main(keep_count: int = 150):
    articles_file = config.DATA_DIR / "articles.json"
    dist_stories_dir = config.DIST_DIR / "stories"
    dist_news_dir = config.DIST_DIR / "news"

    if not articles_file.exists():
        print(f"[ERROR] {articles_file} not found.")
        return 1

    with open(articles_file, "r", encoding="utf-8") as f:
        all_articles = json.load(f)

    total_articles = len(all_articles)
    print(f"[*] Total articles in archive: {total_articles}")

    # Sort descending by published_at
    def sort_key(a):
        return a.get("published_at") or "1970-01-01T00:00:00Z"

    all_articles.sort(key=sort_key, reverse=True)

    kept_articles = all_articles[:keep_count]
    pruned_articles = all_articles[keep_count:]
    kept_slugs = {a["slug"] for a in kept_articles if a.get("slug")}

    print(f"[*] Keeping {len(kept_articles)} latest articles (spans {kept_articles[-1].get('published_at', '')[:10]} to {kept_articles[0].get('published_at', '')[:10]})")
    print(f"[*] Pruning {len(pruned_articles)} old articles...")

    # Calculate initial sizes
    stories_size_before = get_folder_size(dist_stories_dir)
    news_size_before = get_folder_size(dist_news_dir)
    print(f"[*] Size before: dist/stories = {stories_size_before / (1024*1024):.2f} MB, dist/news = {news_size_before / (1024*1024):.2f} MB")

    # 1. Prune dist/stories
    deleted_stories_count = 0
    if dist_stories_dir.exists():
        for item in dist_stories_dir.iterdir():
            if item.is_dir() and item.name not in kept_slugs:
                shutil.rmtree(item, ignore_errors=True)
                deleted_stories_count += 1
    print(f"[OK] Deleted {deleted_stories_count} orphaned story folders from dist/stories/")

    # 2. Prune dist/news
    deleted_news_count = 0
    if dist_news_dir.exists():
        for item in dist_news_dir.iterdir():
            if item.is_dir() and item.name not in kept_slugs:
                shutil.rmtree(item, ignore_errors=True)
                deleted_news_count += 1
    print(f"[OK] Deleted {deleted_news_count} orphaned news folders from dist/news/")

    # 3. Update data/articles.json
    with open(articles_file, "w", encoding="utf-8") as f:
        json.dump(kept_articles, f, indent=2, ensure_ascii=False)
    print(f"[OK] Updated {articles_file} ({len(kept_articles)} articles, {articles_file.stat().st_size / 1024:.2f} KB)")

    # 4. Update dist/api/articles.json
    dist_api = config.DIST_DIR / "api" / "articles.json"
    dist_api.parent.mkdir(parents=True, exist_ok=True)
    with open(dist_api, "w", encoding="utf-8") as f:
        json.dump(kept_articles, f, indent=2, ensure_ascii=False)
    print(f"[OK] Updated {dist_api}")

    # 5. Rebuild sitemaps & static site distribution
    print("[*] Rebuilding static site, sitemaps, and homepage...")
    site_generator.build_static_site(kept_articles)

    # Calculate final sizes
    stories_size_after = get_folder_size(dist_stories_dir)
    news_size_after = get_folder_size(dist_news_dir)
    freed_mb = ((stories_size_before - stories_size_after) + (news_size_before - news_size_after)) / (1024*1024)

    print("\n" + "="*50)
    print(f"CLEANUP SUCCESSFUL!")
    print(f"dist/stories: {stories_size_before / (1024*1024):.2f} MB -> {stories_size_after / (1024*1024):.2f} MB")
    print(f"dist/news:    {news_size_before / (1024*1024):.2f} MB -> {news_size_after / (1024*1024):.2f} MB")
    print(f"TOTAL FREED:  {freed_mb:.2f} MB!")
    print("="*50)
    return 0

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    sys.exit(main(count))
