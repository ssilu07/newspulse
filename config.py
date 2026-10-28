"""
NewsPulse - Central Configuration Module
Customizable branding, category definitions, RSS sources, and AI model parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DIST_DIR = BASE_DIR / "dist"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Site Identity & Branding
SITE_NAME = os.getenv("SITE_NAME", "News Seconds")
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "Bite-Sized EVs, Supercars & Future Mobility in Seconds")
SITE_DESCRIPTION = os.getenv(
    "SITE_DESCRIPTION",
    "Your 60-second pit stop for breaking electric vehicle breakthroughs, supercar debuts, Tesla leaks, and autonomous mobility."
)
SITE_URL = os.getenv("SITE_URL", "https://newsseconds.com").rstrip("/")
SITE_LOCALE = "en_US"
SITE_LANGUAGE = "en"

# Publisher Details for Schema & Compliance
PUBLISHER_NAME = os.getenv("PUBLISHER_NAME", "News Seconds Media Network")
PUBLISHER_LOGO = f"{SITE_URL}/static/assets/logo.png"
EDITORIAL_EMAIL = os.getenv("EDITORIAL_EMAIL", "editorial@newsseconds.com")
DMCA_EMAIL = os.getenv("DMCA_EMAIL", "dmca@newsseconds.com")
CONTACT_ADDRESS = os.getenv("CONTACT_ADDRESS", "548 Market St, Suite 72401, San Francisco, CA 94104")

# Gemini AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_RETRY_ATTEMPTS = int(os.getenv("GEMINI_RETRY_ATTEMPTS", "2"))
GEMINI_PACING_DELAY_SECONDS = float(os.getenv("GEMINI_PACING_DELAY_SECONDS", "0.6"))

# Google-Compliant Ingestion & Anti-Spam Rate Limits (Scaled Content Prevention)
MAX_ARTICLES_PER_CATEGORY = int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "2"))
MAX_TOTAL_FRESH_ARTICLES = int(os.getenv("MAX_TOTAL_FRESH_ARTICLES", "14"))
MAX_ARCHIVE_ARTICLES = int(os.getenv("MAX_ARCHIVE_ARTICLES", "150"))
MAX_LOCAL_POSTER_STORIES = int(os.getenv("MAX_LOCAL_POSTER_STORIES", "30"))
MAX_ARTICLE_AGE_HOURS = int(os.getenv("MAX_ARTICLE_AGE_HOURS", "48"))
SUMMARY_WORD_TARGET = 60

# Network Resilience & Timeouts
FEED_TIMEOUT_SECONDS = float(os.getenv("FEED_TIMEOUT_SECONDS", "7.0"))

# Social Syndication Anti-Spam Limits & Toggles
SOCIAL_MAX_POSTS_PER_RUN = int(os.getenv("SOCIAL_MAX_POSTS_PER_RUN", "2"))
SOCIAL_POST_DELAY_SECONDS = float(os.getenv("SOCIAL_POST_DELAY_SECONDS", "6.0"))
ENABLE_TELEGRAM_POSTING = os.getenv("ENABLE_TELEGRAM_POSTING", "false").lower() in ("true", "1", "yes")
ENABLE_TWITTER_POSTING = os.getenv("ENABLE_TWITTER_POSTING", "true").lower() in ("true", "1", "yes")
ENABLE_REDDIT_POSTING = os.getenv("ENABLE_REDDIT_POSTING", "true").lower() in ("true", "1", "yes")
ENABLE_LINKEDIN_POSTING = os.getenv("ENABLE_LINKEDIN_POSTING", "true").lower() in ("true", "1", "yes")
ENABLE_TUMBLR_POSTING = os.getenv("ENABLE_TUMBLR_POSTING", "true").lower() in ("true", "1", "yes")
TUMBLR_BLOG_NAME = os.getenv("TUMBLR_BLOG_NAME", "newsseconds.tumblr.com")

# Google News Sitemap Age (Google News Guidelines strictly require <= 48 hours for news-sitemap.xml)
GOOGLE_NEWS_MAX_AGE_HOURS = 48

# Analytics & Tracking
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "XMDt3lDT2kpdjLlHlxQCSn5EcJcH2yw8f6nLjhLgN7g")
CLARITY_PROJECT_ID = os.getenv("CLARITY_PROJECT_ID", "yw5kuxh5pg")
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-VX6D7B7WD6")
GA_PROPERTY_ID = os.getenv("GA_PROPERTY_ID", "558495815")
GA_CREDENTIALS_FILE = os.getenv("GA_CREDENTIALS_FILE", "ga_credentials.json")
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "79624caa6fca40dfbc227ab2ed0f7f42")

# Google AdSense Publisher Settings
# Set ADSENSE_PUB_ID (e.g. 'pub-1234567890123456' or 'ca-pub-1234567890123456') in .env
ADSENSE_PUB_ID = os.getenv("ADSENSE_PUB_ID", "")


# Categories and High-Reliability RSS Feeds
CATEGORIES = {
    "world": {
        "name": "EVs & Clean Mobility",
        "slug": "world",
        "color": "#06b6d4",
        "gradient": "linear-gradient(135deg, #06b6d4, #3b82f6)",
        "icon": "⚡",
        "description": "Tesla, BYD, Rivian, next-gen sodium and solid-state batteries, and electric charging networks.",
        "feeds": [
            "https://electrek.co/feed/",
            "https://cleantechnica.com/feed/",
            "https://techcrunch.com/category/transportation/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1600&h=900&fit=crop"
    },
    "tech": {
        "name": "Supercars & Hypercars",
        "slug": "tech",
        "color": "#ef4444",
        "gradient": "linear-gradient(135deg, #ef4444, #f97316)",
        "icon": "🏎️",
        "description": "Ferrari, Porsche, Lamborghini, McLaren, hypercar track telemetry, and aero breakthroughs.",
        "feeds": [
            "https://www.caranddriver.com/rss/all.xml",
            "https://www.carscoops.com/feed/",
            "https://jalopnik.com/rss"
        ],
        "default_image": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=1600&h=900&fit=crop"
    },
    "ai-future": {
        "name": "Robo-Taxis & Autonomous",
        "slug": "ai-future",
        "color": "#8b5cf6",
        "gradient": "linear-gradient(135deg, #8b5cf6, #ec4899)",
        "icon": "🤖",
        "description": "Tesla Full Self-Driving (FSD), Waymo, robotaxis, automotive lidar, and AI smart cockpits.",
        "feeds": [
            "https://techcrunch.com/category/transportation/feed/",
            "https://electrek.co/category/autonomous/feed/",
            "https://cleantechnica.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1600&h=900&fit=crop"
    },
    "business": {
        "name": "Auto Industry & Deals",
        "slug": "business",
        "color": "#10b981",
        "gradient": "linear-gradient(135deg, #10b981, #06b6d4)",
        "icon": "📈",
        "description": "Automaker earnings, gigafactory expansions, battery supply-chains, and global automotive tariffs.",
        "feeds": [
            "https://electrek.co/feed/",
            "https://cleantechnica.com/feed/",
            "https://www.carscoops.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1600&h=900&fit=crop"
    },
    "trending": {
        "name": "Viral Drives & Concepts",
        "slug": "trending",
        "color": "#f43f5e",
        "gradient": "linear-gradient(135deg, #f43f5e, #fb923c)",
        "icon": "🔥",
        "description": "Radical concept vehicles, world speed records, spy shots, and viral custom engineering.",
        "feeds": [
            "https://jalopnik.com/rss",
            "https://www.carscoops.com/feed/",
            "https://www.caranddriver.com/rss/all.xml"
        ],
        "default_image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1600&h=900&fit=crop"
    },
    "sports": {
        "name": "Motorsport & F1 Tech",
        "slug": "sports",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b, #ef4444)",
        "icon": "🏁",
        "description": "Formula 1 telemetry, aerodynamic upgrades, Formula E electric racing, and Le Mans hypercars.",
        "feeds": [
            "https://the-race.com/feed/",
            "https://www.autosport.com/rss/f1/news/"
        ],
        "default_image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1600&h=900&fit=crop"
    },
    "entertainment": {
        "name": "Car Culture & Restomods",
        "slug": "entertainment",
        "color": "#ec4899",
        "gradient": "linear-gradient(135deg, #ec4899, #8b5cf6)",
        "icon": "🎬",
        "description": "V8 restomods, legendary barn finds, cinema car chases, and iconic gearhead culture.",
        "feeds": [
            "https://silodrome.com/feed/",
            "https://jalopnik.com/rss",
            "https://www.caranddriver.com/rss/all.xml"
        ],
        "default_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1600&h=900&fit=crop"
    }
}

# Curated High-Definition Story Background Images per category for AMP slide sequencing
SLIDE_IMAGE_COLLECTIONS = {
    "world": [
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1536700503339-1e4b06520771?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop"
    ],
    "tech": [
        "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1080&h=1920&fit=crop"
    ],
    "ai-future": [
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1080&h=1920&fit=crop"
    ],
    "business": [
        "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1080&h=1920&fit=crop"
    ],
    "trending": [
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=1080&h=1920&fit=crop"
    ],
    "sports": [
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=1080&h=1920&fit=crop"
    ],
    "entertainment": [
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1080&h=1920&fit=crop"
    ]
}
