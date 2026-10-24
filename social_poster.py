"""
NewsPulse - Automated Social Media Syndication Engine (social_poster.py)
Automatically publishes top breaking news summaries & Web Story links to:
1. X (Twitter) via Tweepy (API v2)
2. Reddit via PRAW
3. Telegram Channels via Telegram Bot API (Instant & 100% Free)

Tracks posted stories in data/posted_social.json to prevent duplicate posts.
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HISTORY_FILE = config.DATA_DIR / "posted_social.json"


def load_posted_history() -> dict:
    """Loads social posting history to avoid duplicate shares."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_posted_history(history: dict):
    """Persists social posting history."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[!] Warning: Could not save social history: {e}")


def get_category_hashtags(category: str) -> str:
    """Generates viral hashtags based on topic."""
    tags = {
        "world": "#EV #ElectricVehicles #Tesla #CleanMobility #BatteryTech #NewsSeconds",
        "tech": "#Supercars #Hypercars #Ferrari #Porsche #Lamborghini #CarPorn #NewsSeconds",
        "ai-future": "#AutonomousDriving #TeslaFSD #Waymo #RoboTaxi #FutureMobility #AutoTech",
        "business": "#AutoIndustry #Automotive #Gigafactory #CarNews #EVNews",
        "trending": "#ConceptCar #CarCulture #Hypercar #ViralCars #NewsSeconds",
        "sports": "#Formula1 #F1 #Motorsport #LeMans #RacingTech #GrandPrix",
        "entertainment": "#CarCulture #Restomod #ClassicCars #VintageCars #Gearhead"
    }
    return tags.get(category, "#Cars #EV #Supercars #Automotive #NewsSeconds")


# ==============================================================================
# 1. X (Twitter) Auto-Poster
# ==============================================================================
def post_to_twitter(article: dict) -> bool:
    """Publishes a high-CTR concise tweet with Web Story link."""
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("    [X/Twitter] Credentials not fully configured in environment. Skipping.")
        return False

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        title = article.get("title", "").strip()
        slug = article.get("slug", "")
        cat_slug = article.get("category", "trending")
        story_url = f"{config.SITE_URL}/stories/{slug}/"
        hashtags = get_category_hashtags(cat_slug)

        # Max tweet length is 280 characters
        # Reserve ~30 chars for link and ~40 for hashtags
        max_title_len = 180
        if len(title) > max_title_len:
            title = title[:max_title_len - 3] + "..."

        tweet_text = f"⚡ {title}\n\n👉 Read 60-Sec Story: {story_url}\n\n{hashtags}"

        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data.get("id") if response and response.data else "success"
        print(f"    [X/Twitter] Posted successfully! Tweet ID: {tweet_id}")
        return True

    except Exception as e:
        print(f"    [!] X/Twitter posting error: {e}")
        return False


# ==============================================================================
# 2. Reddit Auto-Poster
# ==============================================================================
def post_to_reddit(article: dict) -> bool:
    """Submits a formatted news summary with bullet points to Reddit."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    user_agent = os.getenv("REDDIT_USER_AGENT", f"NewsPulseBot:v1.0 (by /u/{username or 'anonymous'})")

    if not all([client_id, client_secret, username, password]):
        print("    [Reddit] Credentials not configured in environment. Skipping.")
        return False

    # Default to user's personal subreddit or specified target
    target_subreddit = os.getenv("REDDIT_SUBREDDIT", f"u_{username}")

    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )

        title = article.get("title", "").strip()
        summary = article.get("summary", "").strip()
        bullets = article.get("bullet_points", [])
        slug = article.get("slug", "")
        source = article.get("source", "NewsPulse")
        orig_url = article.get("original_url", "#")
        story_url = f"{config.SITE_URL}/stories/{slug}/"

        bullet_str = "\n".join([f"- {b}" for b in bullets]) if bullets else f"- {summary}"

        post_body = f"""**Summary:** {summary}

**Key Takeaways:**
{bullet_str}

---
⚡ **Read the 5-Slide Visual Web Story:** [{title}]({story_url})  
📰 **Original Source:** [{source}]({orig_url})  
*Curated automatically by NewsPulse Media Network.*
"""

        subreddit = reddit.subreddit(target_subreddit)
        submission = subreddit.submit(title=title, selftext=post_body)
        print(f"    [Reddit] Posted successfully to r/{target_subreddit}: {submission.url}")
        return True

    except Exception as e:
        print(f"    [!] Reddit posting error: {e}")
        return False


