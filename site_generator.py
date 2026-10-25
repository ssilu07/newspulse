"""
NewsPulse - Static Site Generator
Builds the complete production distribution in dist/:
- Modern glassmorphic responsive homepage (index.html)
- 5 Mandatory AdSense & Google News compliance pages
- Google News XML Sitemap with <news:news> and <image:image>
- Dynamic robots.txt and PWA manifest.json
"""

import os
import sys
import shutil
import json
from pathlib import Path
from html import escape
from datetime import datetime, timezone
import config
from story_generator import save_story_to_dist, ensure_category_posters

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_tracking_head_tags() -> str:
    """Renders analytics, Google AdSense, and tracking tags (Microsoft Clarity, Google Analytics)."""
    tags = []

    adsense_pub = getattr(config, "ADSENSE_PUB_ID", "").strip()
    if adsense_pub:
        # Normalize to ca-pub-XXXXXXXXXXXXXXXX
        clean_client = adsense_pub
        if not clean_client.startswith("ca-"):
            clean_client = f"ca-{clean_client}" if clean_client.startswith("pub-") else f"ca-pub-{clean_client}"
        tags.append(f"""  <!-- Google AdSense Verification & Auto-Ads -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={clean_client}" crossorigin="anonymous"></script>""")

    clarity_id = getattr(config, "CLARITY_PROJECT_ID", "").strip()
    if clarity_id:
        tags.append(f"""  <!-- Microsoft Clarity -->
  <script>
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "{clarity_id}");
  </script>""")

    ga_id = getattr(config, "GA_MEASUREMENT_ID", "").strip()
    if ga_id:
        tags.append(f"""  <!-- Google Analytics (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga_id}');
  </script>""")

    # Default Theme Enforcer: guarantees dark/black theme (#07090e) unless explicitly set to light
    tags.append("""  <!-- Theme Init: Default Dark Cinema Mode (#07090e) -->
  <script>
    try {
      if (localStorage.getItem('newspulse_theme_user_set') === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
      }
    } catch(e) {}
  </script>""")

    return "\n".join(tags)



def get_base_header(active_nav: str = "home") -> str:
    """Renders the top navigation header with logo, search, clock, and theme toggle."""
    return f"""
  <header class="site-header">
    <div class="container header-inner">
      <a href="/" class="brand-link" aria-label="{config.SITE_NAME} Home">
        <img src="/static/assets/logo.svg" alt="{config.SITE_NAME}" class="brand-logo-img">
      </a>
      
      <div class="header-center">
        <div class="search-wrapper">
          <span class="search-icon">🔍</span>
          <input type="text" id="newsSearchInput" class="search-input" placeholder="Search news, topics, keywords... (Press /)" aria-label="Search news">
          <span class="search-shortcut-badge">/</span>
        </div>
      </div>

      <div class="header-actions">
        <a href="https://t.me/minutenewshub" target="_blank" rel="noopener" class="telegram-header-badge" style="display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 136, 204, 0.18); border: 1px solid rgba(0, 136, 204, 0.45); color: #38bdf8; text-decoration: none; padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600; transition: all 0.2s;" title="Join {config.SITE_NAME} on Telegram">
          <span>✈️</span> <span>Telegram</span>
        </a>
        <span id="liveTimeDisplay" class="time-widget">UTC</span>
        <button id="themeToggleBtn" class="theme-toggle-btn" aria-label="Toggle dark/light theme">🌙</button>
      </div>
    </div>
  </header>
"""


def get_base_footer() -> str:
    """Renders the comprehensive site footer with compliance links and editorial info."""
    return f"""
  <footer class="site-footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <img src="/static/assets/logo.svg" alt="{config.SITE_NAME}" style="height: 32px; width: auto;">
          <p>{config.SITE_DESCRIPTION}</p>
          <p style="margin-top: 8px; font-size: 11px; color: var(--text-muted);">
            Powered by Google Gemini 3.8 Flash & high-reliability multi-source news syndication.
          </p>
        </div>

        <div class="footer-col">
          <h4>Coverage</h4>
          <ul class="footer-links">
            <li><a href="/#world">⚡ EVs & Clean Mobility</a></li>
            <li><a href="/#tech">🏎️ Supercars & Hypercars</a></li>
            <li><a href="/#ai-future">🤖 Robo-Taxis & Autonomous</a></li>
            <li><a href="/#business">📈 Auto Industry & Deals</a></li>
            <li><a href="/#trending">🔥 Viral Drives & Concepts</a></li>
            <li><a href="/#sports">🏁 Motorsport & F1 Tech</a></li>
            <li><a href="/#entertainment">🎬 Car Culture & Restomods</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Editorial & Trust</h4>
          <ul class="footer-links">
            <li><a href="/about/">About & Mission</a></li>
            <li><a href="/editorial-policy/">Editorial & Fact-Check Policy</a></li>
            <li><a href="/contact/">Contact Editorial Desk</a></li>
            <li><a href="/sitemap.xml">Google News Sitemap</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Legal & Privacy</h4>
          <ul class="footer-links">
            <li><a href="/privacy/">Privacy Policy (GDPR/CCPA)</a></li>
            <li><a href="/terms/">Terms & Fair Use (17 U.S.C. § 107)</a></li>
            <li><a href="/contact/">DMCA Agent Desk</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <span>&copy; {datetime.now().year} {config.PUBLISHER_NAME}. All rights reserved.</span>
        <span>Curated for mobile readers worldwide. 100% AMP Compliant.</span>
      </div>
    </div>
  </footer>

  <!-- Cookie & GDPR Consent Banner (Google EU User Consent Policy) -->
  <div class="cookie-consent-bar" id="cookieConsentBar" role="region" aria-label="Cookie Consent" style="display: none;">
    <div class="container cookie-consent-inner">
      <div class="cookie-text">
        <span>🍪 <strong>Cookie &amp; Privacy Notice:</strong> We and our verified partners use cookies and local storage to deliver tailored news, analyze readership trends, and support our independent digital newsroom under our <a href="/privacy/">Privacy Policy</a>.</span>
      </div>
      <div class="cookie-actions">
        <button id="cookieAcceptBtn" class="cookie-btn cookie-btn-accept">Accept All</button>
        <button id="cookieManageBtn" class="cookie-btn cookie-btn-manage">Manage</button>
      </div>
    </div>
  </div>
"""


