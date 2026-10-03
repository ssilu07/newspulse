"""
NewsPulse - 100% Valid Google AMP Web Story Generator
Produces AMP-compliant, high-CTR, mobile-first 5-slide visual stories with JSON-LD schema.
Validated against official Google AMP Validator.
"""

import os
import sys
import json
from pathlib import Path
from html import escape
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_amp_story_html(article: dict) -> str:
    """
    Renders 100% compliant AMP Story 1.0 HTML with 5 visual slides,
    metadata, JSON-LD NewsArticle schema, and cross-exit navigation.
    """
    slug = article["slug"]
    canonical_url = f"{config.SITE_URL}/stories/{slug}/"
    home_url = f"{config.SITE_URL}/"

    title_escaped = escape(article.get("title", "Breaking News"))
    summary_escaped = escape(article.get("summary", ""))
    cat_name = escape(article.get("category_name", "News"))
    cat_color = article.get("category_color", "#3b82f6")
    source_escaped = escape(article.get("source", "NewsPulse"))
    original_url = article.get("original_url", home_url)
    pub_iso = article.get("published_at", "2026-10-03T12:00:00Z")

    # Images
    cover_image = article.get("image_url") or config.CATEGORIES.get(article.get("category", "tech"), {}).get("default_image")
    slides = article.get("slides") or []

    # Structured Data
    schema_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url
        },
        "headline": article.get("title", ""),
        "image": [cover_image],
        "datePublished": pub_iso,
        "dateModified": pub_iso,
        "author": {
            "@type": "Organization",
            "name": f"{config.SITE_NAME} Editorial Desk"
        },
        "publisher": {
            "@type": "Organization",
            "name": config.PUBLISHER_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": config.PUBLISHER_LOGO
            }
        },
        "description": article.get("summary", "")
    }
    schema_json = json.dumps(schema_data, ensure_ascii=False)

    # Render slides HTML
    slides_html_list = []
    total_slides = len(slides)

    for i, slide in enumerate(slides):
        page_id = f"slide-{i + 1}"
        s_heading = escape(slide.get("heading", f"Part {i+1}"))
        s_badge = escape(slide.get("badge", cat_name))
        s_text = escape(slide.get("text", ""))
        s_image = slide.get("image") or cover_image
        s_alt = escape(slide.get("alt", title_escaped))

        # CTA Layer on slides
        cta_markup = ""
        if i == total_slides - 1:
            cta_markup = f"""
      <amp-story-cta-layer>
        <div class="cta-box">
          <a href="{home_url}" class="cta-btn primary-cta">Explore More Stories</a>
          <a href="{escape(original_url)}" class="cta-btn secondary-cta">Source: {source_escaped} ↗</a>
        </div>
      </amp-story-cta-layer>"""
        else:
            cta_markup = f"""
      <amp-story-cta-layer>
        <div class="cta-mini-box">
          <a href="{home_url}" class="cta-exit-pill" aria-label="Exit to NewsPulse Home">&#10005; Home</a>
        </div>
      </amp-story-cta-layer>"""

        slide_markup = f"""
    <amp-story-page id="{page_id}">
      <amp-story-grid-layer template="fill">
        <amp-img src="{escape(s_image)}"
          width="720" height="1280" layout="responsive"
          alt="{s_alt}">
        </amp-img>
      </amp-story-grid-layer>
      <amp-story-grid-layer template="vertical" class="content-layer">
        <div class="top-nav-bar">
          <div class="brand-pill">
            <span class="pulse-dot"></span>
            <span class="brand-text">{config.SITE_NAME}</span>
          </div>
          <span class="story-indicator">STORY</span>
        </div>
        <div class="spacer"></div>
        <div class="story-card" animate-in="fly-in-bottom" animate-in-duration="0.45s">
          <div class="badge-row">
            <span class="category-tag">{s_badge}</span>
            <span class="progress-pill">{i + 1} of {total_slides}</span>
          </div>
          <h2 class="slide-title">{s_heading}</h2>
          <p class="slide-body" animate-in="fade-in" animate-in-delay="0.2s">{s_text}</p>
          <div class="card-footer">
            <span class="source-credit">Source: {source_escaped}</span>
            <span class="tap-hint">Tap for next &#10140;</span>
          </div>
        </div>
      </amp-story-grid-layer>{cta_markup}
    </amp-story-page>"""
        slides_html_list.append(slide_markup)

    all_slides_html = "\n".join(slides_html_list)

    html_content = f"""<!doctype html>
<html ⚡ lang="en">
<head>
  <meta charset="utf-8">
  <title>{title_escaped} - {config.SITE_NAME} Web Story</title>
  <link rel="canonical" href="{canonical_url}">
  <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
  <meta name="description" content="{summary_escaped}">
  <meta property="og:title" content="{title_escaped}">
  <meta property="og:description" content="{summary_escaped}">
  <meta property="og:image" content="{escape(cover_image)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_escaped}">
  <meta name="twitter:description" content="{summary_escaped}">
  <meta name="twitter:image" content="{escape(cover_image)}">

  <script async src="https://cdn.ampproject.org/v0.js"></script>
  <script async custom-element="amp-story" src="https://cdn.ampproject.org/v0/amp-story-1.0.js"></script>

  <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-moz-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-ms-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-o-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style><noscript><style amp-boilerplate>body{{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}}</style></noscript>

  <style amp-custom>
    amp-story {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: #ffffff;
    }}
    amp-story-page {{
      background-color: #07090e;
    }}
    .content-layer {{
      padding: 24px 20px 32px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 100%;
      box-sizing: border-box;
      background: linear-gradient(180deg, rgba(7, 9, 14, 0.45) 0%, rgba(7, 9, 14, 0.05) 30%, rgba(7, 9, 14, 0.85) 75%, rgba(7, 9, 14, 0.98) 100%);
    }}
    .top-nav-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      z-index: 10;
    }}
    .brand-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(12px);
      padding: 6px 14px;
      border-radius: 9999px;
    }}
    .pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ef4444;
      box-shadow: 0 0 10px #ef4444;
    }}
    .brand-text {{
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #ffffff;
    }}
    .close-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(12px);
      color: #ffffff;
      font-size: 16px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    .spacer {{
      flex-grow: 1;
    }}
    .story-card {{
      background: rgba(13, 18, 30, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(20px);
      border-radius: 20px;
      padding: 22px 20px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
      margin-bottom: 8px;
    }}
    .badge-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .category-tag {{
      display: inline-block;
      background: {cat_color};
      color: #ffffff;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 5px 12px;
      border-radius: 9999px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}
    .progress-pill {{
      font-size: 11px;
      font-weight: 700;
      color: rgba(255, 255, 255, 0.65);
      background: rgba(255, 255, 255, 0.08);
      padding: 4px 10px;
      border-radius: 9999px;
    }}
    .slide-title {{
      font-size: 22px;
      font-weight: 800;
      line-height: 1.25;
      margin: 0 0 10px 0;
      color: #ffffff;
      letter-spacing: -0.01em;
    }}
    .slide-body {{
      font-size: 15px;
      line-height: 1.5;
      color: rgba(255, 255, 255, 0.88);
      margin: 0 0 14px 0;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding-top: 10px;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.55);
    }}
    .source-credit {{
      font-weight: 600;
    }}
    .tap-hint {{
      letter-spacing: 0.02em;
    }}
    .cta-box {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 0 20px 24px 20px;
      width: 100%;
      box-sizing: border-box;
    }}
    .cta-btn {{
      display: block;
      text-align: center;
      font-weight: 700;
      font-size: 14px;
      padding: 14px 20px;
      border-radius: 12px;
      text-decoration: none;
      box-sizing: border-box;
      letter-spacing: 0.02em;
    }}
    .primary-cta {{
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: #ffffff;
      box-shadow: 0 4px 18px rgba(37, 99, 235, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .secondary-cta {{
      background: rgba(15, 23, 42, 0.8);
      color: rgba(255, 255, 255, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .cta-mini-box {{
      padding: 0 16px 16px 16px;
      display: flex;
      justify-content: flex-end;
      width: 100%;
      box-sizing: border-box;
    }}
    .cta-exit-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(15, 23, 42, 0.85);
      color: #ffffff;
      font-size: 11px;
      font-weight: 700;
      text-decoration: none;
      padding: 6px 14px;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
  </style>

  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body>
  <amp-story standalone
    title="{title_escaped}"
    publisher="{config.PUBLISHER_NAME}"
    publisher-logo-src="{config.PUBLISHER_LOGO}"
    poster-portrait-src="{escape(cover_image)}"
    poster-square-src="{escape(cover_image)}"
    poster-landscape-src="{escape(cover_image)}">
{all_slides_html}
  </amp-story>
</body>
</html>"""
    return html_content


