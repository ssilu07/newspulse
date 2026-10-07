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
from story_generator import save_story_to_dist

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


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
          <input type="text" id="newsSearchInput" class="search-input" placeholder="Search news, topics, keywords..." aria-label="Search news">
        </div>
      </div>

      <div class="header-actions">
        <a href="https://t.me/minutenewshub" target="_blank" rel="noopener" class="telegram-header-badge" style="display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 136, 204, 0.18); border: 1px solid rgba(0, 136, 204, 0.45); color: #38bdf8; text-decoration: none; padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600; transition: all 0.2s;" title="Join Minute News on Telegram">
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
            <li><a href="/#trending">🔥 Trending Now</a></li>
            <li><a href="/#tech">Tech & Startups</a></li>
            <li><a href="/#ai-future">AI & Robotics</a></li>
            <li><a href="/#business">Global Markets</a></li>
            <li><a href="/#world">World Affairs</a></li>
            <li><a href="/#sports">Sports Wire</a></li>
            <li><a href="/#entertainment">Entertainment</a></li>
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
    pills_html_list = ['<button class="cat-pill active" data-cat="all">⚡ All Stories</button>']
    for cat_slug, cat_info in config.CATEGORIES.items():
        icon = cat_info.get("icon", "•")
        name = cat_info.get("name")
        pills_html_list.append(f'<button class="cat-pill" data-cat="{cat_slug}">{icon} {name}</button>')
    pills_html = "\n".join(pills_html_list)

    # Hero Spotlight Card (Top Breaking Story)
    hero_html = ""
    grid_articles = articles
    if articles:
        hero_art = articles[0]
        h_id = hero_art.get("id")
        h_slug = hero_art.get("slug")
        h_cat_slug = hero_art.get("category")
        h_cat_name = escape(hero_art.get("category_name", "Breaking"))
        h_cat_color = hero_art.get("category_color", "#ef4444")
        h_title = escape(hero_art.get("title", ""))
        h_summary = escape(hero_art.get("summary", ""))
        h_source = escape(hero_art.get("source", "NewsPulse"))
        h_time_ago = escape(hero_art.get("time_ago", "Just now"))
        h_image = escape(hero_art.get("image_url", ""))
        h_orig_url = escape(hero_art.get("original_url", "#"))
        h_bullets = hero_art.get("bullet_points", [])
        h_bullets_json = escape(json.dumps(h_bullets))

        h_bullets_list_html = "".join([f"<li>{escape(b)}</li>" for b in h_bullets[:3]])

        hero_html = f"""
    <!-- Editor's Spotlight Hero -->
    <section class="featured-hero-section" id="heroSection" aria-label="Editor's Spotlight">
      <div class="section-label-row">
        <h2 class="section-heading">
          <span class="live-dot"></span>
          <span>Editor's Spotlight</span>
        </h2>
        <span class="spotlight-tag">⚡ TOP BREAKING</span>
      </div>
      <article class="news-card featured-news-card"
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
          <img src="{h_image}" alt="{h_title}" class="card-img" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop';">
          <span class="card-tag" style="background-color: {h_cat_color};">{h_cat_name}</span>
          <span class="card-meta-badge">🕒 {h_time_ago}</span>
        </div>

        <div class="card-body featured-body">
          <div class="card-source-row">
            <span class="card-source"><span class="source-dot"></span>{h_source}</span>
            <span class="read-badge">⚡ 1 min read</span>
          </div>
          <h2 class="card-title featured-title">{h_title}</h2>
          <p class="card-summary featured-summary">{h_summary}</p>

          <div class="featured-takeaways-box">
            <div class="featured-takeaways-title">Key Takeaways</div>
            <ul class="featured-takeaways-list">
              {h_bullets_list_html}
            </ul>
          </div>

          <div class="card-actions">
            <div class="action-btn-group">
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
    </section>
"""
        grid_articles = articles[1:] if len(articles) > 1 else articles

    # Article Cards
    cards_html_list = []
    for art in grid_articles:
        art_id = art.get("id")
        slug = art.get("slug")
        cat_slug = art.get("category")
        cat_name = escape(art.get("category_name", "News"))
        cat_color = art.get("category_color", "#3b82f6")
        title = escape(art.get("title", ""))
        summary = escape(art.get("summary", ""))
        source = escape(art.get("source", "NewsPulse"))
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
            <img src="{image}" alt="{title}" class="card-img" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&fit=crop';">
            <span class="card-tag" style="background-color: {cat_color};">{cat_name}</span>
            <span class="card-meta-badge">🕒 {time_ago}</span>
          </div>

          <div class="card-body">
            <div class="card-source-row">
              <span class="card-source"><span class="source-dot"></span>{source}</span>
              <span class="read-badge">1 min read</span>
            </div>
            <h3 class="card-title">{title}</h3>
            <p class="card-summary">{summary}</p>

            <div class="card-actions">
              <div class="action-btn-group">
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
            "https://twitter.com/NewsPulse",
            "https://facebook.com/NewsPulse"
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

  <!-- Favicon & PWA -->
  <link rel="icon" type="image/svg+xml" href="/static/assets/icon.svg">
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#07090e">

  <!-- Stylesheet -->
  <link rel="stylesheet" href="/static/css/style.css">

  <!-- Google Search Console Verification -->
  {f'<meta name="google-site-verification" content="{config.GOOGLE_SITE_VERIFICATION}">' if getattr(config, 'GOOGLE_SITE_VERIFICATION', '') else ''}

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

  <!-- Header -->
  {get_base_header("home")}

  <main class="container">
    <!-- Visual Web Stories Carousel -->
    <section class="stories-section" aria-label="Visual Web Stories">
      <div class="section-label-row">
        <h2 class="section-heading">
          <span class="dot"></span>
          <span>Trending Web Stories</span>
        </h2>
        <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">TAP TO VIEW 5-SLIDE VISUALS</span>
      </div>
      <div class="stories-carousel">
        {bubbles_html}
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

  <!-- Footer -->
  {get_base_footer()}

  <!-- Main JavaScript Engine -->
  <script src="/static/js/main.js"></script>
