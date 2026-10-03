"""
NewsPulse - AI & Heuristic Summarization Engine
Generates 60-word factual news summaries, punchy headlines, and 5-slide AMP Web Stories.
Powered by Gemini 3.8 Flash (google-genai SDK) with a zero-failure rule-based NLP fallback.
"""

import os
import re
import sys
import json
from bs4 import BeautifulSoup
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def clean_headline(title: str) -> str:
    """Cleans clickbait, source tags, and trailing punctuation."""
    cleaned = re.sub(r"\s+[-–|]\s+[A-Za-z0-9\s.&]+$", "", title)
    cleaned = re.sub(r"^\[.*?\]\s*", "", cleaned)
    cleaned = re.sub(r"^(BREAKING|ALERT|WATCH|EXCLUSIVE):\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip("\"' \t\n\r")
    return cleaned


def rule_based_summarize(title: str, text: str, max_words: int = 65) -> str:
    """Extracts a crisp, coherent, factual summary (~60 words) using rule-based scoring."""
    if not text or len(text.strip()) < 10:
        return f"{title}. Details are developing as official sources monitor the situation."

    # Split into candidate sentences
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip().split()) >= 4]

    if not sentences:
        words = text.split()[:max_words]
        return " ".join(words) + ("..." if len(text.split()) > max_words else "")

    selected = []
    total_words = 0

    for sent in sentences:
        w_count = len(sent.split())
        if total_words + w_count <= max_words + 15:
            selected.append(sent)
            total_words += w_count
            if total_words >= 45:
                break
        else:
            if not selected:
                # If even the first sentence is too long, trim it cleanly
                words = sent.split()[:max_words]
                selected.append(" ".join(words) + "...")
                total_words += len(words)
            break

    summary = " ".join(selected).strip()
    return summary


def rule_based_slides(article: dict) -> list:
    """Generates 5 structured, visual story slides from article details."""
    cat = article.get("category", "tech")
    images = config.SLIDE_IMAGE_COLLECTIONS.get(cat, config.SLIDE_IMAGE_COLLECTIONS["tech"])
    article_img = article.get("image_url") or images[0]

    title = article.get("title", article.get("raw_title", "Breaking News"))
    summary = article.get("summary", article.get("raw_summary", ""))

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", summary) if s.strip()]

    # Slide 1: Cover
    slide1_text = sentences[0] if sentences else "Major development unfolding across the industry."

    # Slide 2: The Core Event
    slide2_text = sentences[1] if len(sentences) > 1 else (sentences[0] if sentences else "Key stakeholders confirm major operational changes.")

    # Slide 3: The Context & Background
    slide3_text = sentences[2] if len(sentences) > 2 else "Market analysts highlight how this aligns with recent sector shifts and regulatory milestones."

    # Slide 4: Real-world Impact
    slide4_text = sentences[3] if len(sentences) > 3 else "Consumers and enterprise partners are assessing the immediate functional implications."

    # Slide 5: Looking Ahead
    slide5_text = f"Further updates expected as {article.get('source', 'reporters')} tracks developments and industry reception."

    slides = [
        {
            "slide_number": 1,
            "heading": title,
            "badge": article.get("category_name", "Breaking"),
            "text": slide1_text,
            "image": article_img,
            "alt": f"{title} cover image"
        },
        {
            "slide_number": 2,
            "heading": "The Core Development",
            "badge": "What Happened",
            "text": slide2_text,
            "image": images[1 % len(images)],
            "alt": "Core development visual"
        },
        {
            "slide_number": 3,
            "heading": "Context & Facts",
            "badge": "Key Background",
            "text": slide3_text,
            "image": images[2 % len(images)],
            "alt": "Context visual"
        },
        {
            "slide_number": 4,
            "heading": "Market & Industry Impact",
            "badge": "Why It Matters",
            "text": slide4_text,
            "image": images[3 % len(images)],
            "alt": "Impact visual"
        },
        {
            "slide_number": 5,
            "heading": "Looking Forward",
            "badge": "Key Takeaway",
            "text": slide5_text,
            "image": images[4 % len(images)],
            "alt": "Future outlook visual"
        }
    ]
    return slides


def process_with_gemini(article: dict, api_key: str) -> dict:
    """
    Uses Google GenAI SDK (gemini-3.8-flash) to rewrite the article into a punchy headline,
    a 60-word factual summary, and 5 structured slides.
    """
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""You are an elite news editor for NewsPulse (like Axios, Inshorts, and Bloomberg).
Analyze the following news item:
Category: {article.get('category_name')}
Source: {article.get('source')}
Original Title: {article.get('raw_title')}
Raw Content: {article.get('raw_summary')}

Generate a JSON response with:
1. "headline": A punchy, high-CTR, clickbait-free, factual headline (under 12 words).
2. "summary": A concise, factual, neutral summary in exactly 50-65 words (Inshorts style, answering who, what, why, and impact).
3. "bullet_points": An array of 3 key takeaways (each 10-15 words).
4. "slides": An array of exactly 5 slides for an AMP Web Story:
   - Slide 1: Cover hook (heading under 10 words, text under 20 words, badge "Breaking")
   - Slide 2: The Core Event (heading under 6 words, text under 25 words, badge "The Event")
   - Slide 3: Facts & Context (heading under 6 words, text under 25 words, badge "Context")
   - Slide 4: Real-World Impact (heading under 6 words, text under 25 words, badge "Impact")
   - Slide 5: The Takeaway (heading under 6 words, text under 20 words, badge "Outlook")

