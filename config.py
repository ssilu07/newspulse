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
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "India's High-Velocity Automotive & RTO Intelligence")
SITE_DESCRIPTION = os.getenv(
    "SITE_DESCRIPTION",
    "Unfiltered Indian automobile news, new traffic challan rules, real-world mileage tests, year-end car discounts, and leaked SUV spyshots in bite-sized seconds."
)
SITE_URL = os.getenv("SITE_URL", "https://newsseconds.com").rstrip("/")
SITE_LOCALE = "en_IN"
SITE_LANGUAGE = "en"

# Publisher Details for Schema & Compliance
PUBLISHER_NAME = os.getenv("PUBLISHER_NAME", "News Seconds Automotive Network")
PUBLISHER_LOGO = f"{SITE_URL}/static/assets/logo.png"
EDITORIAL_EMAIL = os.getenv("EDITORIAL_EMAIL", "editorial@newsseconds.com")
DMCA_EMAIL = os.getenv("DMCA_EMAIL", "dmca@newsseconds.com")
CONTACT_ADDRESS = os.getenv("CONTACT_ADDRESS", "DLF Cyber City, Phase II, Sector 24, Gurugram, Haryana 122002, India")

# Gemini AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_RETRY_ATTEMPTS = int(os.getenv("GEMINI_RETRY_ATTEMPTS", "2"))
GEMINI_PACING_DELAY_SECONDS = float(os.getenv("GEMINI_PACING_DELAY_SECONDS", "0.6"))

# Google-Compliant Ingestion & Anti-Spam Rate Limits (Scaled Content Prevention)
MAX_ARTICLES_PER_CATEGORY = int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "2"))
MAX_TOTAL_FRESH_ARTICLES = int(os.getenv("MAX_TOTAL_FRESH_ARTICLES", "16"))
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


# Categories and High-Reliability Viral Indian RSS Feeds
CATEGORIES = {
    "rules-challan": {
        "name": "Challan & RTO Alerts",
        "slug": "rules-challan",
        "color": "#dc2626",
        "gradient": "linear-gradient(135deg, #dc2626, #f97316)",
        "icon": "🚨",
        "description": "New traffic challans, Motor Vehicles Act fines, speed cameras, HSRP number plates, tinted glass rules, and RTO updates.",
        "feeds": [
            "https://www.cartoq.com/feed/",
            "https://timesofindia.indiatimes.com/rssfeeds/74317216.cms",
            "https://www.rushlane.com/feed"
        ],
        "default_image": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1600&h=900&fit=crop"
    },
    "car-hacks": {
        "name": "Car Hacks & Secrets",
        "slug": "car-hacks",
        "color": "#8b5cf6",
        "gradient": "linear-gradient(135deg, #8b5cf6, #3b82f6)",
        "icon": "💡",
        "description": "Hidden dashboard features, AC defogging hacks, real mileage boost tricks, DIY car maintenance, and secrets dealerships hide.",
        "feeds": [
            "https://www.cartoq.com/feed/",
            "https://timesofindia.indiatimes.com/rssfeeds/74317216.cms",
            "https://www.carblogindia.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1600&h=900&fit=crop"
    },
    "suvs-comparisons": {
        "name": "SUV Wars & Real Mileage",
        "slug": "suvs-comparisons",
        "color": "#ea580c",
        "gradient": "linear-gradient(135deg, #ea580c, #f59e0b)",
        "icon": "🚙",
        "description": "Mahindra Thar Roxx, Scorpio-N, Tata Nexon, Safari, Curvv, Creta, Brezza, real-world city mileage, and head-to-head SUV shootouts.",
        "feeds": [
            "https://www.rushlane.com/feed",
            "https://www.motorbeam.com/feed/",
            "https://gaadiwaadi.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1600&h=900&fit=crop"
    },
    "discounts-offers": {
        "name": "Discounts & Waiting Periods",
        "slug": "discounts-offers",
        "color": "#10b981",
        "gradient": "linear-gradient(135deg, #10b981, #06b6d4)",
        "icon": "🏷️",
        "description": "Year-end cash discounts, exchange bonuses, dealer inventory clearances, and realistic waiting periods for popular cars in India.",
        "feeds": [
            "https://gaadiwaadi.com/feed/",
            "https://www.carblogindia.com/feed/",
            "https://www.rushlane.com/feed"
        ],
        "default_image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1600&h=900&fit=crop"
    },
    "spied-upcoming": {
        "name": "Leaked Spyshots & Launches",
        "slug": "spied-upcoming",
        "color": "#ec4899",
        "gradient": "linear-gradient(135deg, #ec4899, #f43f5e)",
        "icon": "📸",
        "description": "Leaked spy photos, camouflaged test mules, 2026-2027 facelifts, interior leaks, and upcoming car launches in India.",
        "feeds": [
            "https://www.carblogindia.com/feed/",
            "https://www.rushlane.com/feed",
            "https://www.motorbeam.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1600&h=900&fit=crop"
    },
    "safety-crashes": {
        "name": "Crash Safety & Build Quality",
        "slug": "safety-crashes",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b, #ef4444)",
        "icon": "🛡️",
        "description": "Bharat NCAP safety star ratings, crash test analysis, real-world highway accident survival, and build quality comparisons.",
        "feeds": [
            "https://www.cartoq.com/feed/",
            "https://www.motorbeam.com/feed/",
            "https://www.carblogindia.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1600&h=900&fit=crop"
    },
    "ev-reality": {
        "name": "EV Range & Hybrid Reality",
        "slug": "ev-reality",
        "color": "#06b6d4",
        "gradient": "linear-gradient(135deg, #06b6d4, #3b82f6)",
        "icon": "⚡",
        "description": "Real highway range vs ARAI claims, electric car battery replacement costs, home charging truths, and hybrid vs EV ownership math in India.",
        "feeds": [
            "https://www.cartoq.com/feed/",
            "https://www.motorbeam.com/feed/",
            "https://gaadiwaadi.com/feed/"
        ],
        "default_image": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1600&h=900&fit=crop"
    }
}

# Curated High-Definition Story Background Images per category for AMP slide sequencing (1080x1920)
SLIDE_IMAGE_COLLECTIONS = {
    "rules-challan": [
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "car-hacks": [
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "suvs-comparisons": [
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "discounts-offers": [
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "spied-upcoming": [
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "safety-crashes": [
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop"
    ],
    "ev-reality": [
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=1080&h=1920&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop"
    ]
}