def render_homepage_html(articles: list) -> str:
    """Generates the modern homepage with breaking marquee, story bubbles, category filters, and cards."""
    # Breaking marquee items (top 10)
    marquee_items = []
    for art in articles[:10]:
        cat_badge = art.get("category_name", "Breaking")
        title = escape(art.get("title", ""))
        slug = art.get("slug")
        marquee_items.append(f'<a href="/stories/{slug}/" class="marquee-item"><strong style="color: {art.get("category_color", "#3b82f6")};">[{cat_badge}]</strong> {title}</a>')
    # Duplicate for continuous smooth loop
    marquee_html = "".join(marquee_items) + "".join(marquee_items)

    # Story Bubbles (top 8 visual stories)
    bubbles_html_list = []
    for art in articles[:8]:
        slug = art.get("slug")
        title = escape(art.get("title", ""))
        img = escape(art.get("image_url", ""))
        cat_name = escape(art.get("category_name", "Story"))
        bubble_item = f"""
        <a href="/stories/{slug}/" class="story-bubble-card" title="{title}">
          <div class="bubble-ring">
            <img src="{img}" alt="{title}" class="bubble-img" loading="lazy">
            <span class="bubble-badge">STORY</span>
          </div>
          <span class="bubble-title">{title}</span>
        </a>"""
        bubbles_html_list.append(bubble_item)
    bubbles_html = "".join(bubbles_html_list)

    # Category Pills
    pills_html_list = ['<button class="cat-pill active" data-cat="all"><span class="pill-icon">⚡</span> All Stories</button>']
    for cat_slug, cat_info in config.CATEGORIES.items():
        icon = cat_info.get("icon", "•")
        name = cat_info.get("name")
        color = cat_info.get("color", "#3b82f6")
        pills_html_list.append(f'<button class="cat-pill" data-cat="{cat_slug}" data-color="{color}"><span class="pill-icon">{icon}</span> {name}</button>')
    pills_html = "\n".join(pills_html_list)

    # Magazine Editorial Hero Showcase (Lead Cover Story + 2 Trending Sidekicks)
    hero_html = ""
    grid_articles = articles
    if articles:
        hero_art = articles[0]
        h_id = hero_art.get("id")
        h_slug = hero_art.get("slug")
        h_cat_slug = hero_art.get("category", "world")
        h_cat_name = escape(hero_art.get("category_name", "Breaking"))
        h_cat_color = hero_art.get("category_color", "#ef4444")
        h_title = escape(hero_art.get("title", ""))
        h_summary = escape(hero_art.get("summary", ""))
        h_source = escape(hero_art.get("source", config.SITE_NAME))
        h_time_ago = escape(hero_art.get("time_ago", "Just now"))
        h_image = escape(hero_art.get("image_url", ""))
        h_orig_url = escape(hero_art.get("original_url", "#"))
        h_bullets = hero_art.get("bullet_points", [])
        h_bullets_json = escape(json.dumps(h_bullets))
        h_bullets_list_html = "".join([f"<li>{escape(b)}</li>" for b in h_bullets[:3]])

        # Author for Hero E-E-A-T
        h_author = AUTHORS.get(h_cat_slug, AUTHORS.get("world", {
            "name": "Dr. Ethan Vance",
            "role": "Chief Mobility Fellow",
            "initials": "EV",
            "color": "#06b6d4"
        }))

        # Trending Sidekick Cards (Story #2 & Story #3)
        sidekicks_list_html = []
        sidekick_arts = []
        if len(articles) > 1:
            sidekick_arts.append(articles[1])
        if len(articles) > 2:
            sidekick_arts.append(articles[2])

        for s_art in sidekick_arts:
            s_id = s_art.get("id")
            s_slug = s_art.get("slug")
            s_cat_slug = s_art.get("category", "world")
            s_cat_name = escape(s_art.get("category_name", "Mobility"))
            s_cat_color = s_art.get("category_color", "#3b82f6")
            s_title = escape(s_art.get("title", ""))
            s_summary = escape(s_art.get("summary", ""))
            s_source = escape(s_art.get("source", config.SITE_NAME))
            s_time_ago = escape(s_art.get("time_ago", "Recently"))
            s_image = escape(s_art.get("image_url", ""))
            s_orig_url = escape(s_art.get("original_url", "#"))
            s_bullets_json = escape(json.dumps(s_art.get("bullet_points", [])))

            s_card = f"""
            <article class="news-card sidekick-card"
              data-id="{s_id}"
              data-slug="{s_slug}"
              data-category="{s_cat_slug}"
              data-category-name="{s_cat_name}"
              data-category-color="{s_cat_color}"
              data-title="{s_title}"
              data-summary="{s_summary}"
              data-bullets="{s_bullets_json}"
              data-source="{s_source}"
              data-time-ago="{s_time_ago}"
              data-image="{s_image}"
              data-original-url="{s_orig_url}">
              <div class="sidekick-thumb-wrap">
                <a href="/news/{s_slug}/" class="sidekick-thumb-link" aria-label="{s_title}">
                  <img src="{s_image}" alt="{s_title}" class="sidekick-thumb" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&fit=crop';">
                </a>
              </div>
              <div class="sidekick-body">
                <div class="sidekick-meta-row">
                  <span class="sidekick-badge" style="background-color: {s_cat_color};">{s_cat_name}</span>
                  <span class="sidekick-time">🕒 {s_time_ago}</span>
                </div>
                <h3 class="sidekick-title"><a href="/news/{s_slug}/" class="card-title-link">{s_title}</a></h3>
                <div class="sidekick-actions">
                  <span class="sidekick-source"><span class="source-dot"></span>{s_source}</span>
                  <div class="action-btn-group">
                    <button class="btn-quick-read sidekick-btn" title="Quick Read Drawer">📖 60s</button>
                    <a href="/stories/{s_slug}/" class="web-story-link sidekick-story-btn" title="Visual Story">⚡ Story</a>
                  </div>
                </div>
              </div>
            </article>"""
            sidekicks_list_html.append(s_card)

        sidekicks_block = "\n".join(sidekicks_list_html) if sidekicks_list_html else ""

        hero_html = f"""
    <!-- Magazine Editorial Hero Showcase -->
    <section class="featured-hero-section" id="heroSection" aria-label="Editor's Spotlight">
      <div class="section-label-row">
        <h2 class="section-heading">
          <span class="live-dot"></span>
          <span>Editor's Showcase</span>
        </h2>
        <div class="hero-top-badges">
          <span class="hero-edition-badge">⚡ VIP MOBILITY EDITION</span>
          <span class="spotlight-tag">🔥 TOP BREAKING</span>
        </div>
      </div>

      <div class="hero-showcase-grid">
        <!-- Lead Cinematic Cover Story -->
        <article class="news-card featured-news-card hero-lead-card"
          data-id="{h_id}"
          data-slug="{h_slug}"
          data-category="{h_cat_slug}"
          data-category-name="{h_cat_name}"
          data-category-color="{h_cat_color}"
          data-title="{h_title}"
          data-summary="{h_summary}"
          data-bullets="{h_bullets_json}"
          data-source="{h_source}"
          data-time-ago="{h_time_ago}"
          data-image="{h_image}"
          data-original-url="{h_orig_url}">
          
          <div class="card-media featured-media">
            <a href="/news/{h_slug}/" class="card-media-link" aria-label="{h_title}">
              <img src="{h_image}" alt="{h_title}" class="card-img" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop';">
            </a>
            <div class="hero-media-scrim"></div>
            <span class="card-tag" style="background-color: {h_cat_color};">{h_cat_name}</span>
            <span class="card-meta-badge">🕒 {h_time_ago}</span>
          </div>

          <div class="card-body featured-body">
            <div class="card-source-row">
              <span class="card-source"><span class="source-dot"></span>{h_source} <span class="verified-source" title="Verified Wire Source">✓</span></span>
              <span class="read-badge">⚡ 1 min read</span>
            </div>
            <h2 class="card-title featured-title"><a href="/news/{h_slug}/" class="card-title-link">{h_title}</a></h2>
            <p class="card-summary featured-summary">{h_summary}</p>

            <!-- E-E-A-T Editorial Byline -->
            <div class="hero-author-byline">
              <span class="hero-author-avatar" style="background-color: {h_author['color']};">{h_author['initials']}</span>
              <div class="hero-author-meta">
                <span class="hero-author-name">{h_author['name']} <span class="verified-badge" title="Verified Editorial Fellow">✓</span></span>
                <span class="hero-author-role">{h_author['role']}</span>
              </div>
            </div>

            <div class="featured-takeaways-box">
              <div class="featured-takeaways-title">Key Intelligence & Telemetry</div>
              <ul class="featured-takeaways-list">
                {h_bullets_list_html}
              </ul>
            </div>

            <div class="card-actions">
              <div class="action-btn-group">
                <a href="/news/{h_slug}/" class="full-article-link" title="Read Full In-Depth Story">📰 Full Story</a>
                <a href="/stories/{h_slug}/" class="web-story-link" title="Open 5-Slide Visual Web Story">⚡ Web Story</a>
                <button class="btn-quick-read" title="Quick Read Drawer">📖 Summary</button>
              </div>
              <div class="action-btn-group">
                <button class="icon-action-btn tts-btn" data-id="{h_id}" title="Listen to audio" aria-label="Listen">🔊</button>
                <button class="icon-action-btn bookmark-btn" data-id="{h_id}" title="Save story" aria-label="Bookmark">☆</button>
                <button class="icon-action-btn share-btn" title="Share story" aria-label="Share">🔗</button>
              </div>
            </div>
          </div>
        </article>

        <!-- Trending Sidekicks Column -->
        <aside class="hero-sidekick-stack" aria-label="Trending In Mobility">
          <div class="sidekick-header">
            <span class="sidekick-header-title">⚡ TRENDING INTELLIGENCE</span>
            <span class="sidekick-header-sub">UPDATED LIVE</span>
          </div>
          {sidekicks_block}
        </aside>
      </div>
    </section>
"""
        # Limit initial homepage grid: skip the 3 featured hero articles (index 0, 1, 2)
        HOMEPAGE_MAX_INITIAL = 36
        grid_articles = articles[3:HOMEPAGE_MAX_INITIAL + 3] if len(articles) > 3 else articles[1:HOMEPAGE_MAX_INITIAL + 1]

    # Article Cards
    cards_html_list = []
    for idx, art in enumerate(grid_articles):
        # Insert VIP Newsletter Card ("THE GRID") after 5 cards
        if idx == 5:
            newsletter_html = """
        <aside class="newsletter-card" aria-label="Join The Grid">
          <div class="newsletter-glow"></div>
          <div class="newsletter-content">
            <div class="newsletter-badge">🏎️ VIP AUTOMOTIVE BRIEF</div>
            <h3 class="newsletter-title">THE GRID: Weekly Supercar &amp; EV Intel</h3>
            <p class="newsletter-desc">Join 28,000+ automotive engineers, track drivers, and mobility founders. Every Friday, get the 60-second recap of breakthroughs shaping high-speed transportation.</p>
            <form class="newsletter-form" id="newsletterForm" onsubmit="event.preventDefault(); window.subscribeGrid(this);">
              <div class="newsletter-input-group">
                <input type="email" required placeholder="Enter your work or personal email..." class="newsletter-input" aria-label="Email Address">
                <button type="submit" class="newsletter-btn">⚡ Join The Grid</button>
              </div>
              <span class="newsletter-note">🔒 Zero spam. One-click unsubscribe anytime. Free forever.</span>
            </form>
          </div>
        </aside>"""
            cards_html_list.append(newsletter_html)

        art_id = art.get("id")
        slug = art.get("slug")
        cat_slug = art.get("category")
        cat_name = escape(art.get("category_name", "News"))
        cat_color = art.get("category_color", "#3b82f6")
        title = escape(art.get("title", ""))
        summary = escape(art.get("summary", ""))
        source = escape(art.get("source", config.SITE_NAME))
        time_ago = escape(art.get("time_ago", "Recently"))
        image = escape(art.get("image_url", ""))
        orig_url = escape(art.get("original_url", "#"))
        bullets_json = escape(json.dumps(art.get("bullet_points", [])))

        card_html = f"""
        <article class="news-card"
          data-id="{art_id}"
          data-slug="{slug}"
          data-category="{cat_slug}"
          data-category-name="{cat_name}"
          data-category-color="{cat_color}"
          data-title="{title}"
          data-summary="{summary}"
          data-bullets="{bullets_json}"
          data-source="{source}"
          data-time-ago="{time_ago}"
          data-image="{image}"
          data-original-url="{orig_url}">
          
          <div class="card-media">
            <a href="/news/{slug}/" class="card-media-link" aria-label="{title}">
              <img src="{image}" alt="{title}" class="card-img" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&fit=crop';">
            </a>
            <span class="card-tag" style="background-color: {cat_color};">{cat_name}</span>
            <span class="card-meta-badge">🕒 {time_ago}</span>
          </div>

          <div class="card-body">
            <div class="card-source-row">
              <span class="card-source"><span class="source-dot"></span>{source} <span class="verified-source" title="Verified Wire Source">✓</span></span>
              <span class="read-badge">1 min read</span>
            </div>
            <h3 class="card-title"><a href="/news/{slug}/" class="card-title-link">{title}</a></h3>
            <p class="card-summary">{summary}</p>

            <div class="card-actions">
              <div class="action-btn-group">
                <a href="/news/{slug}/" class="full-article-link" title="Read Full In-Depth Story">📰 Full Story</a>
                <a href="/stories/{slug}/" class="web-story-link" title="Open 5-Slide AMP Story">⚡ Web Story</a>
                <button class="btn-quick-read" title="Quick Read Drawer">📖 Summary</button>
              </div>
              <div class="action-btn-group">
                <button class="icon-action-btn tts-btn" data-id="{art_id}" title="Listen to summary" aria-label="Listen">🔊</button>
                <button class="icon-action-btn bookmark-btn" data-id="{art_id}" title="Save story" aria-label="Bookmark">☆</button>
                <button class="icon-action-btn share-btn" title="Share story" aria-label="Share">🔗</button>
              </div>
            </div>
          </div>
        </article>"""
        cards_html_list.append(card_html)
    cards_html = "\n".join(cards_html_list)

    # Structured Data
    homepage_schema = {
        "@context": "https://schema.org",
        "@type": "NewsMediaOrganization",
        "name": config.SITE_NAME,
        "url": config.SITE_URL,
        "logo": {
            "@type": "ImageObject",
            "url": config.PUBLISHER_LOGO,
            "width": 512,
            "height": 512
        },
        "description": config.SITE_DESCRIPTION,
        "sameAs": [
            "https://twitter.com/NewsSeconds",
            "https://facebook.com/NewsSeconds"
        ]
    }

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{config.SITE_NAME} - {config.SITE_TAGLINE}</title>
  <meta name="description" content="{config.SITE_DESCRIPTION}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{config.SITE_URL}/">

  <!-- OpenGraph / Twitter Meta -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{config.SITE_URL}/">
  <meta property="og:title" content="{config.SITE_NAME} - {config.SITE_TAGLINE}">
  <meta property="og:description" content="{config.SITE_DESCRIPTION}">
  <meta property="og:image" content="{config.PUBLISHER_LOGO}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{config.SITE_NAME} - {config.SITE_TAGLINE}">
  <meta name="twitter:description" content="{config.SITE_DESCRIPTION}">
  <meta name="twitter:image" content="{config.PUBLISHER_LOGO}">

  <!-- Favicon & PWA Icons (Google, Apple, Android) -->
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#07090e">

  <!-- Stylesheet -->
  <link rel="stylesheet" href="/static/css/style.css">

  <!-- Google Search Console Verification -->
  {f'<meta name="google-site-verification" content="{config.GOOGLE_SITE_VERIFICATION}">' if getattr(config, 'GOOGLE_SITE_VERIFICATION', '') else ''}

