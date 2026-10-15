"""
NewsSeconds - IndexNow Submitter
Instantly notifies search engines (Microsoft Bing, Yandex, Seznam, Naver)
when fresh news summaries and Google AMP stories are published or updated.
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config


def ensure_indexnow_key_file() -> Path:
    """Ensures the IndexNow verification key file exists in dist/ and static/."""
    key = getattr(config, "INDEXNOW_KEY", "b4f910a2d3e54c7b89f0123456789abc")
    key_filename = f"{key}.txt"

    # Save in static (source)
    static_key_path = config.STATIC_DIR / key_filename
    static_key_path.parent.mkdir(parents=True, exist_ok=True)
    static_key_path.write_text(key, encoding="utf-8")

    # Save in dist (deployed root)
    dist_key_path = config.DIST_DIR / key_filename
    dist_key_path.parent.mkdir(parents=True, exist_ok=True)
    dist_key_path.write_text(key, encoding="utf-8")

    return dist_key_path


def get_all_story_urls(limit: int = 100) -> List[str]:
    """Retrieves the list of story URLs from dist/api/articles.json or data/articles.json."""
    urls = [f"{config.SITE_URL}/"]

    source_file = config.DIST_DIR / "api" / "articles.json"
    if not source_file.exists():
        source_file = config.DATA_DIR / "articles.json"

    if source_file.exists():
        try:
            data = json.loads(source_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data[:limit]:
                    slug = item.get("slug")
                    if slug:
                        urls.append(f"{config.SITE_URL}/stories/{slug}/")
        except Exception as e:
            print(f"[!] Warning reading articles for IndexNow: {e}")

    return urls


def submit_to_indexnow(urls: Optional[List[str]] = None, key: str = None) -> bool:
    """
    Submits URLs to the IndexNow protocol (shared by Bing, Yandex, etc.).
    """
    key = key or getattr(config, "INDEXNOW_KEY", "b4f910a2d3e54c7b89f0123456789abc")
    ensure_indexnow_key_file()

    if urls is None:
        urls = get_all_story_urls(limit=80)

    if not urls:
        print("[!] IndexNow: No URLs to submit.")
        return False

    host = config.SITE_URL.replace("https://", "").replace("http://", "").split("/")[0]

    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{config.SITE_URL}/{key}.txt",
        "urlList": urls
    }

    data_bytes = json.dumps(payload, indent=2).encode("utf-8")

    endpoints = [
        ("Bing", "https://api.indexnow.org/IndexNow"),
        ("Yandex", "https://yandex.com/indexnow"),
    ]

    success = False
    for engine_name, endpoint in endpoints:
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "NewsSeconds-IndexNow-Bot/1.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                if status_code in (200, 202):
                    print(f"[OK] IndexNow submitted {len(urls)} URLs to {engine_name} (HTTP {status_code})")
                    success = True
                else:
                    print(f"[!] IndexNow received HTTP {status_code} from {engine_name}")
        except urllib.error.HTTPError as e:
            if e.code == 202:
                print(f"[OK] IndexNow accepted {len(urls)} URLs by {engine_name} (HTTP 202)")
                success = True
            else:
                print(f"[!] IndexNow HTTPError {e.code} ({engine_name}): {e.reason}")
        except Exception as e:
            print(f"[!] IndexNow error connecting to {engine_name}: {e}")

    return success


if __name__ == "__main__":
    submit_to_indexnow()