# ==============================================================================
# 3. Telegram Channel Auto-Poster (100% Free & No Rate Limits)
# ==============================================================================
def post_to_telegram(article: dict) -> bool:
    """Sends a rich instant news card to a Telegram channel or group."""
    if not getattr(config, "ENABLE_TELEGRAM_POSTING", False):
        print("    [Telegram] Auto-posting is paused/disabled. Skipping.")
        return False

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("    [Telegram] Bot token or Chat ID not configured. Skipping.")
        return False

    try:
        import requests
        title = article.get("title", "").strip()
        summary = article.get("summary", "").strip()
        slug = article.get("slug", "")
        source = article.get("source", "NewsPulse")
        story_url = f"{config.SITE_URL}/stories/{slug}/"

        caption = (
            f"⚡ <b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"📰 <i>Source: {source}</i>\n"
            f"👉 <a href=\"{story_url}\"><b>Open 5-Slide Visual Story</b></a>"
        )

        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        res = requests.post(api_url, json=payload, timeout=10)
        if res.status_code == 200:
            print("    [Telegram] Posted successfully to Telegram Channel!")
            return True
        else:
            print(f"    [!] Telegram error response ({res.status_code}): {res.text}")
            return False

    except Exception as e:
        print(f"    [!] Telegram posting error: {e}")
        return False


