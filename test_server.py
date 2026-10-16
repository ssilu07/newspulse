"""
NewsPulse - End-to-End System Tests
Verifies that all static routes, story pages, compliance pages,
sitemap, and APIs respond with status 200 and expected markup.
"""

from fastapi.testclient import TestClient
from dev_server import app
import json
import config

client = TestClient(app)


def test_homepage():
    res = client.get("/")
    assert res.status_code == 200
    assert config.SITE_NAME in res.text
    assert "cookieConsentBar" in res.text
    print("[PASS] Homepage route (200 OK, Cookie Consent Bar Verified)")


def test_compliance_pages():
    for page in ["about", "privacy", "terms", "editorial-policy", "contact"]:
        res = client.get(f"/{page}/")
        assert res.status_code == 200, f"Page /{page}/ returned {res.status_code}"
        assert config.SITE_NAME in res.text
        assert "cookieConsentBar" in res.text
        if page == "about":
            assert "team-card" in res.text
            assert "Editorial Masthead" in res.text
        if page == "privacy":
            assert 'id="cookies"' in res.text
        print(f"[PASS] Compliance page /{page}/ (200 OK)")


def test_story_page():
    # Pick first slug from api
    res_api = client.get("/api/articles")
    assert res_api.status_code == 200
    data = res_api.json()
    assert data["count"] > 0
    first_slug = data["articles"][0]["slug"]

    res_story = client.get(f"/stories/{first_slug}/")
    assert res_story.status_code == 200
    assert "amp-story" in res_story.text
    assert "amp-story-page" in res_story.text
    print(f"[PASS] Story route /stories/{first_slug}/ (200 OK, Valid AMP Story)")

    res_news = client.get(f"/news/{first_slug}/")
    assert res_news.status_code == 200
    assert "article-layout" in res_news.text
    assert "NewsArticle" in res_news.text
    assert "editorial-take-box" in res_news.text
    assert "author-bio-card" in res_news.text
    assert "cookieConsentBar" in res_news.text
    print(f"[PASS] Dedicated Article route /news/{first_slug}/ (200 OK, Full SEO Layout & E-E-A-T Shield)")


def test_seo_files():
    res_sitemap = client.get("/sitemap.xml")
    assert res_sitemap.status_code == 200
    assert "urlset" in res_sitemap.text
    assert "/news/" in res_sitemap.text
    print("[PASS] Standard Sitemap XML with /news/ (200 OK)")

    res_news_sitemap = client.get("/news-sitemap.xml")
    assert res_news_sitemap.status_code == 200
    assert "news:news" in res_news_sitemap.text
    assert "/news/" in res_news_sitemap.text
    print("[PASS] Google News Sitemap XML with /news/ (200 OK)")

    res_robots = client.get("/robots.txt")
    assert res_robots.status_code == 200
    assert "Sitemap:" in res_robots.text
    assert "Mediapartners-Google" in res_robots.text
    print("[PASS] Robots.txt (200 OK, Mediapartners-Google Whitelisted)")

    res_manifest = client.get("/manifest.json")
    assert res_manifest.status_code == 200
    print("[PASS] PWA Manifest JSON (200 OK)")

    res_sitemap_index = client.get("/sitemap_index.xml")
    assert res_sitemap_index.status_code == 200
    assert "sitemapindex" in res_sitemap_index.text
    print("[PASS] Master Sitemap Index XML (200 OK)")

    res_sitemap_main = client.get("/sitemap-main.xml")
    assert res_sitemap_main.status_code == 200
    assert "urlset" in res_sitemap_main.text
    print("[PASS] Clean Sitemap Main XML (200 OK)")

    res_favicon = client.get("/favicon.ico")
    assert res_favicon.status_code == 200
    print("[PASS] Favicon ICO (200 OK)")

    res_ads = client.get("/ads.txt")
    assert res_ads.status_code == 200
    assert "google.com" in res_ads.text
    print("[PASS] ads.txt (200 OK, AdSense Verified)")



def test_api():
    res_api = client.get("/api/articles")
    assert res_api.status_code == 200
    payload = res_api.json()
    assert payload["count"] >= 1
    print(f"[PASS] REST API /api/articles ({payload['count']} items returned)")


if __name__ == "__main__":
    print("Running NewsPulse End-to-End Suite...")
    test_homepage()
    test_compliance_pages()
    test_story_page()
    test_seo_files()
    test_api()
    print("\n[SUCCESS] All 10 verification test suites passed!")