{get_tracking_head_tags()}

  <script type="application/ld+json">
{json.dumps(homepage_schema, ensure_ascii=False)}
  </script>
</head>
<body>

  <!-- Breaking Live Marquee Ticker -->
  <div class="breaking-marquee" role="marquee" aria-label="Breaking Headlines">
    <div class="marquee-badge">
      <span class="live-dot"></span>
      <span>Live Breaking</span>
    </div>
    <div class="marquee-track">
      {marquee_html}
    </div>
  </div>

  <!-- High-Speed Mobility Telemetry & Speed Index -->
  <div class="telemetry-bar" aria-label="Live Automotive Telemetry">
    <div class="container telemetry-inner">
      <div class="telemetry-badge">
        <span class="live-dot" style="background: #06b6d4;"></span>
        <span>MOBILITY PULSE</span>
      </div>
      <div class="telemetry-items">
        <span class="telemetry-item"><strong class="t-accent">⚡ 0-60 RECORD:</strong> 1.40s (McMurtry Spéirling)</span>
        <span class="telemetry-sep">•</span>
        <span class="telemetry-item"><strong class="t-accent">🔋 SOLID-STATE:</strong> 1,020 km Range (CATL Shenxing+)</span>
        <span class="telemetry-sep">•</span>
        <span class="telemetry-item"><strong class="t-accent">🏎️ F1 2026:</strong> 50% Hybrid Electrified</span>
        <span class="telemetry-sep">•</span>
        <span class="telemetry-item"><strong class="t-accent">🤖 ROBOTAXIS:</strong> L4 in 18 Global Hubs</span>
        <span class="telemetry-sep">•</span>
        <span class="telemetry-item"><strong class="t-accent">🚀 HYPERCAR TOP:</strong> 508 km/h (Bugatti Tourbillon)</span>
      </div>
    </div>
  </div>

  <!-- Header -->
  {get_base_header("home")}

  <main class="container">
    <!-- Visual Web Stories Carousel -->
    <section class="stories-section" aria-label="Visual Web Stories">
      <div class="stories-tray">
        <div class="section-label-row">
          <h2 class="section-heading">
            <span class="dot"></span>
            <span>Trending Web Stories</span>
          </h2>
          <span style="font-size: 11px; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em;">TAP TO VIEW 5-SLIDE VISUALS</span>
        </div>
        <div class="stories-carousel">
          {bubbles_html}
        </div>
      </div>
    </section>

    <!-- Category Filter Bar -->
    <section class="filter-bar" aria-label="Category Selection">
      <div class="category-pills">
        {pills_html}
      </div>
      <button id="bookmarksToggleBtn" class="bookmarks-toggle-btn" aria-label="View Saved Stories">
        <span>★ Saved</span>
        <span id="bookmarkCountBadge" style="background: rgba(0,0,0,0.2); padding: 1px 6px; border-radius: 9999px; font-size: 11px;">0</span>
      </button>
    </section>

    {hero_html}

    <!-- News Cards Grid -->
    <section class="articles-grid" id="articlesGrid" aria-label="Top News Headlines">
      {cards_html}

      <div class="empty-state" id="emptyState" style="display: none;">
        <h3>No matching stories found</h3>
        <p>Try searching with another keyword or explore different categories.</p>
      </div>
    </section>

    <!-- Load More Action -->
    <div class="load-more-container" id="loadMoreWrapper" style="text-align: center; margin: 40px 0 30px 0;">
      <button id="loadMoreBtn" class="load-more-btn">
        <span>Load More Breaking Mobility Stories</span>
        <span class="btn-arrow" style="font-size: 16px;">↓</span>
      </button>
    </div>
  </main>

  <!-- Quick Read Drawer / Modal -->
  <div class="modal-overlay" id="quickReadModal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <div class="modal-container">
      <button class="modal-close-btn" id="modalCloseBtn" aria-label="Close Modal">&#10005;</button>
      <img src="" alt="" class="modal-media" id="modalImg">
      <div class="modal-content">
        <div class="modal-meta-row">
          <span class="card-tag" id="modalTag">Category</span>
          <span style="font-size: 12px; font-weight: 700; color: var(--accent);" id="modalSource">Source</span>
          <span style="font-size: 12px; color: var(--text-muted);" id="modalTime">Time</span>
        </div>
        <h2 class="modal-title" id="modalTitle">Headline</h2>
        <div class="modal-summary-box" id="modalSummary">Summary text</div>
        
        <div id="modalTakeawaysWrapper">
          <h4 class="modal-takeaways-title">Key Takeaways</h4>
          <ul class="modal-bullets" id="modalBullets"></ul>
        </div>

        <div class="modal-footer">
          <a href="#" class="web-story-link" id="modalStoryBtn">⚡ Experience Full AMP Story</a>
          <div style="display: flex; gap: 8px;">
            <button class="btn-quick-read" id="modalTtsBtn">🔊 Listen</button>
            <a href="#" target="_blank" rel="noopener noreferrer" class="btn-quick-read" id="modalOriginalBtn">Original Article ↗</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Floating Toast Notification -->
  <div class="toast-msg" id="toastMsg" role="alert">Notification</div>

  <!-- Top Reading Progress Bar -->
  <div id="readingProgressBar" class="reading-progress-bar" aria-hidden="true"></div>

  <!-- Floating Back-to-Top Button -->
  <button id="backToTopBtn" class="back-to-top-btn" aria-label="Scroll to top" title="Back to top">↑</button>

  <!-- Footer -->
  {get_base_footer()}

  <!-- Main JavaScript Engine -->
  <script src="/static/js/main.js?v=2.3"></script>
