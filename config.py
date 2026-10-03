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
SITE_NAME = os.getenv("SITE_NAME", "NewsPulse")
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "Bite-Sized Breaking News & Visual Stories")
SITE_DESCRIPTION = os.getenv(
    "SITE_DESCRIPTION",
    "Real-time, factual 60-word news summaries and immersive visual AMP Web Stories powered by AI."
)
SITE_URL = os.getenv("SITE_URL", "https://newspulse-beta.vercel.app").rstrip("/")
SITE_LOCALE = "en_US"
SITE_LANGUAGE = "en"

# Publisher Details for Schema & Compliance
PUBLISHER_NAME = os.getenv("PUBLISHER_NAME", "NewsPulse Media Network")
PUBLISHER_LOGO = f"{SITE_URL}/static/assets/logo.png"
EDITORIAL_EMAIL = os.getenv("EDITORIAL_EMAIL", "editorial@newspulse.media")
DMCA_EMAIL = os.getenv("DMCA_EMAIL", "dmca@newspulse.media")
CONTACT_ADDRESS = os.getenv("CONTACT_ADDRESS", "548 Market St, Suite 72401, San Francisco, CA 94104")

# Gemini AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Ingestion Settings
MAX_ARTICLES_PER_CATEGORY = int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "5"))
SUMMARY_WORD_TARGET = 60

# Categories and High-Reliability RSS Feeds
CATEGORIES = {
    "tech": {
        "name": "Tech",
        "slug": "tech",
        "color": "#06b6d4",
        "gradient": "linear-gradient(135deg, #06b6d4, #3b82f6)",
        "icon": "⚡",
        "description": "Silicon, startups, breakthrough tech and digital transformation.",
        "feeds": [
            "https://techcrunch.com/feed/",
            "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.arstechnica.com/arstechnica/index"
        ],
        "default_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=800&fit=crop"
    },
    "ai-future": {
        "name": "AI & Future",
        "slug": "ai-future",
        "color": "#8b5cf6",
        "gradient": "linear-gradient(135deg, #8b5cf6, #ec4899)",
        "icon": "🧠",
        "description": "Artificial intelligence, frontier models, robotics, and deep science.",
        "feeds": [
            "https://news.google.com/rss/search?q=Artificial+Intelligence+when:2d&hl=en-US&gl=US&ceid=US:en",
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://www.technologyreview.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&h=800&fit=crop"
    },
    "business": {
        "name": "Business",
        "slug": "business",
        "color": "#10b981",
        "gradient": "linear-gradient(135deg, #10b981, #06b6d4)",
        "icon": "📈",
        "description": "Global markets, finance, economy, and corporate developments.",
        "feeds": [
            "http://feeds.bbci.co.uk/news/business/rss.xml",
            "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
        ],
        "default_image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop"
    },
    "world": {
        "name": "World",
        "slug": "world",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b, #ef4444)",
        "icon": "🌐",
        "description": "Geopolitics, international diplomacy, global events, and treaties.",
        "feeds": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
            "https://www.aljazeera.com/xml/rss/all.xml"
        ],
        "default_image": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1200&h=800&fit=crop"
    },
    "sports": {
        "name": "Sports",
        "slug": "sports",
        "color": "#ef4444",
        "gradient": "linear-gradient(135deg, #ef4444, #f97316)",
        "icon": "🏆",
        "description": "Championships, leagues, athletes, records, and thrilling match highlights.",
        "feeds": [
            "http://feeds.bbci.co.uk/sport/rss.xml",
            "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US&ceid=US:en",
            "https://www.espn.com/espn/rss/news"
        ],
        "default_image": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&h=800&fit=crop"
    },
    "entertainment": {
        "name": "Entertainment",
        "slug": "entertainment",
        "color": "#ec4899",
        "gradient": "linear-gradient(135deg, #ec4899, #8b5cf6)",
        "icon": "🎬",
        "description": "Cinema, streaming, pop culture, music, and celebrity spotlights.",
        "feeds": [
            "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
            "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en"
        ],
        "default_image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200&h=800&fit=crop"
    }
}

# Curated High-Definition Story Background Images per category for AMP slide sequencing
SLIDE_IMAGE_COLLECTIONS = {
    "tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=1080&h=1920&fit=crop"
    ],
    "ai-future": [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1677442136019-21780efad99a?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1617791160505-6f00504e3519?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=1080&h=1920&fit=crop"
    ],
    "business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1080&h=1920&fit=crop"
    ],
    "world": [
        "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1572949645841-094f3a9c4c94?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1080&h=1920&fit=crop"
    ],
    "sports": [
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1080&h=1920&fit=crop"
    ],
    "entertainment": [
        "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1080&h=1920&fit=crop"
    ]
}
