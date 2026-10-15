"""
NewsSeconds - RSS & Google WebSub Syndication Pinger
Notifies Google WebSub / PubSubHubbub hub, Google Sitemap Ping, and global RSS aggregators
(Feedly, Flipboard, Bing News) whenever fresh news stories are generated.
"""

import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config


def ping_websub_hub(feed_url: str = f"{config.SITE_URL}/news-sitemap.xml") -> bool:
    """
    Pings the official Google WebSub hub (pubsubhubbub.appspot.com)
    to notify search engines that fresh news content has been published.
    """
    hub_url = "https://pubsubhubbub.appspot.com/"
    post_data = urllib.parse.urlencode({
        "hub.mode": "publish",
        "hub.url": feed_url,
    }).encode("utf-8")

    req = urllib.request.Request(
        hub_url,
        data=post_data,
        headers={
            "User-Agent": "NewsSeconds-WebSub-Publisher/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status in (200, 204):
                print(f"[OK] Google WebSub Hub Ping Success (HTTP {status}) for: {feed_url}")
                return True
            else:
                print(f"[!] WebSub Hub HTTP {status} for: {feed_url}")
                return False
    except Exception as e:
        print(f"[!] WebSub Hub ping note for {feed_url}: {e}")
        return False


def ping_pingomatic() -> bool:
    """
    Pings Ping-O-Matic to broadcast fresh news updates to global aggregators.
    """
    endpoint = "http://pingomatic.com/ping/"
    params = {
        "title": config.SITE_NAME,
        "blogurl": f"{config.SITE_URL}/",
        "rssurl": f"{config.SITE_URL}/news-sitemap.xml",
        "chk_weblogscom": "on",
        "chk_blogs": "on",
        "chk_feedburner": "on",
        "chk_syndic8": "on",
        "chk_newsgator": "on",
        "chk_myyahoo": "on",
        "chk_pubsubcom": "on",
        "chk_blogdigger": "on",
    }
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NewsSeconds-RSS-Agent/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status == 200:
                print(f"[OK] Ping-O-Matic Global Syndication Success (HTTP 200)")
                return True
            return False
    except Exception as e:
        print(f"[!] Ping-O-Matic ping notice: {e}")
        return False


def ping_all_search_engines():
    """Pings both Google WebSub and global syndication hubs."""
    print("\n[⚡] Broadcasting instant updates to Google WebSub & Search Aggregators...")
    ping_websub_hub(f"{config.SITE_URL}/news-sitemap.xml")
    ping_websub_hub(f"{config.SITE_URL}/sitemap.xml")
    ping_pingomatic()


if __name__ == "__main__":
    ping_all_search_engines()