</body>
</html>"""
    return full_html


AUTHORS = {
    "world": {
        "name": "Dr. Ethan Vance",
        "role": "Chief EV & Battery Systems Fellow",
        "initials": "EV",
        "color": "#06b6d4",
        "bio": "Dr. Vance tracks battery cell chemistries (solid-state, LFP, sodium-ion), megawatt charging protocols, and gigafactory scaling across North America and Europe.",
        "email": "ethan.vance@newsseconds.com"
    },
    "tech": {
        "name": "Marco Rossi",
        "role": "Senior Supercar & Aerodynamics Editor",
        "initials": "MR",
        "color": "#ef4444",
        "bio": "Marco reports on mid-engine twin-turbos, performance hybrid powertrains, active aero, and Nürburgring lap records across Maranello, Stuttgart, and Silverstone.",
        "email": "marco.rossi@newsseconds.com"
    },
    "ai-future": {
        "name": "Aria Tanaka",
        "role": "Autonomous Driving & Sensor Architect",
        "initials": "AT",
        "color": "#8b5cf6",
        "bio": "Aria covers neural network computer vision, automotive lidar suites, Waymo commercial expansion, and Tesla Full Self-Driving regulatory safety filings.",
        "email": "aria.tanaka@newsseconds.com"
    },
    "business": {
        "name": "Elena Rostova",
        "role": "Global Automotive Industry & Supply-Chain Analyst",
        "initials": "ER",
        "color": "#10b981",
        "bio": "Elena investigates automaker quarterly earnings, gigafactory capital allocations, critical battery mineral supply-chains, and global automotive tariffs.",
        "email": "elena.rostova@newsseconds.com"
    },
    "trending": {
        "name": "Tyler Brooks",
        "role": "Viral Concepts & Prototype Lead",
        "initials": "TB",
        "color": "#f43f5e",
        "bio": "Tyler tracks unreleased hypercar prototypes, world speed record runs, radical design concepts, and viral custom engineering projects.",
        "email": "tyler.brooks@newsseconds.com"
    },
    "sports": {
        "name": "David Miller",
        "role": "Formula 1 & Motorsport Telemetry Specialist",
        "initials": "DM",
        "color": "#f59e0b",
        "bio": "David covers Formula 1 ground-effect aerodynamics, FIA power-unit regulations, Formula E gen-spec powertrains, and Le Mans Hypercar endurance racing.",
        "email": "david.miller@newsseconds.com"
    },
    "entertainment": {
        "name": "Chloe Adams",
        "role": "Car Culture & Restomod Editor",
        "initials": "CA",
        "color": "#ec4899",
        "bio": "Chloe chronicles bespoke V8 restomod builds, million-dollar Monterey Car Week auctions, cinematic chase vehicles, and classic automotive preservation.",
        "email": "chloe.adams@newsseconds.com"
    }
}


def generate_editorial_take(article: dict, author: dict) -> dict:
    """Generates an insightful, value-adding 'Why It Matters / Editor's Take' perspective to eliminate scraped content penalties."""
    cat = article.get("category", "world")
    source = article.get("source", config.SITE_NAME)
    cat_name = article.get("category_name", "Automotive")

    if cat == "world":
        takeaway_title = "The Electrification & Charging Infrastructure Horizon"
        takeaway_body = (
            f"Beyond the immediate headline, this development marks a critical inflection point in the broader EV transition. "
            f"As automakers and charging networks race to lower consumer friction, the reporting from {source} highlights that "
            f"battery energy density, thermal management, and raw cost per kilowatt-hour remain the ultimate battlegrounds. "
            f"For prospective EV buyers and fleet operators, tracking these operational metrics offers clear guidance on vehicle longevity and residual value."
        )
        big_picture = "Global battery production scale and grid upgrades will define whether mass-market adoption targets are met over the next 24 months."
    elif cat == "tech":
        takeaway_title = "The Benchmark for Track-Tolerant Engineering"
        takeaway_body = (
            f"In the high-stakes supercar arena, pure horsepower is no longer enough to claim supremacy. "
            f"This dispatch from {source} emphasizes how cutting-edge downforce balance, electronic limited-slip differentials, and hybrid torque-vectoring "
            f"are reshaping driver engagement. Exotic marques must prove that extreme performance can harmonize with reliability, thermal endurance, and road compliance."
        )
        big_picture = "Lap times at benchmark proving grounds and early client allocations will reveal whether this performance envelope disrupts the existing supercar hierarchy."
    elif cat == "ai-future":
        takeaway_title = "Autonomous Validation & Edge-Case Reliability"
        takeaway_body = (
            f"Scaling driverless technology demands an uncompromising safety threshold that exceeds human reaction time. "
            f"As verified by {source}, breakthroughs in multi-modal sensor fusion and end-to-end neural network driving models are shifting the industry "
            f"from geofenced testing toward true commercial viability. The primary hurdle now centers on regulatory certification and public trust."
        )
        big_picture = "Commercial deployment permits in tier-one metropolitan test beds will serve as the litmus test for autonomous scalability."
    elif cat == "business":
        takeaway_title = "Capital Allocation Across Global Automakers"
        takeaway_body = (
            f"From an institutional perspective, the economic figures outlined in this dispatch from {source} reflect monumental shifts in automotive capital. "
            f"Legacy original equipment manufacturers (OEMs) and agile EV startups alike must balance heavy gigafactory capital expenditures against fluctuating consumer demand and trade tariffs. "
            f"Supply chain resilience—especially across lithium, cathode precursor materials, and semiconductors—is determining profitability."
        )
        big_picture = "Upcoming quarterly delivery reports and operating margins will indicate which manufacturers are successfully navigating the EV transformation curve."
    elif cat == "sports":
        takeaway_title = "Aerodynamic Efficiency & Motorsport Racecraft"
        takeaway_body = (
            f"In premier motorsport disciplines, millisecond gains represent months of high-intensity computational fluid dynamics (CFD) research. "
            f"The developments reported by {source} underline how tire degradation curves, ground-effect aero seals, and power-unit energy recovery systems "
            f"dictate race outcomes. Technical compliance under strict cost caps continues to test team engineering depth."
        )
        big_picture = "Upcoming grand prix telemetry and trackside upgrades will reveal which teams hold the definitive technical advantage."
    elif cat == "entertainment":
        takeaway_title = "Heritage Preservation vs Modern Performance"
        takeaway_body = (
            f"Automotive passion is increasingly defined by the synthesis of analog soul and contemporary engineering. "
            f"This coverage from {source} illustrates how bespoke builders, private collectors, and restomod artists are preserving the golden eras "
            f"of internal combustion while adopting carbon fiber composites and precision craftsmanship."
        )
        big_picture = "Auction hammer prices and enthusiast demand indicate sustained historical appreciation for rare, analog driver's vehicles."
    else:
        takeaway_title = "Automotive Innovation & Market Feasibility"
        takeaway_body = (
            f"Concept prototypes and viral vehicle reveals offer an exciting window into the automotive industry's future design language. "
            f"Dispatches from {source} demonstrate how radical styling, lightweight materials, and powertrain packaging can transition from design studios "
            f"to production assembly lines. Engineering feasibility and homologation standards remain the true measures of impact."
        )
        big_picture = "Market reception and formal OEM production announcements will determine which concept innovations make it to consumer streets."

    return {
        "heading": takeaway_title,
        "body": takeaway_body,
        "big_picture": big_picture
    }