</body>
</html>"""
    return full_html


def generate_compliance_pages(dist_dir: Path):
    """
    Builds the 5 mandatory AdSense & Google News compliance pages:
    - /about/
    - /privacy/
    - /terms/
    - /editorial-policy/
    - /contact/
    """
    pages = {
        "about": {
            "title": "About NewsPulse & Editorial Mission",
            "badge": "Transparency & Standards",
            "description": "Learn about NewsPulse's mission, our transparent AI editorial pipeline, and commitment to fast factual news reporting.",
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

              <h2>1. Google AdSense & DART Cookies</h2>
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
            "description": "Reach out to the NewsPulse editorial team, report breaking news tips, or contact our legal and DMCA desk.",
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
                  <input type="text" id="contactName" class="form-input" required placeholder="Jane Doe">
                </div>
                <div class="form-group">
                  <label for="contactEmail">Email Address</label>
                  <input type="email" id="contactEmail" class="form-input" required placeholder="jane@example.com">
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

  <link rel="icon" type="image/svg+xml" href="/static/assets/icon.svg">
  <link rel="stylesheet" href="/static/css/style.css">
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

  {get_base_footer()}

  <script src="/static/js/main.js"></script>
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
        slug = art.get("slug")
        title = escape(art.get("title", ""))
        img = escape(art.get("image_url", ""))
        pub_date = art.get("published_at", today_iso)
        std_lines.extend([
            '  <url>',
            f'    <loc>{config.SITE_URL}/stories/{slug}/</loc>',
            f'    <lastmod>{pub_date}</lastmod>',
            '    <changefreq>daily</changefreq>',
            '    <priority>0.9</priority>',
            '    <image:image>',
            f'      <image:loc>{img}</image:loc>',
            f'      <image:title>{title}</image:title>',
            '    </image:image>',
            '  </url>'
        ])
    std_lines.append('</urlset>')

    with open(dist_dir / "sitemap.xml", "w", encoding="utf-8") as f:
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
        pub_date = art.get("published_at", today_iso)
        # Google News Guideline: Only include stories published within the last 48 hours
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            age_hours = (now_utc - pub_dt).total_seconds() / 3600.0
            if age_hours > max_news_age_hours:
                continue
        except Exception:
            pass

        news_stories_count += 1
        slug = art.get("slug")
        title = escape(art.get("title", ""))
        img = escape(art.get("image_url", ""))
        news_lines.extend([
            '  <url>',
            f'    <loc>{config.SITE_URL}/stories/{slug}/</loc>',
            '    <news:news>',
            '      <news:publication>',
            f'        <news:name>{escape(config.SITE_NAME)}</news:name>',
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

    print(f"[OK] Generated sitemap.xml ({len(articles)} total stories) and news-sitemap.xml ({news_stories_count} fresh stories <= {max_news_age_hours}h).")


def generate_robots_txt(dist_dir: Path):
    """Generates standard robots.txt directing search engines to sitemaps."""
    content = f"""User-agent: *
Allow: /

Sitemap: {config.SITE_URL}/sitemap.xml
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
                "src": "/static/assets/icon.svg",
                "sizes": "any",
                "type": "image/svg+xml"
            }
        ]
    }
    with open(dist_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("[OK] Generated manifest.json")


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

    # 2. Copy static assets
    dist_static = dist_dir / "static"
    if dist_static.exists():
        shutil.rmtree(dist_static)
    shutil.copytree(config.STATIC_DIR, dist_static)
    print(f"[OK] Copied static assets to {dist_static}")

    # 3. Build Homepage (index.html) with top active articles
    home_html = render_homepage_html(all_articles)
    with open(dist_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print(f"[OK] Built homepage index.html with {len(all_articles)} active & archived stories.")

    # 4. Build AMP Stories for each article in the archive
    stories_dir = dist_dir / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Ensuring AMP Web Stories are generated for {len(all_articles)} stories...")
    for art in all_articles:
        save_story_to_dist(art, stories_dir / art["slug"])
    print(f"[OK] Successfully verified/built {len(all_articles)} AMP Web Stories in dist/stories/")

    # 5. Build Compliance Pages
    generate_compliance_pages(dist_dir)

    # 6. Build SEO files (sitemap, robots, manifest)
    generate_sitemap_xml(all_articles, dist_dir)
    generate_robots_txt(dist_dir)
    generate_manifest_json(dist_dir)

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