# ==============================================
# 4. LinkedIn Auto-Poster (Professional & High Organic Reach)
# ==============================================
def post_to_linkedin(article: dict) -> bool:
    """Publishes an article share with commentary to a LinkedIn profile or company page."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN") or os.getenv("LINKEDIN_ORG_URN")

    if not access_token or not person_urn:
        print("    [LinkedIn] Access Token or Person/Org URN not configured in environment. Skipping.")
        return False

    try:
        import requests
        title = article.get("title", "").strip()
        summary = article.get("summary", "").strip()
        slug = article.get("slug", "")
        cat_slug = article.get("category", "tech")
        source = article.get("source", "NewsPulse")
        story_url = f"{config.SITE_URL}/stories/{slug}/"
        hashtags = get_category_hashtags(cat_slug)

        author_urn = person_urn if person_urn.startswith("urn:li:") else f"urn:li:person:{person_urn}"

        commentary = (
            f"⚡ {title}\n\n"
            f"{summary}\n\n"
            f"Read the full 5-slide visual story: {story_url}\n\n"
            f"{hashtags}"
        )

        api_url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": commentary
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": summary[:200]
                            },
                            "originalUrl": story_url,
                            "title": {
                                "text": title[:200]
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        res = requests.post(api_url, headers=headers, json=payload, timeout=12)
        if res.status_code in (200, 201):
            print("    [LinkedIn] Posted successfully to LinkedIn!")
            return True
        else:
            print(f"    [!] LinkedIn error response ({res.status_code}): {res.text}")
            return False

    except Exception as e:
        print(f"    [!] LinkedIn posting error: {e}")
        return False


# ==============================================================================
# 5. Tumblr Auto-Poster (100% Free - Organic Traffic & SEO Backlinks)
# ==============================================================================
def get_tumblr_tags(category: str) -> str:
    """Returns comma-separated tags tailored for Tumblr discovery."""
    tags_map = {
        "world": "EV, Electric Vehicles, Tesla, Clean Energy, Battery Tech, NewsSeconds, Cars",
        "tech": "Supercars, Hypercars, Ferrari, Porsche, Lamborghini, Sports Cars, Automotive",
        "ai-future": "Autonomous Driving, Tesla FSD, RoboTaxi, Future Mobility, Auto Tech",
        "business": "Auto Industry, Cars, Electric Cars, Automotive News, Gigafactory, Business",
        "trending": "Concept Cars, Hypercar, Supercar, Auto Show, Custom Cars, NewsSeconds",
        "sports": "Formula 1, F1, Motorsport, Racing, Grand Prix, Le Mans, Speed",
        "entertainment": "Car Culture, Restomod, Classic Cars, Vintage Cars, Automobiles, V8"
    }
    return tags_map.get(category, "Cars, Supercars, EV, Automotive, NewsSeconds")


def post_to_tumblr(article: dict) -> bool:
    """
    Publishes a high-CTR visual Photo Post with hero image, caption, and Web Story link to Tumblr.
    Uses Tumblr API v2 with OAuth 1.0a.
    Prioritizes Native Photo Posts so the image renders large, full-width, and clickable in user feeds.
    """
    if not getattr(config, "ENABLE_TUMBLR_POSTING", True):
        print("    [Tumblr] Auto-posting is disabled in config. Skipping.")
        return False

    consumer_key = os.getenv("TUMBLR_CONSUMER_KEY")
    consumer_secret = os.getenv("TUMBLR_CONSUMER_SECRET")
    oauth_token = os.getenv("TUMBLR_OAUTH_TOKEN")
    oauth_secret = os.getenv("TUMBLR_OAUTH_SECRET")
    blog_name = os.getenv("TUMBLR_BLOG_NAME")

    if not all([consumer_key, consumer_secret, oauth_token, oauth_secret, blog_name]):
        print("    [Tumblr] Credentials or blog name not fully configured in environment. Skipping.")
        return False

    # Clean blog name (remove http:// or https:// or trailing slashes)
    blog_identifier = blog_name.strip()
    blog_identifier = re.sub(r"^https?://", "", blog_identifier).rstrip("/")

    try:
        from requests_oauthlib import OAuth1
        import requests
        from html import escape

        auth = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret
        )

        title = article.get("title", "").strip()
        summary = article.get("summary", "").strip()
        bullets = article.get("bullet_points", [])
        slug = article.get("slug", "")
        category = article.get("category", "trending")
        source = article.get("source", "NewsPulse")
        orig_url = article.get("original_url", "#")
        story_url = f"{config.SITE_URL}/stories/{slug}/"
        tags_str = get_tumblr_tags(category)

        # Bullet points formatted for HTML caption
        if bullets:
            bullet_html = "".join([f"• {escape(b)}<br>" for b in bullets])
        else:
            bullet_html = f"• {escape(summary)}<br>"

        # Rich, eye-catching HTML caption underneath the image
        caption_html = (
            f"<h3>⚡ {escape(title)}</h3>"
            f"<p>{escape(summary)}</p>"
            f"<p><b>📌 Key Takeaways:</b><br>{bullet_html}</p>"
            f"<hr>"
            f"<p>👉 <a href=\"{story_url}\"><b>Open 5-Slide Visual Web Story</b></a></p>"
            f"<p>📰 <i>Source: {escape(source)}</i> • Curated by <a href=\"{config.SITE_URL}\">{escape(config.SITE_NAME)}</a></p>"
        )

        # 1. Resolve Best Image (Remote URL or Category Fallback)
        image_url = article.get("image_url", "").strip()
        if not image_url or not image_url.startswith("http"):
            cat_info = config.CATEGORIES.get(category, {})
            image_url = cat_info.get("default_image", "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1600&h=900&fit=crop")

        api_url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/post"

        # Attempt 1: Native Photo Post via URL (Tumblr auto-caches & optimizes on their CDN)
        photo_payload = {
            "type": "photo",
            "state": "published",
            "source": image_url,
            "caption": caption_html,
            "link": story_url,  # Clicking image opens the web story directly
            "tags": tags_str,
            "slug": slug
        }

        response = requests.post(api_url, data=photo_payload, auth=auth, timeout=20)
        if response.status_code in (200, 201):
            res_data = response.json()
            post_id = res_data.get("response", {}).get("id_string") or res_data.get("response", {}).get("id")
            print(f"    [Tumblr] Visual Photo Post published to {blog_identifier}! Post ID: {post_id}")
            return True

        # Attempt 2: If remote source URL fails (e.g. anti-hotlink block), upload local image file
        print(f"    [Tumblr] Source URL photo attempt returned {response.status_code}. Trying local image file upload...")
        local_cover = config.DIST_DIR / "stories" / slug / "cover-16x9.jpg"
        if not local_cover.exists():
            local_cover = config.STATIC_DIR / "assets" / "posters" / category / "cover-16x9.jpg"

        if local_cover.exists():
            with open(local_cover, "rb") as img_f:
                upload_payload = {
                    "type": "photo",
                    "state": "published",
                    "caption": caption_html,
                    "link": story_url,
                    "tags": tags_str,
                    "slug": slug
                }
                files = {"data": img_f}
                file_response = requests.post(api_url, data=upload_payload, files=files, auth=auth, timeout=30)
                if file_response.status_code in (200, 201):
                    res_data = file_response.json()
                    post_id = res_data.get("response", {}).get("id_string") or res_data.get("response", {}).get("id")
                    print(f"    [Tumblr] Local image Photo Post published to {blog_identifier}! Post ID: {post_id}")
                    return True

        # Attempt 3: Fallback to HTML Text Post with embedded image if photo endpoints reject
        print(f"    [Tumblr] Falling back to structured text post...")
        text_body = (
            f"<p><img src=\"{image_url}\" style=\"max-width:100%; border-radius:8px;\"></p>\n"
            f"{caption_html}"
        )
        text_payload = {
            "type": "text",
            "state": "published",
            "title": title,
            "body": text_body,
            "format": "html",
            "tags": tags_str,
            "slug": slug
        }
        res_text = requests.post(api_url, data=text_payload, auth=auth, timeout=15)
        if res_text.status_code in (200, 201):
            res_data = res_text.json()
            post_id = res_data.get("response", {}).get("id_string") or res_data.get("response", {}).get("id")
            print(f"    [Tumblr] Fallback post published to {blog_identifier}! Post ID: {post_id}")
            return True
        else:
            print(f"    [!] Tumblr error response ({res_text.status_code}): {res_text.text}")
            return False

    except Exception as e:
        print(f"    [!] Tumblr posting error: {e}")
        return False


# ==============================================================================
# Main Dispatcher
# ==============================================================================
def auto_share_top_articles(articles: list = None, max_posts: int = None) -> dict:
    """
    Selects top breaking articles that have not yet been posted to social media
    and broadcasts them across Twitter, Reddit, Telegram, LinkedIn, and Tumblr.
    Enforces safe anti-spam rate limits and delays between posts.
    """
    if max_posts is None:
        max_posts = getattr(config, "SOCIAL_MAX_POSTS_PER_RUN", 2)

    if not articles:
        articles_file = config.DATA_DIR / "articles.json"
        if not articles_file.exists():
            print("[Social Poster] No articles found to share.")
            return {"shared": 0}
        try:
            articles = json.loads(articles_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[!] Could not load articles: {e}")
            return {"shared": 0}

    history = load_posted_history()
    shared_count = 0
    post_delay = getattr(config, "SOCIAL_POST_DELAY_SECONDS", 6.0)

    print(f"\n[Social Auto-Poster] Reviewing top {len(articles)} articles for safe broadcast (Cap: {max_posts})...")

    for art in articles:
        if shared_count >= max_posts:
            break

        slug = art.get("slug", "")
        if not slug:
            continue

        art_history = history.get(slug, {})

        # Check enabled platforms based on config toggles
        need_twitter = getattr(config, "ENABLE_TWITTER_POSTING", True) and not art_history.get("twitter", False)
        need_reddit = getattr(config, "ENABLE_REDDIT_POSTING", True) and not art_history.get("reddit", False)
        need_telegram = getattr(config, "ENABLE_TELEGRAM_POSTING", False) and not art_history.get("telegram", False)
        need_linkedin = getattr(config, "ENABLE_LINKEDIN_POSTING", True) and not art_history.get("linkedin", False)
        need_tumblr = getattr(config, "ENABLE_TUMBLR_POSTING", True) and not art_history.get("tumblr", False)

        if not (need_twitter or need_reddit or need_telegram or need_linkedin or need_tumblr):
            continue

        print(f"\n[*] Broadcasting: '{art.get('title', '')[:55]}...'")

        if need_twitter:
            try:
                tw_ok = post_to_twitter(art)
                if tw_ok:
                    art_history["twitter"] = True
            except Exception as e:
                print(f"    [!] Twitter broadcast error (non-fatal): {e}")

        if need_reddit:
            try:
                rd_ok = post_to_reddit(art)
                if rd_ok:
                    art_history["reddit"] = True
            except Exception as e:
                print(f"    [!] Reddit broadcast error (non-fatal): {e}")

        if need_telegram:
            try:
                tg_ok = post_to_telegram(art)
                if tg_ok:
                    art_history["telegram"] = True
            except Exception as e:
                print(f"    [!] Telegram broadcast error (non-fatal): {e}")

        if need_linkedin:
            try:
                li_ok = post_to_linkedin(art)
                if li_ok:
                    art_history["linkedin"] = True
            except Exception as e:
                print(f"    [!] LinkedIn broadcast error (non-fatal): {e}")

        if need_tumblr:
            try:
                tb_ok = post_to_tumblr(art)
                if tb_ok:
                    art_history["tumblr"] = True
            except Exception as e:
                print(f"    [!] Tumblr broadcast error (non-fatal): {e}")

        art_history["last_posted_at"] = datetime.now(timezone.utc).isoformat()
        history[slug] = art_history
        shared_count += 1

        # Anti-spam delay between social shares to prevent bot detection
        if shared_count < max_posts and post_delay > 0:
            time.sleep(post_delay)

    save_posted_history(history)
    print(f"[Social Auto-Poster] Finished broadcast cycle. Total stories processed: {shared_count}")
    return {"shared": shared_count}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NewsPulse Social Auto-Poster")
    parser.add_argument("--limit", type=int, default=2, help="Number of top stories to broadcast")
    args = parser.parse_args()

    auto_share_top_articles(max_posts=args.limit)