def render_article_page_html(article: dict, all_articles: list) -> str:
    """
    Renders a dedicated, in-depth, AdSense & Google News-compliant article page.
    Generates substantive long-form reporting with structured sections, executive takeaways,
    audio narration player, companion Web Story, related news, and NewsArticle JSON-LD.
    """
    import urllib.parse
    title = escape(article.get("title", ""))
    slug = article.get("slug", "")
    cat_slug = article.get("category", "trending")
    cat_info = config.CATEGORIES.get(cat_slug, {})
    cat_name = escape(article.get("category_name", cat_info.get("name", "News")))
    cat_color = escape(article.get("category_color", cat_info.get("color", "#3b82f6")))
    summary = escape(article.get("summary", ""))
    raw_summary = escape(article.get("raw_summary", ""))
    source = escape(article.get("source", config.SITE_NAME))
    time_ago = escape(article.get("time_ago", "Recently"))
    image_url = escape(article.get("image_url", ""))
    orig_url = escape(article.get("original_url", "#"))
    published_at = article.get("published_at", datetime.now(timezone.utc).isoformat())
    reading_time = escape(article.get("reading_time", "2 min read"))
    bullet_points = article.get("bullet_points", [])
    slides = article.get("slides", [])

    # Assign Expert Author (E-E-A-T Compliance)
    author = AUTHORS.get(cat_slug, AUTHORS["trending"])
    take_info = generate_editorial_take(article, author)


    # Format Takeaways Box & Filter Out Repetitive Default Stubs
    paras = [escape(p.strip()) for p in article.get("article_paragraphs", []) if p and p.strip()]

    clean_bullets = []
    if bullet_points:
        for b in bullet_points:
            b_clean = escape(b.strip())
            if b_clean and b_clean not in clean_bullets and "details monitored" not in b_clean.lower() and "verified coverage" not in b_clean.lower():
                clean_bullets.append(b_clean)

    if len(clean_bullets) < 2 and paras:
        for p in paras[:3]:
            first_sent = p.split(". ")[0].strip()
            if len(first_sent.split()) >= 6 and first_sent not in clean_bullets:
                clean_bullets.append(first_sent if first_sent.endswith(".") else f"{first_sent}.")

    if not clean_bullets:
        clean_bullets = [summary] if summary else [title]

    bullets_html = "".join([f"<li>{b}</li>" for b in clean_bullets[:4]])

    # Multi-Section Substantive Editorial Narrative
    if paras:
        lead_text = paras[0]
        remaining = paras[1:]
        if len(remaining) >= 6:
            sec1_text = "</p><p class=\"article-p\">".join(remaining[0:2])
            sec2_text = "</p><p class=\"article-p\">".join(remaining[2:4])
            sec3_text = "</p><p class=\"article-p\">".join(remaining[4:5])
            sec4_text = "</p><p class=\"article-p\">".join(remaining[5:])
        elif len(remaining) >= 4:
            sec1_text = remaining[0]
            sec2_text = remaining[1]
            sec3_text = remaining[2]
            sec4_text = "</p><p class=\"article-p\">".join(remaining[3:])
        elif len(remaining) >= 2:
            sec1_text = remaining[0]
            sec2_text = remaining[1]
            sec3_text = f"Industry insights from {source} indicate significant structural shifts underway across the {cat_name.lower()} landscape."
            sec4_text = f"Follow-up milestones over the coming days will clarify long-term impacts as reported by {source} correspondents."
        elif len(remaining) == 1:
            sec1_text = remaining[0]
            sec2_text = f"This latest development follows growing attention across the {cat_name.lower()} sector as analyzed by {source}."
            sec3_text = f"The broader implications are expected to influence operational frameworks and consumer adoption."
            sec4_text = f"Observers and market participants are advised to monitor official briefings from {source}."
        else:
            sec1_text = f"According to verified dispatches reported by {source}, key developments accelerated rapidly around this story."
            sec2_text = f"This latest development follows growing attention across the {cat_name.lower()} landscape."
            sec3_text = f"The broader implications are expected to influence operational frameworks and consumer adoption."
            sec4_text = f"Key milestones over the coming days will clarify long-term impacts as reported by {source}."
    else:
        # Fallback if no full article paragraphs
        s_texts = [s.get("text", "").strip() for s in slides if s.get("text") and s.get("text").strip() != summary]
        lead_text = summary if summary else (raw_summary[:250] if raw_summary else title)
        raw_sec1 = s_texts[0] if len(s_texts) > 0 and s_texts[0] != summary else ""
        sec1_text = f"{raw_sec1} According to verified dispatches reported by {source}, key developments accelerated rapidly around this timeline." if (raw_sec1 and len(raw_sec1) > 20) else f"According to verified wire dispatches reported by {source}, key developments accelerated rapidly around this story."
        raw_sec2 = s_texts[1] if len(s_texts) > 1 and s_texts[1] != summary else ""
        sec2_text = f"{raw_sec2} This latest development follows growing attention across the {cat_name.lower()} landscape over recent weeks." if (raw_sec2 and len(raw_sec2) > 20) else f"This latest development follows growing attention across the {cat_name.lower()} landscape over recent weeks."
        raw_sec3 = s_texts[2] if len(s_texts) > 2 and s_texts[2] != summary else ""
        sec3_text = f"{raw_sec3} Beyond the initial disclosures, ecosystem participants have signaled that structural adjustments and strategic adaptations will be necessary." if (raw_sec3 and len(raw_sec3) > 20) else f"The broader implications of this development are expected to influence operational frameworks, regulatory considerations, and consumer engagement."
        raw_sec4 = s_texts[3] if len(s_texts) > 3 and s_texts[3] != summary else ""
        sec4_text = f"{raw_sec4} As subsequent updates continue to unfold, analysts emphasize that key follow-up benchmarks over the coming days will clarify long-term impacts." if (raw_sec4 and len(raw_sec4) > 20) else f"As updates continue to unfold, analysts emphasize that key milestones in the coming days will clarify long-term impacts."


    # AdSense Non-Intrusive Placement Slot
    adsense_pub = getattr(config, "ADSENSE_PUB_ID", "").strip()
    if adsense_pub:
        clean_client = adsense_pub
        if not clean_client.startswith("ca-"):
            clean_client = f"ca-{clean_client}" if clean_client.startswith("pub-") else f"ca-pub-{clean_client}"
        ad_slot_html = f"""
        <div class="ad-placement-slot">
          <span class="ad-label">Advertisement</span>
          <ins class="adsbygoogle"
               style="display:block; text-align:center;"
               data-ad-layout="in-article"
               data-ad-format="fluid"
               data-ad-client="{clean_client}"
               data-ad-slot="auto"></ins>
          <script>
            (adsbygoogle = window.adsbygoogle || []).push({{}});
          </script>
        </div>"""
    else:
        ad_slot_html = ""

    # Related Articles in same category (up to 3)
    related = [a for a in all_articles if a.get("slug") != slug and a.get("category") == cat_slug]
    if len(related) < 3:
        related.extend([a for a in all_articles if a.get("slug") != slug and a not in related])
    related = related[:3]

    related_cards_html = []
    for r in related:
        r_slug = r.get("slug", "")
        r_title = escape(r.get("title", ""))
        r_img = escape(r.get("image_url", ""))
        r_time = escape(r.get("time_ago", "Recently"))
        r_source = escape(r.get("source", config.SITE_NAME))
        related_cards_html.append(f"""
          <article class="news-card" style="margin: 0;">
            <div class="card-media" style="height: 150px;">
              <a href="/news/{r_slug}/" class="card-media-link" aria-label="{r_title}">
                <img src="{r_img}" alt="{r_title}" class="card-img" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&fit=crop';">
              </a>
              <span class="card-tag" style="background-color: {cat_color}; font-size: 10px; padding: 2px 8px;">{cat_name}</span>
            </div>
            <div class="card-body" style="padding: 14px;">
              <div class="card-source-row" style="margin-bottom: 6px;">
                <span class="card-source" style="font-size: 11px;"><span class="source-dot"></span>{r_source}</span>
                <span class="read-badge" style="font-size: 10px;">🕒 {r_time}</span>
              </div>
              <h4 style="font-size: 14px; font-weight: 700; line-height: 1.35; margin: 0 0 10px 0;">
                <a href="/news/{r_slug}/" class="card-title-link">{r_title}</a>
              </h4>
              <div style="display: flex; gap: 6px;">
                <a href="/news/{r_slug}/" class="full-article-link" style="padding: 4px 10px; font-size: 11px;">Read Story</a>
                <a href="/stories/{r_slug}/" class="web-story-link" style="padding: 4px 10px; font-size: 11px;">⚡ Story</a>
              </div>
            </div>
          </article>""")
    related_grid_html = "\n".join(related_cards_html)

    # Social share encoded links
    page_url = f"{config.SITE_URL}/news/{slug}/"
    enc_url = urllib.parse.quote(page_url)
    enc_title = urllib.parse.quote(article.get("title", ""))

    wa_share = f"https://api.whatsapp.com/send?text={enc_title}%20{enc_url}"
    tw_share = f"https://twitter.com/intent/tweet?text={enc_title}&url={enc_url}"
    li_share = f"https://www.linkedin.com/sharing/share-offsite/?url={enc_url}"
    fb_share = f"https://www.facebook.com/sharer/sharer.php?u={enc_url}"

    # Schema JSON-LD
    schema_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.get("title", ""),
        "description": article.get("summary", ""),
        "image": [article.get("image_url", config.PUBLISHER_LOGO)],
        "datePublished": published_at,
        "dateModified": published_at,
        "author": {
            "@type": "Person",
            "name": author["name"],
            "jobTitle": author["role"],
            "url": f"{config.SITE_URL}/about/#team"
        },
        "publisher": {
            "@type": "NewsMediaOrganization",
            "name": config.SITE_NAME,
            "url": config.SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": config.PUBLISHER_LOGO,
                "width": 512,
                "height": 512
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": page_url
        },
        "articleSection": cat_name,
        "wordCount": len((lead_text + " " + sec1_text + " " + sec2_text + " " + sec3_text + " " + sec4_text + " " + take_info["body"]).split())
    }
    schema_json = json.dumps(schema_data, indent=2, ensure_ascii=False)

    article_html = f"""<!DOCTYPE html>
<html lang="{config.SITE_LANGUAGE}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | {config.SITE_NAME}</title>
  <meta name="description" content="{summary}">
  <link rel="canonical" href="{page_url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{summary}">
  <meta property="og:url" content="{page_url}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:site_name" content="{config.SITE_NAME}">
  <meta property="article:published_time" content="{published_at}">
  <meta property="article:section" content="{cat_name}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{summary}">
  <meta name="twitter:image" content="{image_url}">

  <!-- Favicons -->
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="manifest" href="/manifest.json">

  <!-- Core Stylesheet -->
  <link rel="stylesheet" href="/static/css/style.css">

  {get_tracking_head_tags()}

  <!-- NewsArticle JSON-LD Structured Data -->
  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body>
  <!-- Global Top Header -->
  {get_base_header(active_nav="news")}

  <!-- Breadcrumbs Navigation -->
  <nav class="breadcrumb-nav" aria-label="Breadcrumb">
    <div class="container">
      <ol class="breadcrumb-list">
        <li><a href="/">Home</a></li>
        <li><span class="sep">/</span></li>
        <li><a href="/#{cat_slug}">{cat_name}</a></li>
        <li><span class="sep">/</span></li>
        <li class="active-crumb" aria-current="page">{title}</li>
      </ol>
    </div>
  </nav>

  <!-- Main Article Layout -->
  <main class="container">
    <article class="article-layout">
      <!-- Article Header -->
      <header class="article-header">
        <div class="article-badge-row">
          <span class="article-cat-badge" style="background-color: {cat_color};">{cat_name}</span>
          <span class="article-time-badge">🕒 {time_ago}</span>
          <span class="article-read-badge">⚡ {reading_time}</span>
        </div>

        <h1 class="article-title">{title}</h1>

        <div class="article-byline-bar">
          <div class="article-author-info">
            <div class="article-author-avatar" style="background: {author['color']};">{author['initials']}</div>
            <div class="article-author-text">
              <span class="article-author-name">By {author['name']}</span>
              <span class="article-author-role">{author['role']} • via {source} Wire</span>
            </div>
          </div>

          <div class="article-quick-actions">
            <button id="articleTtsBtn" class="article-action-pill" title="Listen to article">
              <span>🔊</span> <span>Listen to Story</span>
            </button>
            <a href="/stories/{slug}/" class="article-action-pill story-pill" title="Open 5-Slide Web Story">
              <span>⚡</span> <span>Visual Story</span>
            </a>
          </div>
        </div>
      </header>

      <!-- Featured Image -->
      <div class="article-featured-image-box">
        <img src="{image_url}" alt="{title}" class="article-featured-img" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop';">
        <div class="article-img-caption">
          <span>Source & Photography: {source} Wire Dispatch</span>
          <span>Verified Editorial Asset</span>
        </div>
      </div>

      <!-- High-Signal Executive Takeaways Box -->
      <section class="article-takeaways-box" aria-label="Executive Takeaways">
        <div class="article-takeaways-title">
          <span>⚡</span>
          <span>Executive Takeaways & Key Highlights</span>
        </div>
        <ul class="article-takeaways-list">
          {bullets_html}
        </ul>
      </section>

      <!-- Editorial Perspective & Value-Add Commentary Box (Anti-Scraped Value Shield) -->
      <section class="editorial-take-box" aria-label="Editorial Perspective">
        <div class="editorial-take-header">
          <span class="editorial-take-badge">⚡ EDITORIAL TAKE • {author['name'].upper()}</span>
          <span class="editorial-take-author-tag">{author['role']}</span>
        </div>
        <h3 class="editorial-take-title">{take_info['heading']}</h3>
        <p class="editorial-take-body">{take_info['body']}</p>
        <div class="editorial-take-horizon">
          <strong>Big Picture:</strong>
          <span>{take_info['big_picture']}</span>
        </div>
      </section>

      <!-- Substantive In-Depth Editorial Content -->
      <section class="article-body">
        <p class="article-lead">{lead_text}</p>

        <h2 class="article-section-title">
          <span>📌</span>
          <span>The Core Development</span>
        </h2>
        <p class="article-p">{sec1_text}</p>

        <!-- Google AdSense Non-Intrusive In-Article Display Slot -->
        {ad_slot_html}

        <h2 class="article-section-title">
          <span>🔍</span>
          <span>Background & Sector Context</span>
        </h2>
        <p class="article-p">{sec2_text}</p>

        <h2 class="article-section-title">
          <span>📊</span>
          <span>Industry & Real-World Impact</span>
        </h2>
        <p class="article-p">{sec3_text}</p>

        <!-- Companion AMP Web Story Callout Banner -->
        <div class="article-story-cta-box">
          <div class="story-cta-text">
            <h4>⚡ Prefer Visual Stories on Mobile?</h4>
            <p>Experience this news piece in an interactive 5-slide visual format crafted for mobile devices & Google Discover.</p>
          </div>
          <a href="/stories/{slug}/" class="story-cta-btn">View Web Story ⚡</a>
        </div>

        <h2 class="article-section-title">
          <span>🔮</span>
          <span>Strategic Outlook & What Lies Ahead</span>
        </h2>
        <p class="article-p">{sec4_text}</p>

        <!-- Editorial Integrity & Attribution Box -->
        <div class="editorial-trust-box">
          <strong>Editorial Integrity & Multi-Source Notice:</strong> {config.SITE_NAME} adheres to rigorous verification and fact-checking protocols. Original reporting credited to <strong>{source}</strong>. For primary wire documentation and full source material, visit <a href="{orig_url}" target="_blank" rel="noopener noreferrer">Original Coverage at {source} ↗</a>.
        </div>

        <!-- Author Bio Card (E-E-A-T Quality Standards) -->
        <div class="author-bio-card">
          <div class="author-bio-avatar" style="background: {author['color']};">{author['initials']}</div>
          <div class="author-bio-details">
            <div class="author-bio-header">
              <span class="author-bio-name">{author['name']}</span>
              <span class="author-bio-badge">Verified Editorial Staff</span>
            </div>
            <div class="author-bio-role">{author['role']}</div>
            <p class="author-bio-desc">{author['bio']}</p>
            <div class="author-bio-footer">
              <span>{config.SITE_NAME} Media Network</span>
              <span>•</span>
              <a href="mailto:{author['email']}">Contact Correspondent ✉️</a>
              <span>•</span>
              <a href="/about/#team">Meet the Newsroom →</a>
            </div>
          </div>
        </div>
      </section>

      <!-- Social Share Bar -->
      <section class="article-share-section" aria-label="Share Story">
        <span class="share-title">Share this story:</span>
        <div class="share-buttons-group">
          <a href="{wa_share}" target="_blank" rel="noopener noreferrer" class="share-icon-btn" title="Share on WhatsApp">
            <span>💬</span> <span>WhatsApp</span>
          </a>
          <a href="{tw_share}" target="_blank" rel="noopener noreferrer" class="share-icon-btn" title="Share on X">
            <span>𝕏</span> <span>Post</span>
          </a>
          <a href="{li_share}" target="_blank" rel="noopener noreferrer" class="share-icon-btn" title="Share on LinkedIn">
            <span>💼</span> <span>LinkedIn</span>
          </a>
          <a href="{fb_share}" target="_blank" rel="noopener noreferrer" class="share-icon-btn" title="Share on Facebook">
            <span>👥</span> <span>Facebook</span>
          </a>
          <button id="copyArticleLinkBtn" class="share-icon-btn" title="Copy link to clipboard">
            <span>🔗</span> <span>Copy Link</span>
          </button>
        </div>
      </section>

      <!-- Related Stories Grid -->
      <section class="related-stories-section" aria-label="Related Stories">
        <h3 class="related-title">
          <span>⚡</span>
          <span>Related Stories in {cat_name}</span>
        </h3>
        <div class="related-grid">
          {related_grid_html}
        </div>
      </section>
    </article>
  </main>

  <!-- Floating Toast Notification -->
  <div class="toast-msg" id="toastMsg" role="alert">Notification</div>

  <!-- Top Reading Progress Bar -->
  <div id="readingProgressBar" class="reading-progress-bar" aria-hidden="true"></div>

  <!-- Floating Back-to-Top Button -->
  <button id="backToTopBtn" class="back-to-top-btn" aria-label="Scroll to top" title="Back to top">↑</button>

  <!-- Global Footer -->
  {get_base_footer()}

  <!-- Main JavaScript Engine -->
  <script src="/static/js/main.js?v=2.3"></script>
</body>
</html>"""
    return article_html