Output ONLY valid JSON without markdown fences.
"""
        response = None
        # Try interactions API first as per modern SDK standard
        if hasattr(client, "interactions") and hasattr(client.interactions, "create"):
            res = client.interactions.create(
                model=config.GEMINI_MODEL,
                input=prompt
            )
            raw_output = res.output_text or ""
        elif hasattr(client, "models") and hasattr(client.models, "generate_content"):
            res = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )
            raw_output = res.text or ""
        else:
            raise RuntimeError("Unsupported genai client structure")

        # Strip possible markdown codeblocks
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_output.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)

        headline = data.get("headline") or clean_headline(article.get("raw_title", ""))
        summary = data.get("summary") or rule_based_summarize(headline, article.get("raw_summary", ""))
        bullet_points = data.get("bullet_points") or []

        # Construct slides
        cat = article.get("category", "tech")
        images = config.SLIDE_IMAGE_COLLECTIONS.get(cat, config.SLIDE_IMAGE_COLLECTIONS["tech"])
        article_img = article.get("image_url") or images[0]

        raw_slides = data.get("slides") or []
        slides = []
        for i, s in enumerate(raw_slides[:5]):
            img = article_img if i == 0 else images[i % len(images)]
            slides.append({
                "slide_number": i + 1,
                "heading": s.get("heading", f"Slide {i+1}"),
                "badge": s.get("badge", article.get("category_name", "News")),
                "text": s.get("text", ""),
                "image": img,
                "alt": f"{headline} - part {i+1}"
            })

        if len(slides) < 5:
            slides = rule_based_slides(article)

        return {
            "title": headline,
            "summary": summary,
            "bullet_points": bullet_points,
            "slides": slides,
            "ai_generated": True
        }

    except Exception as e:
        print(f"    [!] Gemini API notice ({e}), applying intelligent rule-based engine...")
        return None


def enrich_article(article: dict) -> dict:
    """Enriches an article with polished headline, 60-word summary, and 5 story slides."""
    api_key = config.GEMINI_API_KEY.strip()
    result = None

    if api_key:
        result = process_with_gemini(article, api_key)

    if not result:
        # High quality rule-based NLP pipeline
        headline = clean_headline(article.get("raw_title", ""))
        summary = rule_based_summarize(headline, article.get("raw_summary", ""))
        slides = rule_based_slides({**article, "title": headline, "summary": summary})

        # Generate 3 bullets
        sents = [s for s in re.split(r"(?<=[.!?])\s+", summary) if len(s.split()) >= 4]
        bullet_points = sents[:3] if len(sents) >= 3 else [
            f"Factual reporting confirmed by {article.get('source', 'wire services')}.",
            "Global industry stakeholders are monitoring downstream implications.",
            "Full regulatory and community updates scheduled for upcoming briefing."
        ]

        result = {
            "title": headline,
            "summary": summary,
            "bullet_points": bullet_points,
            "slides": slides,
            "ai_generated": False
        }

    # Merge results into article dict
    article["title"] = result["title"]
    article["summary"] = result["summary"]
    article["bullet_points"] = result["bullet_points"]
    article["slides"] = result["slides"]
    article["ai_generated"] = result["ai_generated"]
    article["word_count"] = len(result["summary"].split())
    return article


def enrich_all_articles(articles: list) -> list:
    """Processes and enriches a list of articles."""
    print(f"[*] Processing {len(articles)} articles through summarization pipeline...")
    enriched = []
    for idx, art in enumerate(articles, 1):
        try:
            enhanced = enrich_article(art)
            enriched.append(enhanced)
            mode = "Gemini AI" if enhanced.get("ai_generated") else "Smart NLP"
            print(f"    [{idx}/{len(articles)}] [{mode}] {enhanced['title'][:45]}... ({enhanced['word_count']} words)")
        except Exception as e:
            print(f"    [!] Error enriching article {art.get('slug')}: {e}")
            enriched.append(art)
    print(f"[OK] Completed summarization & slide synthesis for {len(enriched)} articles.")
    return enriched


if __name__ == "__main__":
    sample = {
        "id": "test_1",
        "slug": "meta-muse-ai-wearables",
        "category": "tech",
        "category_name": "Tech",
        "category_color": "#06b6d4",
        "source": "TechCrunch",
        "raw_title": "Meta wants your next gadget to be Muse-infused",
        "raw_summary": "Meta has announced strategic updates regarding its next generation wearable devices. The initiative focuses on ambient intelligence and high efficiency sensors. Engineering teams across Silicon Valley are preparing developer kits. The company highlighted that lightweight form factors will redefine consumer experiences while preserving privacy standards.",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=800&fit=crop"
    }
    res = enrich_article(sample)
    print("Headline:", res["title"])
    print("Summary:", res["summary"])
    print("Slides Count:", len(res["slides"]))