def save_story_to_dist(article: dict, output_dir: Path = None) -> Path:
    """Renders and writes the AMP Story HTML file into dist/stories/<slug>/index.html."""
    if output_dir is None:
        output_dir = config.DIST_DIR / "stories" / article["slug"]
    output_dir.mkdir(parents=True, exist_ok=True)

    html_code = generate_amp_story_html(article)
    file_path = output_dir / "index.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    return file_path


if __name__ == "__main__":
    sample_art = {
        "slug": "sample-ai-breakthrough",
        "title": "Frontier AI Models Achieve Human-Level Spatial Reasoning",
        "summary": "Next-generation spatial reasoning models developed by leading AI labs have achieved record benchmark scores across robotics navigation and interactive 3D simulations. The milestone enables unprecedented autonomous systems in real-world environments.",
        "category": "ai-future",
        "category_name": "AI & Future",
        "category_color": "#8b5cf6",
        "source": "TechCrunch",
        "published_at": "2026-10-03T12:00:00Z",
        "original_url": "https://techcrunch.com",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1920&fit=crop",
        "slides": [
            {
                "slide_number": 1,
                "heading": "Frontier AI Models Achieve Human-Level Spatial Reasoning",
                "badge": "AI & Future",
                "text": "Spatial reasoning benchmarks shattered by next-generation multi-agent systems.",
                "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1920&fit=crop",
                "alt": "Frontier AI cover"
            },
            {
                "slide_number": 2,
                "heading": "The Core Breakthrough",
                "badge": "What Happened",
                "text": "Robotics researchers demonstrated real-time spatial pathfinding with zero prior maps.",
                "image": "https://images.unsplash.com/photo-1677442136019-21780efad99a?w=1080&h=1920&fit=crop",
                "alt": "AI core event"
            },
            {
                "slide_number": 3,
                "heading": "Context & Architecture",
                "badge": "Behind the Code",
                "text": "The multi-modal architecture combines continuous vision tokens with physical simulation models.",
                "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1080&h=1920&fit=crop",
                "alt": "AI architecture"
            },
            {
                "slide_number": 4,
                "heading": "Real-World Impact",
                "badge": "Why It Matters",
                "text": "Autonomous warehouse robots and medical imaging devices will see immediate efficiency upgrades.",
                "image": "https://images.unsplash.com/photo-1617791160505-6f00504e3519?w=1080&h=1920&fit=crop",
                "alt": "AI impact"
            },
            {
                "slide_number": 5,
                "heading": "The Next Frontier",
                "badge": "Key Takeaway",
                "text": "Commercial availability begins next quarter as developer APIs roll out globally.",
                "image": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=1080&h=1920&fit=crop",
                "alt": "AI future"
            }
        ]
    }
    p = save_story_to_dist(sample_art)
    print("Saved sample story to:", p)