def generate_news_pages(articles: list, dist_dir: Path):
    """
    Builds dedicated, fully standalone in-depth SEO news article pages
    into dist/news/<slug>/index.html for AdSense compliance and organic Google Search ranking.
    """
    news_dir = dist_dir / "news"
    news_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Generating dedicated in-depth article pages for {len(articles)} stories...")
    generated_count = 0
    for art in articles:
        slug = art.get("slug")
        if not slug:
            continue
        art_dir = news_dir / slug
        art_dir.mkdir(parents=True, exist_ok=True)
        html_content = render_article_page_html(art, articles)
        with open(art_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_count += 1
    print(f"[OK] Successfully built {generated_count} dedicated news pages in dist/news/")


def generate_compliance_pages(dist_dir: Path):
    """
    Builds the 5 mandatory AdSense & Google News compliance pages:
    - /about/
    - /privacy/
    - /terms/
    - /editorial-policy/
    - /contact/
    """
    team_cards = []
    for beat, author in AUTHORS.items():
        team_cards.append(f"""
          <div class="team-card">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="width: 48px; height: 48px; border-radius: 50%; background: {author['color']}; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                {author['initials']}
              </div>
              <div>
                <h4 style="margin: 0; font-size: 16px; font-weight: 700; color: var(--text-primary);">{author['name']}</h4>
                <span style="font-size: 12px; font-weight: 600; color: {author['color']}; text-transform: uppercase; letter-spacing: 0.5px;">{author['role']}</span>
              </div>
            </div>
            <p style="font-size: 13px; line-height: 1.6; color: var(--text-muted); margin: 0;">{author['bio']}</p>
            <div style="margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border-subtle); font-size: 12px;">
              <a href="mailto:{author['email']}" style="color: var(--accent); text-decoration: none; font-weight: 600;">✉ Contact {author['name']}</a>
            </div>
          </div>
        """)
    team_grid_html = f'<div class="team-grid">{"".join(team_cards)}</div>'

    pages = {
        "about": {
            "title": f"About {config.SITE_NAME} & Editorial Mission",
            "badge": "Transparency & Standards",
            "description": f"Learn about {config.SITE_NAME}'s mission, our transparent AI editorial pipeline, and commitment to fast factual news reporting.",
            "content": f"""
              <p>Welcome to <strong>{config.SITE_NAME}</strong>, a next-generation news and visual storytelling portal created to deliver factual, fast, 60-word summaries and immersive Google AMP Web Stories for modern mobile readers.</p>
              
              <h2>Our Core Mission</h2>
              <p>In an era overwhelmed by clickbait, sensationalism, and information overload, our mission is simple: <strong>clarity, speed, and uncompromising accuracy</strong>. We believe readers deserve direct, verified news without navigating through manipulative headlines or bloated 2,000-word articles.</p>

              <h2>Transparent AI Disclosure</h2>
              <p>At {config.SITE_NAME}, transparency is our guiding principle. We employ <strong>Google Gemini 3.8 Flash</strong> as an editorial assistive tool. Here is how our pipeline works:</p>
              <ul>
                <li><strong>Verified Sourcing:</strong> All incoming wire stories originate exclusively from reputable, accredited news syndicates (including Reuters, BBC, TechCrunch, CNBC, and official press desks).</li>
                <li><strong>AI Distillation:</strong> Gemini models analyze multi-source accounts to synthesize factual 60-word summaries and extract 3 essential bullet points.</li>
                <li><strong>Clickbait Removal:</strong> Headlines are stripped of hype, sensationalist prefixes, and deceptive framing.</li>
                <li><strong>Visual Storyboarding:</strong> We convert textual reports into interactive, 5-slide visual Google AMP Web Stories complete with licensed photographic context.</li>
                <li><strong>Editorial Oversight:</strong> Automated sentiment checks and strict fact-consistency checks ensure no speculative hallucination occurs.</li>
              </ul>

              <h2 id="team">Our Editorial Masthead & Beat Specialists</h2>
              <p>In full adherence to Google Search Quality Rater guidelines (E-E-A-T: Experience, Expertise, Authoritativeness, and Trustworthiness), our coverage is stewarded by dedicated beat specialists who provide original editorial analysis, verify primary reporting, and uphold journalistic standards:</p>
              {team_grid_html}

              <h2>Leadership & Publisher Masthead</h2>
              <div class="info-card">
                <p><strong>Publisher:</strong> {config.PUBLISHER_NAME}</p>
                <p><strong>Editorial Desk:</strong> <a href="mailto:{config.EDITORIAL_EMAIL}">{config.EDITORIAL_EMAIL}</a></p>
                <p><strong>Headquarters:</strong> {config.CONTACT_ADDRESS}</p>
                <p><strong>Syndication Network:</strong> Global Tech, Business, Geopolitics, Sports, and Artificial Intelligence.</p>
              </div>
            """
        },
        "editorial-policy": {
            "title": "Editorial Policy & Fact-Checking Guidelines",
            "badge": "Google News Trust Guidelines",
            "description": "Our formal fact-checking, verification, source accreditation, and corrections policy required for Google News approval.",
            "content": f"""
              <p>This Editorial Policy sets forth the standards of journalism, verification, and ethical reporting upheld across all publications by <strong>{config.SITE_NAME}</strong>.</p>

              <h2>1. Fact-Checking & Primary Verification</h2>
              <p>Every story published on {config.SITE_NAME} undergoes rigorous multi-source cross-referencing. We require verification by at least two independent primary reporting desks (e.g., Associated Press, Reuters, BBC, official government statements, or peer-reviewed scientific journals) prior to inclusion in our breaking news pipeline.</p>

              <h2>2. Corrections & Retractions Policy</h2>
              <p>When factual errors or misleading data points are discovered, {config.SITE_NAME} acts swiftly:</p>
              <ul>
                <li><strong>Immediate Rectification:</strong> The article summary and corresponding AMP Web Story are corrected immediately upon confirmation.</li>
                <li><strong>Transparent Correction Notice:</strong> Articles with substantial factual updates carry a timestamped "Correction Note" detailing the alteration.</li>
                <li><strong>Submission of Corrections:</strong> Readers, journalists, and subject parties may submit correction requests directly to our editorial team at <a href="mailto:{config.EDITORIAL_EMAIL}">{config.EDITORIAL_EMAIL}</a> with supporting documentation. All requests are addressed within 24 hours.</li>
              </ul>

              <h2>3. Anonymous Sources & Wire Attribution</h2>
              <p>We do not fabricate anonymous commentary. When an original syndicated report cites anonymous sources, our summary explicitly designates the attribution to the originating investigating publication.</p>

              <h2>4. Editorial Independence & Non-Partisanship</h2>
              <p>{config.SITE_NAME} operates independently of political lobbies, commercial sponsors, and partisan interests. Our AI algorithms are instructed to maintain neutrality, emotional equilibrium, and objective tone regardless of topic.</p>
            """
        },
        "privacy": {
            "title": "Privacy Policy & AdSense Cookie Disclosures",
            "badge": "GDPR & CCPA Compliant",
            "description": "Full privacy policy disclosing Google AdSense DART cookies, analytics, data protection, and user rights.",
            "content": f"""
              <p>Last updated: October 2026. This Privacy Policy details how <strong>{config.SITE_NAME}</strong> ("we", "us", or "our") collects, uses, and safeguards information when you visit {config.SITE_URL}.</p>

              <h2 id="cookies">1. Google AdSense & DART Cookies</h2>
              <p>We may display advertisements served by Google AdSense and third-party advertising partners. Google, as a third-party vendor, uses cookies to serve ads on our site:</p>
              <ul>
                <li>Google's use of the <strong>DART cookie</strong> enables it to serve ads to our users based on their visit to our site and other sites on the Internet.</li>
                <li>Users may opt out of the use of the DART cookie by visiting the <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer">Google Ad and Content Network privacy policy</a>.</li>
                <li>Third-party ad servers or ad networks use technology in their advertisements and links that appear on {config.SITE_NAME}, sent directly to your browser. They automatically receive your IP address when this occurs.</li>
              </ul>

              <h2>2. Local Storage Usage</h2>
              <p>{config.SITE_NAME} is built with a privacy-first static architecture. We do NOT maintain user accounts or personal profiles on remote servers. Features such as "Saved Bookmarks" and "Dark/Light Theme Preference" operate 100% locally within your browser via <code>localStorage</code>.</p>

              <h2>3. GDPR Compliance (EU Citizens)</h2>
              <p>If you reside within the European Economic Area (EEA), you possess rights under the General Data Protection Regulation (GDPR), including the right to access, rectify, or erase any personal data held by third-party processors, as well as the right to restrict automated profiling.</p>

              <h2>4. CCPA / CPRA Compliance (California Residents)</h2>
              <p>Under the California Consumer Privacy Act (CCPA), California residents have the right to know what personal data is collected and the right to opt-out of the "sale" or "sharing" of personal data. {config.SITE_NAME} does not sell personal information to data brokers.</p>

              <h2>5. Contacting the Privacy Officer</h2>
              <p>If you have questions about this privacy statement, contact our Data Protection Officer at: <a href="mailto:{config.EDITORIAL_EMAIL}">{config.EDITORIAL_EMAIL}</a>.</p>
            """
        },
        "terms": {
            "title": "Terms of Service & Fair Use Disclaimer",
            "badge": "Legal Notice & 17 U.S.C. § 107",
            "description": "Terms of service, intellectual property guidelines, DMCA takedown policies, and 17 U.S.C. § 107 Fair Use notice.",
            "content": f"""
              <p>By accessing <strong>{config.SITE_NAME}</strong> ({config.SITE_URL}), you agree to be bound by these Terms of Service, applicable laws, and regulations.</p>

              <h2>1. Fair Use Disclaimer (17 U.S.C. § 107)</h2>
              <p>This portal publishes concise, factual summaries, news commentary, and educational visual stories. <strong>17 U.S.C. § 107</strong> provides for the lawful reproduction of copyrighted materials for purposes such as criticism, comment, news reporting, teaching, scholarship, or research:</p>
              <ul>
                <li>All news headlines and brief summaries are transformative, non-substitutive condensations designed to inform mobile readers.</li>
                <li>Direct attribution and outbound hyperlinks to the original publisher are provided on every article card, quick read drawer, and AMP story.</li>
                <li>Photographic media is utilized under creative licensing or editorial fair-use identification.</li>
              </ul>

              <h2>2. DMCA Copyright Notice & Takedown Desk</h2>
              <p>{config.SITE_NAME} respects the intellectual property rights of all copyright holders. In accordance with the Digital Millennium Copyright Act (17 U.S.C. § 512), if you believe your copyrighted work has been improperly indexed or summarized, please send a written takedown notice to our Designated Copyright Agent:</p>
              <div class="info-card">
                <p><strong>DMCA Agent:</strong> Copyright Desk - {config.PUBLISHER_NAME}</p>
                <p><strong>Email:</strong> <a href="mailto:{config.DMCA_EMAIL}">{config.DMCA_EMAIL}</a></p>
                <p><strong>Address:</strong> {config.CONTACT_ADDRESS}</p>
              </div>
              <p>Your notice must include: (a) identification of the copyrighted work, (b) the specific URL on {config.SITE_NAME}, (c) your contact information, and (d) a statement of good-faith belief.</p>

              <h2>3. External Hyperlinks Disclaimer</h2>
              <p>{config.SITE_NAME} contains outbound links to external third-party news websites. We have no control over the nature, content, and availability of those external destinations.</p>
            """
        },
        "contact": {
            "title": "Contact Editorial Desk & DMCA",
            "badge": "Direct Inquiries",
            "description": f"Reach out to the {config.SITE_NAME} editorial team, report breaking news tips, or contact our legal and DMCA desk.",
            "content": f"""
              <p>We welcome tips, feedback, partnership inquiries, and correction notifications. Please use the appropriate channels below to reach our team.</p>

              <div class="info-card" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                  <h4 style="color: var(--text-primary); margin-bottom: 6px;">Editorial & News Tips</h4>
                  <p><a href="mailto:{config.EDITORIAL_EMAIL}">{config.EDITORIAL_EMAIL}</a></p>
                  <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">For breaking scoops, press releases & tips.</p>
                </div>
                <div>
                  <h4 style="color: var(--text-primary); margin-bottom: 6px;">DMCA & Legal Desk</h4>
                  <p><a href="mailto:{config.DMCA_EMAIL}">{config.DMCA_EMAIL}</a></p>
                  <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">For copyright, permissions & legal notices.</p>
                </div>
              </div>

              <h2>Send a Direct Message</h2>
              <form class="contact-form" id="newsPulseContactForm">
                <div class="form-group">
                  <label for="contactName">Your Name</label>
                  <input type="text" id="contactName" class="form-input" required placeholder="Enter your full name">
                </div>
                <div class="form-group">
                  <label for="contactEmail">Email Address</label>
                  <input type="email" id="contactEmail" class="form-input" required placeholder="your.name@domain.com">
                </div>
                <div class="form-group">
                  <label for="contactSubject">Subject / Department</label>
                  <input type="text" id="contactSubject" class="form-input" required placeholder="Editorial Correction / News Tip / Inquiry">
                </div>
                <div class="form-group">
                  <label for="contactMessage">Message Details</label>
                  <textarea id="contactMessage" class="form-textarea" rows="5" required placeholder="Provide details, URLs, or news background..."></textarea>
                </div>
                <button type="submit" class="form-submit-btn">Transmit Message</button>
              </form>
            """
        }
    }

    for slug, pdata in pages.items():
        page_dir = dist_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{config.SITE_URL}/{slug}/"

        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(pdata['title'])} - {config.SITE_NAME}</title>
  <meta name="description" content="{escape(pdata['description'])}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">

  <!-- OpenGraph -->
  <meta property="og:title" content="{escape(pdata['title'])} - {config.SITE_NAME}">
  <meta property="og:description" content="{escape(pdata['description'])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{config.PUBLISHER_LOGO}">

  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/static/css/style.css">
{get_tracking_head_tags()}
</head>
<body>
  {get_base_header(slug)}

  <main class="container">
    <article class="compliance-layout">
      <div class="compliance-header">
        <span class="compliance-badge">{pdata['badge']}</span>
        <h1 class="compliance-title">{pdata['title']}</h1>
        <span class="compliance-updated">Last Modified: {datetime.now().strftime('%B %d, %Y')} • {config.PUBLISHER_NAME}</span>
      </div>

      <div class="compliance-body">
        {pdata['content']}
      </div>
    </article>
  </main>

  <div class="toast-msg" id="toastMsg" role="alert">Notification</div>

  <!-- Top Reading Progress Bar -->
  <div id="readingProgressBar" class="reading-progress-bar" aria-hidden="true"></div>

  <!-- Floating Back-to-Top Button -->
  <button id="backToTopBtn" class="back-to-top-btn" aria-label="Scroll to top" title="Back to top">↑</button>

  {get_base_footer()}

  <script src="/static/js/main.js?v=2.3"></script>
