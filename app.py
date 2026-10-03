"""
NewsPulse - FastAPI Local Dev Server & Dynamic API
Serves static distribution, provides JSON APIs, and enables live on-demand refresh.
Run with: python app.py (or uvicorn app:app --reload)
"""

import sys
import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = FastAPI(
    title=f"{config.SITE_NAME} API",
    description=config.SITE_DESCRIPTION,
    version="1.0.0"
)

# Ensure dist exists
config.DIST_DIR.mkdir(parents=True, exist_ok=True)
if (config.DIST_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(config.DIST_DIR / "static")), name="static")
elif config.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


def read_file_or_404(path: Path, media_type: str = "text/html") -> Response:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path.name}")
    return Response(content=path.read_text(encoding="utf-8"), media_type=media_type)


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_home():
    """Serves the main NewsPulse homepage."""
    index_file = config.DIST_DIR / "index.html"
    if not index_file.exists():
        # Build if not yet present
        from fetch_and_generate import run_pipeline
        run_pipeline(max_per_category=2, skip_validation=True)
    return read_file_or_404(index_file)


@app.api_route("/stories/{slug}/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/stories/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_story(slug: str):
    """Serves an individual 100% compliant AMP Web Story."""
    story_file = config.DIST_DIR / "stories" / slug / "index.html"
    return read_file_or_404(story_file)


@app.api_route("/about/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/about", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_about():
    return read_file_or_404(config.DIST_DIR / "about" / "index.html")


@app.api_route("/privacy/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/privacy", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_privacy():
    return read_file_or_404(config.DIST_DIR / "privacy" / "index.html")


@app.api_route("/terms/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/terms", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_terms():
    return read_file_or_404(config.DIST_DIR / "terms" / "index.html")


@app.api_route("/editorial-policy/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/editorial-policy", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_editorial_policy():
    return read_file_or_404(config.DIST_DIR / "editorial-policy" / "index.html")


@app.api_route("/contact/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/contact", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_contact():
    return read_file_or_404(config.DIST_DIR / "contact" / "index.html")


@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
@app.api_route("//sitemap.xml", methods=["GET", "HEAD"])
def get_sitemap():
    return read_file_or_404(config.DIST_DIR / "sitemap.xml", media_type="application/xml; charset=utf-8")


@app.api_route("/news-sitemap.xml", methods=["GET", "HEAD"])
@app.api_route("//news-sitemap.xml", methods=["GET", "HEAD"])
def get_news_sitemap():
    news_file = config.DIST_DIR / "news-sitemap.xml"
    if not news_file.exists():
        news_file = config.DIST_DIR / "sitemap.xml"
    return read_file_or_404(news_file, media_type="application/xml; charset=utf-8")


@app.api_route("/robots.txt", methods=["GET", "HEAD"])
def get_robots():
    return read_file_or_404(config.DIST_DIR / "robots.txt", media_type="text/plain; charset=utf-8")


@app.api_route("/manifest.json", methods=["GET", "HEAD"])
def get_manifest():
    return read_file_or_404(config.DIST_DIR / "manifest.json", media_type="application/json; charset=utf-8")


@app.get("/api/articles")
def api_articles():
    """Returns all current news articles and story metadata as JSON."""
    articles_file = config.DATA_DIR / "articles.json"
    if not articles_file.exists():
        return JSONResponse(content={"articles": [], "count": 0})
    with open(articles_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content={"articles": data, "count": len(data)})


@app.post("/api/refresh")
def api_refresh(background_tasks: BackgroundTasks):
    """Triggers an asynchronous pipeline refresh."""
    from fetch_and_generate import run_pipeline
    background_tasks.add_task(run_pipeline, max_per_category=3, skip_validation=True)
    return {"status": "ok", "message": "Pipeline refresh initiated in background."}


if __name__ == "__main__":
    print(f"[*] Starting {config.SITE_NAME} server on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
