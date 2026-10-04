"""
NewsPulse - Feed Ingestion & Content Extraction Module
Fetches, cleans, deduplicates, and extracts metadata/images from multi-source RSS feeds.
"""

import re
import sys
import time
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
import feedparser
from bs4 import BeautifulSoup
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (NewsPulse/1.0 Bot)"
}


def slugify(text: str) -> str:
    """Creates a clean URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:65] or "story"


def clean_html(raw_html: str) -> str:
    """Strips HTML tags, script/style, and boilerplate text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.extract()
    text = soup.get_text(separator=" ")
    # Clean whitespace and boilerplate
    text = re.sub(r"\s+", " ", text).strip()
    # Strip common RSS boilerplate lines
    boilerplate = [
        r"The post .* appeared first on .*",
        r"Read more on .*",
        r"Click here to read more",
        r"Continue reading\.\.\.",
        r"© \d{4} .* All rights reserved\.",
        r"Follow us on Twitter.*"
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


def extract_image_url(entry, category_slug: str) -> str:
    """Extracts the best possible image URL from feed item or uses high-res fallback."""
    # 0. Google Trends picture
    if getattr(entry, "ht_picture", None):
        return entry.ht_picture
    if getattr(entry, "ht_news_item_picture", None):
        return entry.ht_news_item_picture

    # 1. media_content
    if "media_content" in entry and entry.media_content:
        for media in entry.media_content:
            url = media.get("url")
            if url and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp", "images", "photo"]):
                return url

    # 2. media_thumbnail
    if "media_thumbnail" in entry and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            url = thumb.get("url")
            if url:
                return url

    # 3. enclosures
    if "enclosures" in entry and entry.enclosures:
        for enc in entry.enclosures:
            url = enc.get("href") or enc.get("url")
            mime = enc.get("type", "")
            if url and ("image" in mime or any(ext in url.lower() for ext in [".jpg", ".png", ".webp"])):
                return url

    # 4. Search in html description or summary
    html_content = ""
    if "content" in entry and entry.content:
        html_content = entry.content[0].value
    elif "summary" in entry:
        html_content = entry.summary
    elif "description" in entry:
        html_content = entry.description

    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            src = img["src"]
            if not src.startswith("http"):
                pass
            elif "pixel" not in src and "stat" not in src and "tracking" not in src:
                return src

    # 5. Fallback to curated default for category
    cat_conf = config.CATEGORIES.get(category_slug, {})
    return cat_conf.get("default_image", "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop")


def format_relative_time(dt: datetime) -> str:
    """Returns human-friendly relative time (e.g. '15m ago', '2h ago')."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    else:
        days = seconds // 86400
        if days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days}d ago"
        return dt.strftime("%b %d, %Y")


def parse_entry_time(entry) -> datetime:
    """Parses published or updated time from feed entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def extract_source_name(entry, feed_url: str) -> str:
    """Determines clean publisher/source name."""
    if getattr(entry, "ht_news_item_source", None):
        return entry.ht_news_item_source.strip()
    if hasattr(entry, "source") and entry.source and hasattr(entry.source, "title"):
        return entry.source.title.strip()
    parsed = urlparse(feed_url)
    domain = parsed.netloc.lower()
    if "bbci.co.uk" in domain or "bbc.com" in domain:
        return "BBC News"
    if "techcrunch.com" in domain:
        return "TechCrunch"
    if "theverge.com" in domain:
        return "The Verge"
    if "arstechnica.com" in domain:
        return "Ars Technica"
    if "technologyreview.com" in domain:
        return "MIT Tech Review"
    if "aljazeera.com" in domain:
        return "Al Jazeera"
    if "espn.com" in domain:
        return "ESPN"
    if "espncricinfo.com" in domain:
        return "ESPN Cricinfo"
    if "cnbc.com" in domain:
        return "CNBC"
    if "9to5mac.com" in domain:
        return "9to5Mac"
    if "wired.com" in domain:
        return "Wired"
    if "yahoo.com" in domain:
        return "Yahoo Finance"
    if "coindesk.com" in domain:
        return "CoinDesk"
    if "ign.com" in domain or "feedburner.com" in domain:
        return "IGN"
    if "variety.com" in domain:
        return "Variety"
    if "hollywoodreporter.com" in domain:
        return "Hollywood Reporter"
    if "trends.google.com" in domain:
        return "Google Trends"
    if "news.google.com" in domain:
        # Google News RSS often puts source at the end: 'Headline - SourceName'
        return "Google News"
    return domain.replace("www.", "").capitalize()


def fetch_all_categories(max_per_category: int = None) -> list:
    """
    Ingests and parses top news items across all defined categories.
    Returns a deduplicated list of raw articles ready for summarization and story creation.
    """
    if max_per_category is None:
        max_per_category = config.MAX_ARTICLES_PER_CATEGORY

    articles = []
    seen_hashes = set()
    seen_slugs = set()

    print(f"[*] Starting ingestion for {len(config.CATEGORIES)} categories...")

    for cat_slug, cat_info in config.CATEGORIES.items():
        cat_count = 0
        print(f"    -> Fetching {cat_info['name']} ({len(cat_info['feeds'])} feeds)...")

        for feed_url in cat_info["feeds"]:
            if cat_count >= max_per_category:
                break
            try:
                parsed_feed = feedparser.parse(feed_url, request_headers=HEADERS)
                entries = parsed_feed.entries or []

                for entry in entries:
                    if cat_count >= max_per_category:
                        break

                    # Check Google Trends item attributes
                    trend_headline = getattr(entry, "ht_news_item_title", None)
                    if trend_headline:
                        raw_title = clean_html(trend_headline)
                    else:
                        raw_title = entry.get("title", "").strip()

                    if not raw_title:
                        continue

                    # If title ends with "- SourceName", separate it
                    source_name = extract_source_name(entry, feed_url)
                    if " - " in raw_title and ("Google" in source_name or source_name == "NewsPulse"):
                        parts = raw_title.rsplit(" - ", 1)
                        if len(parts) == 2 and len(parts[1]) < 30:
                            raw_title = parts[0].strip()
                            if source_name == "Google News":
                                source_name = parts[1].strip()

                    # Deduplication key based on title normalized
                    title_norm = re.sub(r"\W+", "", raw_title.lower())
                    title_hash = hashlib.md5(title_norm.encode("utf-8")).hexdigest()
                    if title_hash in seen_hashes:
                        continue

                    # Slug generation
                    base_slug = slugify(raw_title)
                    slug = base_slug
                    suffix = 1
                    while slug in seen_slugs:
                        slug = f"{base_slug}-{suffix}"
                        suffix += 1

                    # Extract raw summary / description
                    raw_summary = ""
                    if getattr(entry, "ht_news_item_snippet", None):
                        raw_summary = clean_html(entry.ht_news_item_snippet)
                    if not raw_summary and "content" in entry and entry.content:
                        raw_summary = clean_html(entry.content[0].value)
                    if not raw_summary and "summary" in entry:
                        raw_summary = clean_html(entry.summary)
                    if not raw_summary and "description" in entry:
                        raw_summary = clean_html(entry.description)
                    if not raw_summary:
                        raw_summary = raw_title

                    # Published time
                    pub_dt = parse_entry_time(entry)
                    pub_iso = pub_dt.isoformat()
                    time_ago = format_relative_time(pub_dt)

                    # Image URL
                    image_url = extract_image_url(entry, cat_slug)

                    # Original URL
                    link = getattr(entry, "ht_news_item_url", None) or entry.get("link", "#")

                    article = {
                        "id": f"art_{len(articles) + 1}",
                        "slug": slug,
                        "category": cat_slug,
                        "category_name": cat_info["name"],
                        "category_color": cat_info["color"],
                        "category_gradient": cat_info["gradient"],
                        "category_icon": cat_info["icon"],
                        "source": source_name,
                        "raw_title": raw_title,
                        "title": raw_title,  # Will be refined by AI
                        "raw_summary": raw_summary,
                        "summary": raw_summary,  # Will be refined to 60 words by AI
                        "image_url": image_url,
                        "original_url": link,
                        "published_at": pub_iso,
                        "time_ago": time_ago,
                        "reading_time": "1 min read"
                    }

                    seen_hashes.add(title_hash)
                    seen_slugs.add(slug)
                    articles.append(article)
                    cat_count += 1

            except Exception as e:
                print(f"    [!] Warning: Error parsing {feed_url}: {e}")
                continue

    print(f"[OK] Successfully ingested {len(articles)} unique articles across all categories.")
    return articles


if __name__ == "__main__":
    arts = fetch_all_categories(max_per_category=2)
    print(f"Test run completed. Total: {len(arts)}")
    if arts:
        print(f"Sample: [{arts[0]['category_name']}] {arts[0]['title']} ({arts[0]['source']})")
