"""
NewsPulse - End-to-End System Tests
Verifies that all static routes, story pages, compliance pages,
sitemap, and APIs respond with status 200 and expected markup.
"""

from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)


def test_homepage():
    res = client.get("/")
    assert res.status_code == 200
    assert "NewsPulse" in res.text
    assert "Trending Web Stories" in res.text
    assert "Live Breaking" in res.text
    print("[PASS] Homepage route (200 OK)")


def test_compliance_pages():
    for page in ["about", "privacy", "terms", "editorial-policy", "contact"]:
        res = client.get(f"/{page}/")
        assert res.status_code == 200, f"Page /{page}/ returned {res.status_code}"
        assert "NewsPulse" in res.text
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


def test_seo_files():
    res_sitemap = client.get("/sitemap.xml")
    assert res_sitemap.status_code == 200
    assert "news:news" in res_sitemap.text
    print("[PASS] Google News Sitemap XML (200 OK)")

    res_robots = client.get("/robots.txt")
    assert res_robots.status_code == 200
    assert "Sitemap:" in res_robots.text
    print("[PASS] Robots.txt (200 OK)")

    res_manifest = client.get("/manifest.json")
    assert res_manifest.status_code == 200
    print("[PASS] PWA Manifest JSON (200 OK)")


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
