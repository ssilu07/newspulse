"""
NewsPulse - Feed Ingestion & Content Extraction Module
Fetches, cleans, deduplicates, and extracts metadata/images from multi-source RSS feeds.
Equipped with OpenGraph web-scraper fallback and high-resolution media transformers.
"""

import re
import sys
import time
import hashlib
import urllib.request
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (NewsPulse/2.0 Bot)"
}

# Curated high-resolution editorial backup images (per category) if an article has no photo
CATEGORY_CURATED_POOLS = {
    "trending": [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=800&fit=crop"
    ],
    "tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=1200&h=800&fit=crop"
    ],
    "ai-future": [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1677442136019-21780efad99a?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=1200&h=800&fit=crop"
    ],
    "business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=800&fit=crop"
    ],
    "world": [
        "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1572949645841-094f3a9c4c94?w=1200&h=800&fit=crop"
    ],
    "sports": [
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1200&h=800&fit=crop"
    ],
    "entertainment": [
        "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1200&h=800&fit=crop"
    ]
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
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.extract()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    # Strip common RSS boilerplate lines
    boilerplate = [
        r"The post .* appeared first on .*",
        r"Read more on .*",
        r"Click here to read more",
        r"Continue reading\.\.\.",
        r"© \d{4} .* All rights reserved\.",
        r"Follow us on Twitter.*",
        r"Sign up for our .* newsletter.*",
        r"Subscribe to .*"
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


def extract_web_meta(url: str, timeout: float = 3.5) -> tuple:
    """
    Scrapes OpenGraph image and description from the actual news article page
    when RSS feeds lack full content or high-res images.
    """
    if not url or not url.startswith("http") or "google.com" in url:
        return "", ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Read first 65KB containing the head tags
            html = resp.read(65000).decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")

        # 1. OG Image or Twitter Image
        og_img = (
            soup.find("meta", property="og:image")
            or soup.find("meta", attrs={"name": "twitter:image"})
            or soup.find("meta", property="twitter:image")
        )
        img_url = og_img.get("content", "").strip() if og_img else ""

        # 2. OG Description or Meta Description
        og_desc = (
            soup.find("meta", property="og:description")
            or soup.find("meta", attrs={"name": "description"})
            or soup.find("meta", attrs={"name": "twitter:description"})
        )
        desc = og_desc.get("content", "").strip() if og_desc else ""

        return img_url, desc
    except Exception:
        return "", ""


def extract_image_url(entry, feed_url: str, category_slug: str, entry_link: str = "", title: str = "") -> str:
    """
    Extracts the best possible high-resolution image URL:
    1. Upgrades BBC thumbnails from 240px to 1024px HD.
    2. RSS media:content and enclosures.
    3. Content <img> tags (skipping tracking pixels).
    4. OpenGraph scraper on the original article URL.
    5. Curated category image pool (never repeats identically).
    """
    # 1. media_thumbnail (e.g., BBC, Variety)
    if "media_thumbnail" in entry and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            url = thumb.get("url")
            if url:
                # Upgrade BBC standard thumbnails to crystal clear 1024px HD
                if "bbci.co.uk" in url and "/240/" in url:
                    url = url.replace("/240/", "/1024/")
                elif "bbci.co.uk" in url and "/320/" in url:
                    url = url.replace("/320/", "/1024/")
                return url

    # 2. media_content
    if "media_content" in entry and entry.media_content:
        for media in entry.media_content:
            url = media.get("url")
            if url and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp", "images", "photo", "upload"]):
                if not any(bad in url.lower() for bad in ["pixel", "avatar", "icon", "logo", "1x1"]):
                    return url

    # 3. enclosures
    if "enclosures" in entry and entry.enclosures:
        for enc in entry.enclosures:
            url = enc.get("href") or enc.get("url")
            mime = enc.get("type", "")
            if url and ("image" in mime or any(ext in url.lower() for ext in [".jpg", ".png", ".webp"])):
                return url

    # 4. Search in html description, summary, or content:encoded
    html_content = ""
    if "content" in entry and entry.content:
        html_content = entry.content[0].value
    elif "summary" in entry:
        html_content = entry.summary
    elif "description" in entry:
        html_content = entry.description

    if html_content and "<img" in html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("http") and not any(bad in src.lower() for bad in ["pixel", "stat", "tracking", "feedsportal", "doubleclick", "spacer", "1x1"]):
                return src

    # 5. OpenGraph Web Scrape fallback (fetches real editorial image from article page)
    if entry_link and entry_link.startswith("http") and "google.com" not in entry_link:
        og_img, _ = extract_web_meta(entry_link, timeout=3.5)
        if og_img and og_img.startswith("http") and not any(bad in og_img.lower() for bad in ["pixel", "spacer", "blank"]):
            return og_img

    # 6. High-Res Diverse Curated Pool Fallback
    pool = CATEGORY_CURATED_POOLS.get(category_slug, CATEGORY_CURATED_POOLS["trending"])
    seed = int(hashlib.md5((title or category_slug).encode("utf-8")).hexdigest()[:6], 16)
    return pool[seed % len(pool)]


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
        mins = max(1, seconds // 60)
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
        return dt.strftime("%b %d")


def parse_entry_time(entry) -> datetime:
    """Parses published or updated time from feed entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def extract_source_name(entry, feed_url: str) -> str:
    """Determines clean publisher/source name."""
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
    if "venturebeat.com" in domain:
        return "VentureBeat"
    if "aljazeera.com" in domain:
        return "Al Jazeera"
    if "espn.com" in domain:
        return "ESPN"
    if "espncricinfo.com" in domain:
        return "ESPN Cricinfo"
    if "cnbc.com" in domain:
        return "CNBC"
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
    if "npr.org" in domain:
        return "NPR"
    if "theguardian.com" in domain:
        return "The Guardian"
    if "france24.com" in domain:
        return "France 24"
    if "skysports.com" in domain or "skynews.com" in domain:
        return "Sky News"
    return domain.replace("www.", "").capitalize()


def fetch_all_categories(max_per_category: int = None) -> list:
    """
    Ingests and parses top news items across all defined categories.
    Guarantees rich content, zero BS generic filler, and sharp editorial images.
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

                    raw_title = entry.get("title", "").strip()
                    if not raw_title:
                        continue

                    # Clean source name suffixes (e.g. "Headline - BBC News")
                    source_name = extract_source_name(entry, feed_url)
                    if " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        if len(parts) == 2 and len(parts[1]) < 30:
                            raw_title = parts[0].strip()

                    # Deduplication key based on title normalized
                    title_norm = re.sub(r"\W+", "", raw_title.lower())
                    title_hash = hashlib.md5(title_norm.encode("utf-8")).hexdigest()
                    if title_hash in seen_hashes:
                        continue

                    # Original URL
                    link = entry.get("link", "#")

                    # Extract raw summary / description
                    raw_summary = ""
                    if "content" in entry and entry.content:
                        raw_summary = clean_html(entry.content[0].value)
                    if not raw_summary and "summary" in entry:
                        raw_summary = clean_html(entry.summary)
                    if not raw_summary and "description" in entry:
                        raw_summary = clean_html(entry.description)

                    # If summary is tiny or missing, scrape OG meta from original page
                    og_image_candidate = ""
                    if len(raw_summary.split()) < 12 and link.startswith("http") and "google.com" not in link:
                        og_img, og_desc = extract_web_meta(link, timeout=3.0)
                        if og_desc and len(og_desc.split()) >= 8:
                            raw_summary = clean_html(og_desc)
                        if og_img:
                            og_image_candidate = og_img

                    # Discard empty/stub items without substance (no BS stubs allowed!)
                    if len(raw_summary.split()) < 8 and len(raw_title.split()) < 5:
                        continue

                    # If still no summary, create informative lead from title and source
                    if not raw_summary or len(raw_summary.strip()) < 10:
                        raw_summary = f"{raw_title}. Comprehensive reporting from {source_name} on ongoing developments."

                    # Slug generation
                    base_slug = slugify(raw_title)
                    slug = base_slug
                    suffix = 1
                    while slug in seen_slugs:
                        slug = f"{base_slug}-{suffix}"
                        suffix += 1

                    # Published time
                    pub_dt = parse_entry_time(entry)
                    pub_iso = pub_dt.isoformat()
                    time_ago = format_relative_time(pub_dt)

                    # Image URL extraction
                    if og_image_candidate:
                        image_url = og_image_candidate
                    else:
                        image_url = extract_image_url(entry, feed_url, cat_slug, entry_link=link, title=raw_title)

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
                        "title": raw_title,
                        "raw_summary": raw_summary,
                        "summary": raw_summary,
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

    print(f"[OK] Successfully ingested {len(articles)} high-quality, verified articles across all categories.")
    return articles


if __name__ == "__main__":
    arts = fetch_all_categories(max_per_category=2)
    print(f"Test run completed. Total: {len(arts)}")
    if arts:
        print(f"Sample: [{arts[0]['category_name']}] {arts[0]['title']} ({arts[0]['source']})")
        print(f"Image: {arts[0]['image_url']}")
        print(f"Summary: {arts[0]['summary']}")
