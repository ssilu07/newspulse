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
        "trending": "#BreakingNews #TrendingNow #ViralNews #NewsPulse",
        "tech": "#TechNews #Technology #Gadgets #SiliconValley #Innovation",
        "ai-future": "#ArtificialIntelligence #AI #MachineLearning #TechTrends #GenAI",
        "business": "#BusinessNews #StockMarket #Crypto #Economy #Finance",
        "world": "#WorldNews #GlobalNews #Geopolitics #Breaking",
        "sports": "#SportsNews #Cricket #Football #Scores #MatchDay",
        "entertainment": "#Entertainment #Cinema #Movies #Gaming #PopCulture"
    }
    return tags.get(category, "#NewsPulse #BreakingNews #DailyNews")


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
# Main Dispatcher
# ==============================================================================
def auto_share_top_articles(articles: list = None, max_posts: int = None) -> dict:
    """
    Selects top breaking articles that have not yet been posted to social media
    and broadcasts them across Twitter, Reddit, Telegram, and LinkedIn.
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

        if not (need_twitter or need_reddit or need_telegram or need_linkedin):
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
