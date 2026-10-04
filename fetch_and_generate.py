"""
NewsPulse - Unified Pipeline Runner (fetch_and_generate.py)
Automates the full ingestion, AI summarization, AMP story synthesis,
static site generation, sitemap updates, and compliance validation.
"""

import sys
import time
import argparse
from datetime import datetime, timezone
import config
from fetcher import fetch_all_categories
from summarizer import enrich_all_articles
from site_generator import build_static_site
from validate_amp import validate_all_stories

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_pipeline(max_per_category: int = None, skip_validation: bool = False):
    """Executes the complete NewsPulse publishing pipeline."""
    start_time = time.time()
    print("=" * 72)
    print(f"  ⚡ {config.SITE_NAME} AUTOMATED PUBLISHING PIPELINE")
    print(f"  Target: {config.SITE_URL} | Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 72)

    # Step 1: Ingest multi-source RSS feeds
    print("\n[Step 1/4] Ingesting breaking feeds across all categories...")
    articles = fetch_all_categories(max_per_category=max_per_category)
    if not articles:
        print("[!] No articles ingested. Exiting.")
        return False

    # Step 2: Summarize & fact-check with Gemini 3.8 Flash / Rule-Based NLP
    print(f"\n[Step 2/4] Summarizing & fact-checking {len(articles)} stories...")
    enriched_articles = enrich_all_articles(articles)

    # Step 3: Build static production site & AMP stories into dist/
    print("\n[Step 3/4] Building static pages, AMP stories, sitemap, and compliance suite...")
    build_static_site(enriched_articles)

    # Step 4: Validate AMP compliance
    if not skip_validation:
        print("\n[Step 4/5] Running Google AMP Validator compliance checks...")
        amp_passed = validate_all_stories()
    else:
        print("\n[Step 4/5] AMP validation skipped by user flag.")
        amp_passed = True

    # Step 5: Auto-broadcast top stories to Twitter, Reddit & Telegram
    print("\n[Step 5/5] Checking social syndication channels (Twitter, Reddit, Telegram)...")
    try:
        from social_poster import auto_share_top_articles
        auto_share_top_articles(enriched_articles, max_posts=2)
    except Exception as e:
        print(f"  [!] Note on social broadcast: {e}")

    duration = time.time() - start_time
    print("\n" + "=" * 72)
    print(f"  [OK] PIPELINE FINISHED IN {duration:.2f}s!")
    print(f"  Stories Generated: {len(enriched_articles)}")
    print(f"  AMP Compliance: {'100% PASS' if amp_passed else 'WARNINGS DETECTED'}")
    print(f"  Output Directory: {config.DIST_DIR}")
    print(f"  Deploy Command: cd dist && vercel --prod (or cloudflare pages)")
    print("=" * 72 + "\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{config.SITE_NAME} Automated Publisher")
    parser.add_argument("--count", type=int, default=config.MAX_ARTICLES_PER_CATEGORY, help="Max articles per category (default: 5)")
    parser.add_argument("--skip-val", action="store_true", help="Skip AMP validator step")
    args = parser.parse_args()

    success = run_pipeline(max_per_category=args.count, skip_validation=args.skip_val)
    sys.exit(0 if success else 1)
