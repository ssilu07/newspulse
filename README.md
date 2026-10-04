# ⚡ NewsPulse

> **Modern, Automated, High-Performance News & Visual Web Stories Portal**  
> Powered by Python, Google Gemini 3.8 Flash, and 100% Valid Google AMP Web Stories.

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![AMP Validated](https://img.shields.io/badge/Google%20AMP-100%25%20PASS-green.svg)](https://amp.dev)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

---

## 🌟 Overview

**NewsPulse** is an automated digital news publishing portal designed for modern mobile-first readers. It transforms multi-source breaking news RSS feeds into:
1. **60-word factual, concise summaries** (Inshorts / Axios style).
2. **100% Valid Google AMP Web Stories** (5-slide immersive visual cards optimized for Google Discover & viral mobile engagement).
3. **High-CTR, clickbait-free headlines** synthesized via **Google Gemini 3.8 Flash** (with a zero-failure rule-based NLP fallback).
4. **AdSense & Google News Compliant Pages** required for publisher approval.

---

## ✨ Key Features

### 1. 🎨 Cinema-Grade Glassmorphic Frontend
- **Dark Cinema Aesthetic**: Deep navy-black tones (`#07090e`), subtle glow accents, and frosted glass cards (`backdrop-filter: blur(16px)`).
- **Responsive Dark/Light Mode**: Smooth transition switch with automatic local storage persistence.
- **Breaking News Marquee**: Real-time ticker with a live pulsing beacon.
- **CineStories Carousel**: Horizontal story bubble tray with animated gradient rings for one-tap visual story viewing.
- **Instant Search**: 0ms clientside keyword filtering without reloading.
- **Category Filtering**: Instant switching across *Tech*, *AI & Future*, *Business*, *World*, *Sports*, and *Entertainment*.
- **Quick Read Drawer / Modal**: Distraction-free reading view with 3 bullet takeaways, source links, and reading time.
- **🔊 Web Speech Audio Reader (TTS)**: Built-in voice player to listen to summaries on mobile or desktop.
- **★ Bookmarks & Saved Stories**: Bookmark favorites saved purely in `localStorage` without requiring a remote database.

### 2. ⚡ 100% Valid Google AMP Web Stories (`/stories/<slug>/`)
- Built strictly to the **Google AMP Story 1.0 Specification**.
- 5 structured, visual slides:
  - **Slide 1: Breaking Cover** (High-impact headline & hook).
  - **Slide 2: Core Development** (Factual summary of the event).
  - **Slide 3: Context & Background** (Historical data and statistics).
  - **Slide 4: Real-World Impact** (Industry & market implications).
  - **Slide 5: Key Takeaway & Full Coverage CTA** (Outbound links to original publisher and NewsPulse home).
- High-resolution editorial photography with fallback asset management.
- Validated via official `npx amphtml-validator` with **0 errors**.

### 3. 🧠 Dual AI & Rule-Based Summarization Engine
- **Primary AI**: Uses the official `google-genai` SDK with `gemini-3.8-flash`.
- **Zero-Failure Fallback**: If no API key is provided or quota is exhausted, an intelligent NLP engine performs sentence scoring, headline normalization, and slide structuring to ensure **100% uptime**.

### 4. ⚖️ Google News & AdSense Compliance Suite
Includes complete, legally reviewed policy pages:
- [`/about/`](/about/): Editorial mission, transparent AI disclosure, publisher masthead, and leadership.
- [`/editorial-policy/`](/editorial-policy/): Multi-source verification, fact-checking, anonymous source guidelines, and correction/retraction policy (mandatory for Google News approval).
- [`/privacy/`](/privacy/): Comprehensive Google AdSense DART cookies disclosure, GDPR, CCPA/CPRA, and cookie controls.
- [`/terms/`](/terms/): Terms of Service and **Fair Use Notice under 17 U.S.C. § 107** for news commentary and reporting.
- [`/contact/`](/contact/): Editorial desk, DMCA designated agent information, and inquiry form.

### 5. 🔍 SEO & Google Discover Optimization
- **`NewsArticle` JSON-LD Schema**: Full structured data on all pages (headline, dates, publisher logo, author).
- **Google News XML Sitemap**: Automated `sitemap.xml` with `<news:news>`, `<news:publication>`, `<news:publication_date>`, and `<image:image>` extensions.
- **Dynamic `robots.txt`** and OpenGraph/Twitter Cards for social previews.

---

## 📁 Project Architecture

```
minutesNews/
├── config.py                 # Site branding, categories, feeds, and AI configuration
├── fetcher.py                # Multi-source RSS feed ingestion & deduplication
├── summarizer.py             # Gemini 3.8 Flash AI & rule-based summarization engine
├── story_generator.py        # 100% valid Google AMP Story generator
├── site_generator.py         # Static site compiler (Homepage, Compliance, Sitemap, Manifest)
├── fetch_and_generate.py     # Single-command CLI publishing pipeline
├── validate_amp.py           # Automated AMP compliance validator (Python + npx CLI)
├── app.py                    # FastAPI server for local preview & REST APIs
├── static/
│   ├── css/style.css         # Glassmorphic responsive dark/light cinema design system
│   ├── js/main.js            # Instant search, category filters, TTS reader, bookmarks
│   └── assets/               # Glowing SVG logos & icons
├── dist/                     # Production static build output (Vercel / Cloudflare ready)
├── vercel.json               # Vercel deployment configuration
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/newspulse.git
cd newspulse

# Install Python requirements
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your free Gemini API key from [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=your_gemini_api_key_here
SITE_NAME=NewsPulse
SITE_URL=https://your-domain.vercel.app
```
*(If `GEMINI_API_KEY` is omitted, NewsPulse automatically uses its smart rule-based engine!)*

### 3. Run the Publishing Pipeline
Run the single-command runner to fetch breaking news, synthesize summaries & AMP stories, and generate the static site:
```bash
python fetch_and_generate.py
```

### 4. Start Local Development Server
```bash
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 🧪 Validating AMP Compliance

To test all generated stories against the official Google AMP Validator:
```bash
python validate_amp.py
```
Output:
```
[*] Validating 12 AMP Stories...
    [PASS] story-slug-1 -> 100% Valid Google AMP Story (PASS)
    [PASS] story-slug-2 -> 100% Valid Google AMP Story (PASS)
[OK] ALL 12 AMP Stories PASSED 100% Google AMP Validation!
```

---

## ☁️ Deployment

### Deploy to Vercel (1-Click)
1. Push your repository to GitHub.
2. Import the project into **[Vercel](https://vercel.com/)**.
3. In Project Settings:
   - **Framework Preset**: `Other`
   - **Build Command**: `python fetch_and_generate.py --count 3 --skip-val`
   - **Output Directory**: `dist`
4. Add Environment Variables:
   - `GEMINI_API_KEY`: *(Optional)* Your Gemini API Key
   - `SITE_URL`: Your Vercel production URL (e.g. `https://newspulse.vercel.app`)
5. Click **Deploy**!

### Deploy to Cloudflare Pages
- **Build command**: `python fetch_and_generate.py --count 3 --skip-val`
- **Build output directory**: `dist`

### Automated Scheduled Publishing
A ready-to-use GitHub Actions workflow is included in `.github/workflows/scheduled_publish.yml`. It runs automatically every 4 hours to pull breaking news and push fresh stories to your live site!

---

## 📄 License & Attribution
- Published under the **MIT License**.
- News content summarized under **Fair Use 17 U.S.C. § 107** for transformative commentary and news reporting. All original sources are attributed.
