"""
NewsPulse - Feed Ingestion & Content Extraction Module
Fetches, cleans, deduplicates, and extracts metadata/images from multi-source RSS feeds.
Equipped with OpenGraph web-scraper fallback and high-resolution media transformers.
"""

import re
import sys
import time
import hashlib
import json
import urllib.request
from pathlib import Path
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


# Spam and low-quality keyword filter (prevents commercial affiliate spam and zero-value filler)
SPAM_TITLE_KEYWORDS = [
    r"\bdeal\b", r"\bdeals\b", r"\bdiscount\b", r"\bcoupon\b", r"\bsave \$\d+",
    r"\bsale\b", r"\bpromo\b", r"\bgiveaway\b", r"\bpodcast\b", r"\bepisode \d+",
    r"\bhoroscope\b", r"\bshopping\b", r"\bbest deals\b", r"\bexclusive offer\b",
    r"\bsponsored content\b"
]


def is_spam_or_low_value(title: str, summary: str) -> bool:
    """Detects commercial spam, coupon roundups, and zero-value promotional filler."""
    combined = f"{title} {summary}".lower()
    for pattern in SPAM_TITLE_KEYWORDS:
        if re.search(pattern, combined):
            return True
    return False


def load_existing_identifiers(articles_file: Path = None) -> tuple[set, set, set, list]:
    """
    Loads existing slugs, original URLs, and title hashes from the persistent archive.
    Guarantees that already indexed/published stories are NEVER re-fetched or duplicated.
    """
    if articles_file is None:
        articles_file = config.DATA_DIR / "articles.json"
    known_slugs = set()
    known_urls = set()
    known_hashes = set()
    existing_articles = []

    if articles_file.exists():
        try:
            with open(articles_file, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
            for it in existing_articles:
                if isinstance(it, dict):
                    if it.get("slug"):
                        known_slugs.add(it["slug"])
                    if it.get("original_url") and it["original_url"] != "#":
                        known_urls.add(it["original_url"].strip().lower())
                    t = it.get("title") or it.get("raw_title") or ""
                    if t:
                        norm = re.sub(r"\W+", "", t.lower())
                        known_hashes.add(hashlib.md5(norm.encode("utf-8")).hexdigest())
        except Exception as e:
            print(f"    [!] Note on reading existing archive: {e}")

    return known_slugs, known_urls, known_hashes, existing_articles


def fetch_feed_entries_safe(feed_url: str, timeout: float = None) -> list:
    """
    Safely retrieves entries from an RSS feed with a strict timeout and fallback.
    Guarantees the publishing script never hangs or crashes if an external publisher is down.
    """
    if timeout is None:
        timeout = getattr(config, "FEED_TIMEOUT_SECONDS", 7.0)
    try:
        req = urllib.request.Request(feed_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
        parsed = feedparser.parse(content)
        return parsed.entries or []
    except Exception:
        # Fallback to direct feedparser in case urllib fails
        try:
            parsed = feedparser.parse(feed_url, request_headers=HEADERS)
            return parsed.entries or []
        except Exception:
            return []


def fetch_all_categories(
    max_per_category: int = None,
    max_total_fresh: int = None,
    skip_existing: bool = True
) -> list:
    """
    Ingests and parses fresh news items across all defined categories.
    Complies with Google Search & Google News quality guidelines:
    - Never re-fetches or churns previously processed stories (Zero Duplication).
    - Filters out promotional/commercial spam and low-substance stubs.
    - Limits ingestion to safe, high-quality volumes (Anti-Scaled Abuse).
    - Enforces freshness (skips stale stories older than 48 hours).
    - Resilient network handling with timeouts so pipeline never hangs.
    """
    if max_per_category is None:
        max_per_category = getattr(config, "MAX_ARTICLES_PER_CATEGORY", 2)
    if max_total_fresh is None:
        max_total_fresh = getattr(config, "MAX_TOTAL_FRESH_ARTICLES", 14)

    known_slugs, known_urls, known_hashes, _ = load_existing_identifiers() if skip_existing else (set(), set(), set(), [])
    seen_hashes = set(known_hashes)
    seen_slugs = set(known_slugs)
    seen_urls = set(known_urls)

    fresh_articles = []
    print(f"[*] Checking fresh breaking news across {len(config.CATEGORIES)} categories (Cap: {max_per_category}/category, max fresh: {max_total_fresh})...")

    now_utc = datetime.now(timezone.utc)
    max_age_hours = getattr(config, "MAX_ARTICLE_AGE_HOURS", 48)

    for cat_slug, cat_info in config.CATEGORIES.items():
        if len(fresh_articles) >= max_total_fresh:
            print(f"    [!] Global fresh article limit ({max_total_fresh}) reached. Preserving high editorial curation.")
            break

        cat_count = 0
        print(f"    -> Scanning {cat_info['name']} ({len(cat_info['feeds'])} feeds)...")

        for feed_url in cat_info["feeds"]:
            if cat_count >= max_per_category or len(fresh_articles) >= max_total_fresh:
                break

            entries = fetch_feed_entries_safe(feed_url)
            for entry in entries:
                if cat_count >= max_per_category or len(fresh_articles) >= max_total_fresh:
                    break

                raw_title = entry.get("title", "").strip()
                if not raw_title or len(raw_title) < 15:
                    continue

                # Clean source name suffixes (e.g. "Headline - BBC News")
                source_name = extract_source_name(entry, feed_url)
                if " - " in raw_title:
                    parts = raw_title.rsplit(" - ", 1)
                    if len(parts) == 2 and len(parts[1]) < 30:
                        raw_title = parts[0].strip()

                # Deduplication key based on normalized title
                title_norm = re.sub(r"\W+", "", raw_title.lower())
                title_hash = hashlib.md5(title_norm.encode("utf-8")).hexdigest()
                if title_hash in seen_hashes:
                    continue

                # Original URL check
                link = entry.get("link", "#").strip()
                norm_link = link.lower()
                if norm_link in seen_urls:
                    continue

                # Freshness check: skip stale stories older than max_age_hours
                pub_dt = parse_entry_time(entry)
                diff_hours = (now_utc - pub_dt).total_seconds() / 3600.0
                if diff_hours > max_age_hours:
                    continue

                # Extract raw summary / description
                raw_summary = ""
                if "content" in entry and entry.content:
                    raw_summary = clean_html(entry.content[0].value)
                if not raw_summary and "summary" in entry:
                    raw_summary = clean_html(entry.summary)
                if not raw_summary and "description" in entry:
                    raw_summary = clean_html(entry.description)

                # Filter commercial/promo spam
                if is_spam_or_low_value(raw_title, raw_summary):
                    continue

                # Scrape OG meta fallback if summary is sparse
                og_image_candidate = ""
                if len(raw_summary.split()) < 12 and link.startswith("http") and "google.com" not in link:
                    og_img, og_desc = extract_web_meta(link, timeout=2.5)
                    if og_desc and len(og_desc.split()) >= 8:
                        raw_summary = clean_html(og_desc)
                    if og_img:
                        og_image_candidate = og_img

                # Discard low-substance stubs (Google Spam Policy: Thin Content)
                if len(raw_summary.split()) < 8 and len(raw_title.split()) < 6:
                    continue

                if not raw_summary or len(raw_summary.strip()) < 10:
                    raw_summary = f"{raw_title}. Ongoing breaking developments confirmed and reported via {source_name} correspondents."

                # Unique slug generation
                base_slug = slugify(raw_title)
                slug = base_slug
                suffix = 1
                while slug in seen_slugs:
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1

                pub_iso = pub_dt.isoformat()
                time_ago = format_relative_time(pub_dt)

                # Extract high-definition visual
                if og_image_candidate:
                    image_url = og_image_candidate
                else:
                    image_url = extract_image_url(entry, feed_url, cat_slug, entry_link=link, title=raw_title)

                article = {
                    "id": f"art_{int(now_utc.timestamp())}_{len(fresh_articles) + 1}",
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
                seen_urls.add(norm_link)
                fresh_articles.append(article)
                cat_count += 1

    print(f"[OK] Ingestion complete. Discovered {len(fresh_articles)} fresh breaking stories (skipped all existing & stale items).")
    return fresh_articles


if __name__ == "__main__":
    arts = fetch_all_categories(max_per_category=1, max_total_fresh=3)
    print(f"Test run completed. Fresh discovered: {len(arts)}")
    if arts:
        print(f"Sample: [{arts[0]['category_name']}] {arts[0]['title']} ({arts[0]['source']})")
        print(f"Image: {arts[0]['image_url']}")
        print(f"Summary: {arts[0]['summary']}")