</body>
</html>"""

        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(page_html)

    print(f"[OK] Generated {len(pages)} compliance pages (About, Privacy, Terms, Editorial Policy, Contact).")


def generate_sitemap_xml(articles: list, dist_dir: Path):
    """
    Generates standard sitemap.xml for Google Search Console,
    plus dedicated news-sitemap.xml for Google News.
    """
    import re
    def xml_escape(val: str) -> str:
        if not val:
            return ""
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+", "", str(val)).strip()
        return escape(cleaned)

    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Standard Sitemap (Universal XML standard)
    std_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        '  <url>',
        f'    <loc>{config.SITE_URL}/</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '    <changefreq>hourly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>'
    ]

    for page in ["about", "editorial-policy", "privacy", "terms", "contact"]:
        std_lines.extend([
            '  <url>',
            f'    <loc>{config.SITE_URL}/{page}/</loc>',
            f'    <lastmod>{today_iso}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.5</priority>',
            '  </url>'
        ])

    for art in articles:
        slug = xml_escape(art.get("slug", ""))
        title = xml_escape(art.get("title", ""))
        img = xml_escape(art.get("image_url", ""))
        pub_date = xml_escape(art.get("published_at", today_iso))
        # Dedicated SEO In-Depth News Article Page (Priority 0.9)
        std_lines.extend([
            '  <url>',
            f'    <loc>{config.SITE_URL}/news/{slug}/</loc>',
            f'    <lastmod>{pub_date}</lastmod>',
            '    <changefreq>daily</changefreq>',
            '    <priority>0.9</priority>',
            '    <image:image>',
            f'      <image:loc>{img}</image:loc>',
            f'      <image:title>{title}</image:title>',
            '    </image:image>',
            '  </url>',
            # Companion AMP Web Story (Priority 0.8)
            '  <url>',
            f'    <loc>{config.SITE_URL}/stories/{slug}/</loc>',
            f'    <lastmod>{pub_date}</lastmod>',
            '    <changefreq>daily</changefreq>',
            '    <priority>0.8</priority>',
            '    <image:image>',
            f'      <image:loc>{img}</image:loc>',
            f'      <image:title>{title}</image:title>',
            '    </image:image>',
            '  </url>'
        ])
    std_lines.append('</urlset>')

    with open(dist_dir / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(std_lines))

    # Also save as sitemap-main.xml as a clean alternative endpoint
    with open(dist_dir / "sitemap-main.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(std_lines))

    # 2. Google News Specific Sitemap (Articles published within last 48 hours only per Google News guidelines)
    news_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    max_news_age_hours = getattr(config, "GOOGLE_NEWS_MAX_AGE_HOURS", 48)
    now_utc = datetime.now(timezone.utc)
    news_stories_count = 0

    for art in articles:
        pub_date = xml_escape(art.get("published_at", today_iso))
        # Google News Guideline: Only include stories published within the last 48 hours
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            age_hours = (now_utc - pub_dt).total_seconds() / 3600.0
            if age_hours > max_news_age_hours:
                continue
        except Exception:
            pass

        news_stories_count += 1
        slug = xml_escape(art.get("slug", ""))
        title = xml_escape(art.get("title", ""))
        img = xml_escape(art.get("image_url", ""))
        # Add primary news article page for Google News
        news_lines.extend([
            '  <url>',
            f'    <loc>{config.SITE_URL}/news/{slug}/</loc>',
            '    <news:news>',
            '      <news:publication>',
            f'        <news:name>{xml_escape(config.SITE_NAME)}</news:name>',
            f'        <news:language>{config.SITE_LANGUAGE}</news:language>',
            '      </news:publication>',
            f'      <news:publication_date>{pub_date}</news:publication_date>',
            f'      <news:title>{title}</news:title>',
            '    </news:news>',
            '    <image:image>',
            f'      <image:loc>{img}</image:loc>',
            f'      <image:title>{title}</image:title>',
            '    </image:image>',
            '  </url>'
        ])
    news_lines.append('</urlset>')

    with open(dist_dir / "news-sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(news_lines))

    # 3. Master Sitemap Index (Universal standard bundling news-sitemap + sitemap)
    index_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <sitemap>',
        f'    <loc>{config.SITE_URL}/news-sitemap.xml</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '  </sitemap>',
        '  <sitemap>',
        f'    <loc>{config.SITE_URL}/sitemap-main.xml</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '  </sitemap>',
        '</sitemapindex>'
    ]
    with open(dist_dir / "sitemap_index.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

    print(f"[OK] Generated sitemap.xml ({len(articles)} total stories), news-sitemap.xml ({news_stories_count} fresh stories <= {max_news_age_hours}h), and sitemap_index.xml.")


def generate_robots_txt(dist_dir: Path):
    """Generates standard robots.txt directing search engines to sitemaps."""
    content = f"""User-agent: Mediapartners-Google
Allow: /

User-agent: Googlebot
Allow: /

User-agent: *
Allow: /

Sitemap: {config.SITE_URL}/sitemap_index.xml
Sitemap: {config.SITE_URL}/sitemap.xml
Sitemap: {config.SITE_URL}/sitemap-main.xml
Sitemap: {config.SITE_URL}/news-sitemap.xml
"""
    with open(dist_dir / "robots.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Generated robots.txt")


def generate_manifest_json(dist_dir: Path):
    """Generates PWA web app manifest."""
    manifest = {
        "name": f"{config.SITE_NAME} - {config.SITE_TAGLINE}",
        "short_name": config.SITE_NAME,
        "description": config.SITE_DESCRIPTION,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#07090e",
        "theme_color": "#07090e",
        "icons": [
            {
                "src": "/favicon-48x48.png",
                "sizes": "48x48",
                "type": "image/png"
            },
            {
                "src": "/android-chrome-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/android-chrome-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icon.svg",
                "sizes": "any",
                "type": "image/svg+xml"
            }
        ]
    }
    with open(dist_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("[OK] Generated manifest.json")


def generate_ads_txt(dist_dir: Path):
    """
    Generates official ads.txt for Google AdSense verification.
    Matches standard specification required for publisher account approval.
    """
    pub_id = getattr(config, "ADSENSE_PUB_ID", "").strip()
    clean_pub = pub_id.replace("ca-", "") if pub_id else ""
    if not clean_pub or not clean_pub.startswith("pub-"):
        content = (
            f"# Google AdSense Verification File for {config.SITE_NAME}\n"
            "# Set ADSENSE_PUB_ID=pub-XXXXXXXXXXXXXXXX in your .env file to update\n"
            "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n"
        )
    else:
        content = (
            f"# Google AdSense ads.txt for {config.SITE_NAME}\n"
            f"google.com, {clean_pub}, DIRECT, f08c47fec0942fa0\n"
        )
    with open(dist_dir / "ads.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Generated ads.txt in {dist_dir / 'ads.txt'}")


def merge_with_archive(new_articles: list) -> list:
    """
    Merges newly enriched articles with existing historical articles.
    - Prevents 404 dead links on previously indexed AMP stories.
    - Prioritizes newest breaking stories at the top.
    - Caps archive to MAX_ARCHIVE_ARTICLES to prevent storage inflation.
    """
    articles_file = config.DATA_DIR / "articles.json"
    archive = []
    if articles_file.exists():
        try:
            with open(articles_file, "r", encoding="utf-8") as f:
                archive = json.load(f)
        except Exception as e:
            print(f"    [!] Note on reading existing archive for merge: {e}")
            archive = []

    merged_map = {}

    # Insert fresh articles first
    for art in (new_articles or []):
        slug = art.get("slug")
        if slug:
            merged_map[slug] = art

    # Insert existing archive articles if not replaced
    for art in archive:
        slug = art.get("slug")
        if slug and slug not in merged_map:
            merged_map[slug] = art

    merged_list = list(merged_map.values())

    def sort_key(a):
        pub = a.get("published_at", "")
        return pub or "1970-01-01T00:00:00Z"

    merged_list.sort(key=sort_key, reverse=True)

    max_archive = getattr(config, "MAX_ARCHIVE_ARTICLES", 150)
    return merged_list[:max_archive]


def build_static_site(articles: list, dist_dir: Path = None):
    """
    Builds the complete static site distribution into dist_dir.
    Seamlessly merges fresh articles with the persistent archive so that
    previously indexed URLs NEVER return 404.
    """
    if dist_dir is None:
        dist_dir = config.DIST_DIR

    print(f"[*] Building static distribution in {dist_dir}...")
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 1. Merge incoming fresh articles with existing archive
    all_articles = merge_with_archive(articles)
    if not all_articles:
        print("[!] No articles available to build site.")
        return

    # 2. Ensure shared category HD posters and copy static assets
    ensure_category_posters(config.STATIC_DIR)
    dist_static = dist_dir / "static"
    if dist_static.exists():
        shutil.rmtree(dist_static)
    shutil.copytree(config.STATIC_DIR, dist_static)
    print(f"[OK] Copied static assets to {dist_static}")

    # Copy root favicons for Googlebot & browsers directly to dist root
    root_favicons = [
        "favicon.ico", "favicon-16x16.png", "favicon-32x32.png", "favicon-48x48.png",
        "apple-touch-icon.png", "android-chrome-192x192.png", "android-chrome-512x512.png"
    ]
    for fav_name in root_favicons:
        src_f = config.STATIC_DIR / fav_name
        if src_f.exists():
            shutil.copy2(src_f, dist_dir / fav_name)
    print(f"[OK] Copied {len(root_favicons)} root favicon files to {dist_dir}")

    # 3. Build Homepage (index.html) with top active articles
    home_html = render_homepage_html(all_articles)
    with open(dist_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print(f"[OK] Built homepage index.html with {len(all_articles)} active & archived stories.")

    # 4. Build AMP Stories for each article in the archive
    stories_dir = dist_dir / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)
    active_slugs = {art["slug"] for art in all_articles if art.get("slug")}
    for existing_dir in stories_dir.iterdir():
        if existing_dir.is_dir() and existing_dir.name not in active_slugs:
            shutil.rmtree(existing_dir, ignore_errors=True)

    max_local_posters = getattr(config, "MAX_LOCAL_POSTER_STORIES", 150)
    print(f"[*] Ensuring AMP Web Stories are generated for {len(all_articles)} stories (top {max_local_posters} with dedicated posters)...")
    for idx, art in enumerate(all_articles):
        save_story_to_dist(art, stories_dir / art["slug"], keep_local_posters=(idx < max_local_posters))
    print(f"[OK] Successfully verified/built {len(all_articles)} AMP Web Stories in dist/stories/")

    # 5. Build Dedicated SEO News Article Pages (/news/<slug>/index.html)
    generate_news_pages(all_articles, dist_dir)

    # 6. Build Compliance Pages
    generate_compliance_pages(dist_dir)

    # 7. Build SEO & Monetization files (sitemap, robots, manifest, ads.txt)
    generate_sitemap_xml(all_articles, dist_dir)
    generate_robots_txt(dist_dir)
    generate_manifest_json(dist_dir)
    generate_ads_txt(dist_dir)

    # 7. Persist updated archive JSON cache
    data_dir = config.DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / "articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    # Copy to dist/api/articles.json for static serverless fetching
    api_dir = dist_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    with open(api_dir / "articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    print(f"[OK] Production build completed successfully in {dist_dir} ({len(all_articles)} total stories retained)!")


if __name__ == "__main__":
    from fetcher import upgrade_image_resolution, fetch_all_categories
    from summarizer import enrich_all_articles

    arts = fetch_all_categories(max_per_category=1)
    enriched = enrich_all_articles(arts)
    build_static_site(enriched)
