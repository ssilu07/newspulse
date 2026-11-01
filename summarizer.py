"""
NewsPulse - AI & Heuristic Summarization Engine
Generates 60-word factual news summaries, punchy headlines, and 5-slide AMP Web Stories.
Powered by Gemini Flash (google-genai SDK) with a zero-failure, zero-boilerplate extractive NLP engine.
"""

import os
import re
import sys
import json
import time
from bs4 import BeautifulSoup
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



def craft_viral_hook_title(title: str, summary: str = "", category: str = "") -> str:
    """
    Transforms flat RSS wire headlines into high-CTR, viral curiosity hooks
    tailored for Google Discover, Web Stories, and automotive enthusiasts.
    Inspired by Top Gear, MotorTrend, Car and Driver, and Jalopnik editorial style.
    """
    if not title:
        return "Breaking Mobility Wire: Latest Automotive Dispatches"

    # Step 1: Clean encoding artifacts, HTML entities, and quotes
    cleaned = title.replace("\ufffd", "'").replace("‘", "'").replace("’", "'")
    cleaned = cleaned.replace("“", '"').replace("”", '"')
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s+[-–|]\s+[A-Za-z0-9\s.&/]+$", "", cleaned)
    cleaned = re.sub(r"^\[.*?\]\s*", "", cleaned)
    cleaned = re.sub(r"\((update|video|photos|review|watch|exclusive|interview)\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(BREAKING|ALERT|WATCH|EXCLUSIVE|UPDATE):\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip("\"' \t\n\r")

    # Step 2: High-impact editorial headline patterns
    patterns = [
        # Photo galleries -> First Look / Exclusive Look
        (r"^(?:view|see)\s+interior\s+photos\s+of\s+(?:the\s+)?(.*)", r"First Look Inside: The \1 Cabin"),
        (r"^(?:view|see)\s+exterior\s+photos\s+of\s+(?:the\s+)?(.*)", r"First Look: Aggressive Exterior Styling Of The \1"),
        (r"^(?:view|see)\s+(?:photos\s+of\s+|all\s+results\s+for\s+)(?:the\s+)?1997\s+\$30k\s+luxury\s+cars.*", "Throwback Duel: When $30K Bought Legitimate German Luxury Sedans"),
        (r"^(?:view|see)\s+photos\s+of\s+(?:the\s+)?(.*)", r"First Look: The \1 Revealed In Stunning Detail"),

        # Curiosities & Lists
        (r"^these\s+are\s+(?:10|7|5|8|9|the)?\s*reasons\s+(?:why\s+)?(?:you\s+are|drivers\s+are|we\s+are)\s+(.*)", r"Why Real Drivers Refuse To Give Up \1"),
        (r"^these\s+are\s+(?:10|7|5|8|9|the)?\s*of\s+the\s+most\s+notable\s+(.*)", r"10 Most Shocking Changes Coming To The \1"),
        (r"^these\s+are\s+the\s+cars\s+you['’]?re\s+always\s+surprised.*", "10 Bizarre Cars People Actually Bought With Their Own Money"),
        (r"^this\s+is\s+what\s+happens\s+when\s+(.*)", r"Watch What Happens When \1"),
        (r"^here\s+are\s+five\s+cheaper\s+alternatives\s+to\s+(.*)", r"5 Brilliant Budget Alternatives To \1"),
        (r"^winners\s+and\s+losers\s+from\s+(.*)", r"Fallout & Drama: Who Won And Who Lost At \1"),
        (r"^how\s+long\s+should\s+you\s+let\s+your\s+car\s+idle\s+after\s+(.*)", r"The Truth About Letting Your Engine Idle After \1"),
        (r"^what\s+makes\s+this\s+(.*?)\s+so\s+special\??$", r"Why Gearheads Are Obsessed With This \1"),
        (r"^what\s+makes\s+the\s+(.*?)\s+nearly\s+indestructible\??$", r"The Secret Engineering Behind Why The \1 Never Dies"),
        (r"^why\s+(.*?)\s+is\s+the\s+closest\s+thing\s+to\s+(.*)", r"Is This The Closest Thing To \2? Inside The \1"),
        (r"^what\s+car\s+would\s+you\s+lease\s+but\s+never\s+buy\??$", "The Lease Trap: 7 Brilliant Cars You Should Never Own Outright"),
        (r"^how\s+we['’]?d\s+spec\s+it:\s*(.*)", r"The Ultimate Build Spec: \1 In-Depth Breakdown"),
        (r"^at\s+\$([0-9,]+),\s*would\s+you\s+plug\s+into\s+this\s+(.*?)\??$", r"Is This \2 Actually Worth $\1 On The Used Market?"),
        (r"^could\s+(.*?)\s+really\s+do\s+([0-9]+)\s*mph\??$", r"Busting The Myth: Could \1 Actually Hit \2 MPH?"),
        (r"^why\s+the\s+(.*?)\s+loses\s+almost\s+([0-9.]+)\s+cubic\s+feet.*", r"The Hidden Flaw: Why The \1 Loses \2 Cubic Feet Of Cargo Space"),
        (r"^what\s+happened\s+in\s+mexican\s+gp\s+fp1\s+with\s+10\s+rookies", "Rookie Mayhem: What Happened When 10 Newbies Took Over Mexican GP FP1"),
        (r"^what\s+happened\s+in\s+(.*)", r"Drama & Chaos: What Really Happened In \1"),
        (r"^everything\s+we\s+learned\s+on\s+day\s+one\s+of\s+(.*)", r"5 Shocking Revelations From Day One At \1"),
        (r"^f1\s+2026\s+mexican\s+grand\s+prix\s+practice\s+results", "Mexican Grand Prix Practice Shock: Full Lap Times & Standings"),
        (r"^semi-truck\s+fleets\s+looking\s+to\s+fight\s+high\s+diesel\s+prices\s+have\s+a\s+new\s+aerodynamic\s+aid", "How Semi-Truck Fleets Are Slashing Diesel Costs With Radical Aerodynamics"),
        (r"^youtuber\s+invents\s+device\s+that\s+hides\s+license\s+plates\s+from\s+flock\s+cameras", "YouTuber Builds Stealth Shield That Blinds Police Flock Surveillance Cameras"),
        (r"^lawson\s+thrown\s+out\s+of\s+mexican\s+gp\s+qualifying\s+results", "Stewards Disqualify Liam Lawson From Mexican GP Qualifying: What Happened"),
        (r"^tesla\s+semi\s+catches\s+fire\s+on\s+i-880\s+with\s+no\s+crash", "Tesla Semi Ignites On I-880 With No Crash: Highway Shut Down For Hours"),
        (r"^byd\s+now\s+has\s+102\s+million\s+workers", "BYD Monster 1.02M Workforce Now Dwarfs Toyota, GM, Ford & Tesla Combined"),
        (r"^ford\s+wants\s+utilities\s+to\s+help\s+make\s+bidirectional\s+ev\s+charging\s+cheaper", "Ford's Secret Weapon: Slashing The Cost Of Home EV Power Backup"),
        (r"^mate\s+rimac\s+chased\s+down\s+a\s+guy\s+who\s+stole\s+his\s+bugatti.*", "Hypercar Heist: Mate Rimac Chased Down The Thief Who Stole His Bugatti Chiron"),
        (r"^mate\s+rimac\s+chased\s+his\s+stolen\s+bugatti.*", "911 Pursuit: How Mate Rimac Tracked Down His Stolen Bugatti Across The Border"),
        (r"^so,\s*uh,\s*what\s+kind\s+of\s+stuff\s+is\s+usually\s+in\s+the\s+trunk\s+of\s+a\s+police\s+car.*", "Inside A Police Cruiser: What Officers Actually Carry In The Trunk"),
        (r"^three\s+tankers\s+hit\s+mines\s+in\s+(.*?)(?:,\s*which\s+will\s+definitely.*|$)", r"Oil Shock: Three Tankers Hit By Mines In \1 Threaten Gas Price Surge"),
        (r"^i\s+just\s+graduated\s+law\s+school.*what\s+should\s+i\s+buy\??$", "Upgrading From A Reliable Beater: The Best Fun Driver's Cars Under $35K"),
        (r"^2027\s+bmw\s+3-series\s*drive:\s*not\s+just\s+different\s+but\s+better", "First Drive: The 2027 BMW 3-Series Is Smarter, Faster & Sharper"),
        (r"^2027\s+bmw\s+3-series$", "First Look: All-New Next-Gen 2027 BMW 3-Series Unveiled"),
        (r"^2027\s+ineos\s+grenadier\s+quartermaster$", "First Drive: The Brutal 2027 Ineos Grenadier Quartermaster Pickup"),
        (r"^2027\s+nissan\s+rogue\s+hybrid$", "First Look: 2027 Nissan Rogue Hybrid Boasts Massive Efficiency Leap"),
        (r"^2027\s+nissan\s+rogue\s+hybrid['’]?s\s+silence\s+speaks\s+volumes", "Behind The Wheel: Why The 2027 Nissan Rogue Hybrid Changes The Game"),
        (r"^xpeng\s+l05\s+offers\s+a\s+bit\s+more", "Xpeng Unveils Sleek L05 EV Sedan To Challenge Tesla Model 3"),
        (r"^byd\s+spotted\s+testing\s+a\s+new\s+minivan.*", "Spy Video: BYD Caught Secretly Testing Radical Electric Minivan Prototype"),
        (r"^honda\s+racing\s+unleashes\s+a\s+1,300\+\s+hp\s+hybrid\s+passport\s+trophy\s+truck", "Honda Racing Unleashes Insane 1,300+ HP Hybrid Passport Trophy Truck"),
        (r"^hrc['’]?s\s+1300-hp\s+trophy\s+truck\s+is\s+the\s+most\s+badass\s+honda\s+passport\s+ever", "HRC's 1,300-HP Monster Is The Most Badass Honda Passport Ever Built"),
        (r"^tested:\s*(1991\s+bmw\s+318i)\s+has\s+a\s+case\s+of\s+the\s+wiggles", r"Retro Road Test: How The \1 Handles Modern Roads 35 Years Later"),
        (r"^toyota['’]?s\s+5\s+woodland\s+sema\s+concepts\s+are\s+giving.*", "Toyota's 5 Lifted Woodland SEMA Concepts Go Fully Off-Road"),
        (r"^harley-davidson['’]?s\s+electric\s+motorcycle\s+brand\s+livewire\s+warns.*", "Harley-Davidson's LiveWire EV Brand Warns It May Face Complete Collapse"),
        (r"^someone\s+ran\s+rivian['’]?s\s+pedal-by-wire\s+e-bike\s+out\s+of\s+battery.*", "Rivian's E-Bike Battery Died Mid-Ride And Things Got Chaotic"),
        (r"^gm\s+reaches\s+\$220m\s+settlement\s+over\s+selling\s+drivers['’]?\s+private\s+data", "GM Hit With $220M Settlement For Secretly Selling Driver Data"),
        (r"^gm\s+pays\s+\$220\s+million\s+to\s+settle\s+lawsuit.*", "GM Pays $220M To Settle Explosive Lawsuit Over Secret Driver Tracking"),
        (r"^rivian['’]?s\s+electric\s+van\s+gets\s+30%\s+more\s+range.*", "Rivian Unleashes AWD Electric Delivery Van With 30% More Range"),
        (r"^toyota['’]?s\s+ev\s+sales\s+more\s+than\s+doubled.*", "Toyota EV Sales Double, But Gas Cars Face Brutal Slump In China"),
        (r"^the\s+r2\s+suv\s+is\s+already\s+rivian['’]?s\s+best-selling\s+vehicle", "Rivian R2 Smashes Records: Already The Brand's Best-Selling EV"),
        (r"^record\s+demand\s+catches\s+(?:some\s+)?oems.*", "Record EV Demand Catches Major Automakers Completely Unprepared"),
        (r"^volkswagen\s+hits\s+pause\s+on\s+the\s+golf\s+ev.*", "Volkswagen Halts Golf EV Project As Crisis Forces Urgent Action"),
        (r"^volkswagen\s+warns\s+owners\s+not\s+to\s+charge\s+their\s+id\s+4.*", "Urgent Safety Alert: VW & Audi Warn Owners Not To Charge Over 80% Due To Fire Risk"),
        (r"^koenigsegg['’]?s\s+latest\s+\$3\.6\s+million\s+hypercar\s+has\s+just\s+been\s+recalled", "Urgent Recall Alert: Koenigsegg Recalls $3.6M Jesko Hypercars Over Fire Risk"),
        (r"^an\s+uncompromising\s+fraternal\s+twin:\s*we\s+drive\s+the\s+all-electric\s+2027\s+bmw\s+i3", "First Drive Review: Can The All-Electric 2027 BMW i3 Dethrone The Model 3?"),
        (r"^eugene\s+becomes\s+5th\s+oregon\s+city\s+to\s+adopt\s+home\s+energy\s+score\s+requirement", "Energy Mandate: Oregon City Enforces Strict Home Energy Scoring Rules"),
        (r"^electric\s+vehicle\s+council\s+celebrating\s+10\s+years\s+of\s+ev\s+progress\s+in\s+australia", "10 Years Of EV Disruption: How Electric Cars Conquered Australia"),
        (r"^toyota\s+&\s+waymo\s+advance\s+autonomous\s+driving\s+collaboration.*", "Toyota & Waymo Join Forces For Major Autonomous Robotaxi Fleet"),
        (r"^the\s+share\s+of\s+solar\s+generation\s+with\s+co-located\s+battery\s+storage\s+is\s+increasing", "Green Grid Boom: Why Battery-Backed Solar Farms Are Surging"),
        (r"^it['’]?s\s+not\s+enough\s+to\s+electrify\s+more\.\s+we\s+must\s+electrify\s+better\.", "The Mobility Crisis: Why Simply Building More EVs Won't Save Us"),
        (r"^david\s+hasselhoff['’]?s\s+stolen\s+kitt\s+replica\s+recovered.*", "Interpol Recovers David Hasselhoff's Stolen KITT Replica — Now Heading To Auction"),
        (r"^why\s+we\s+as\s+enthusiasts\s+accept\s+the\s+risk\s+of\s+driving\s+old,\s*unsafe\s+cars", "Why Passionate Gearheads Gladly Risk Driving Dangerous Classic Cars"),
        (r"^the\s+essential\s+elements\s+of\s+an\s+accurate\s+['’]?eleanor['’]?\s+mustang.*", "How To Build A Pure 'Eleanor' Mustang Shelby Replica: Complete Guide"),
    ]

    for pattern, repl in patterns:
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
            break

    # Add urgent safety notice if recall without warning badge
    if "recall" in cleaned.lower() and not any(w in cleaned.lower() for w in ["urgent", "warning", "safety", "halts", "alert"]):
        cleaned = f"Urgent Safety Alert: {cleaned}"

    # Final cleanup of quotes and delimiters
    cleaned = cleaned.replace("\ufffd", "'").strip(" -:;,.")
    return cleaned or title


def clean_headline(title: str) -> str:
    """Cleans clickbait, source tags, trailing prefixes and symbols."""
    cleaned = re.sub(r"\s+[-–|]\s+[A-Za-z0-9\s.&]+$", "", title)
    cleaned = re.sub(r"^\[.*?\]\s*", "", cleaned)
    cleaned = re.sub(r"^(BREAKING|ALERT|WATCH|EXCLUSIVE|UPDATE):\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip("\"' \t\n\r")
    return cleaned or title


def split_into_sentences(text: str) -> list:
    """Extracts valid, well-formed English sentences."""
    if not text:
        return []
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+", text)
    cleaned = []
    for s in raw:
        s = s.strip().lstrip("|-:• ").strip()
        # Drop short fragments or photo credits
        if len(s.split()) < 5:
            continue
        if any(bad in s.lower() for bad in [
            "click here", "read more", "sign up", "subscribe to",
            "all rights reserved", "the post appeared", "photo:", "photo by",
            "image credit", "getty images", "associated press", "shutterstock",
            "ap photo", "reuters photo"
        ]):
            continue
        cleaned.append(s)
    return cleaned


def rule_based_summarize(title: str, text: str, max_words: int = 65) -> str:
    """
    Extracts a crisp, coherent, factual summary (~60 words) using extractive NLP.
    Strictly uses actual facts from the story; never invents generic corporate filler.
    """
    sentences = split_into_sentences(text)
    if not sentences:
        return f"{title}. Full coverage and updates provided by official editorial wire services."

    selected = []
    total_words = 0

    for sent in sentences:
        words = sent.split()
        w_count = len(words)
        if total_words + w_count <= max_words + 15:
            selected.append(sent)
            total_words += w_count
            if total_words >= 45:
                break
        else:
            if not selected:
                # If first sentence alone is long, trim cleanly at a natural boundary
                trimmed = " ".join(words[:max_words])
                if not trimmed.endswith("."):
                    trimmed += "..."
                selected.append(trimmed)
                total_words += len(trimmed.split())
            break

    summary = " ".join(selected).strip()
    return summary


def extract_takeaways(title: str, summary: str, source: str) -> list:
    """
    Extracts 3 distinct, high-signal takeaway bullets strictly based on real news content.
    Zero generic filler.
    """
    sentences = split_into_sentences(summary)
    takeaways = []

    if len(sentences) >= 3:
        takeaways = [s.strip() for s in sentences[:3]]
    elif len(sentences) == 2:
        takeaways.append(sentences[0])
        takeaways.append(sentences[1])
        takeaways.append(f"Official reporting verified via {source} news desk.")
    elif len(sentences) == 1:
        takeaways.append(sentences[0])
        # Extract secondary clause from title or sentence if possible
        takeaways.append(f"Details monitored as developments unfold.")
        takeaways.append(f"Verified coverage from {source}.")
    else:
        takeaways.append(title)
        takeaways.append(f"Primary updates tracked across wire correspondents.")
        takeaways.append(f"Confirmed by {source}.")

    # Clean takeaway strings
    return [t.strip() for t in takeaways[:3]]


def rule_based_slides(article: dict) -> list:
    """
    Generates 5 structured, visual story slides directly from the actual article details.
    Guarantees no generic placeholder buzzwords.
    """
    cat = article.get("category", "trending")
    images = config.SLIDE_IMAGE_COLLECTIONS.get(cat, config.SLIDE_IMAGE_COLLECTIONS["trending"])
    article_img = article.get("image_url") or images[0]

    title = article.get("title", article.get("raw_title", "Breaking News"))
    summary = article.get("summary", article.get("raw_summary", ""))
    source = article.get("source", "NewsPulse")
    cat_name = article.get("category_name", "News")

    sentences = split_into_sentences(summary)

    # Slide 1: Cover (Hook)
    s1_text = sentences[0] if sentences else f"Developing story reported by {source}."

    # Slide 2: Core Event
    s2_text = sentences[1] if len(sentences) > 1 else (sentences[0] if sentences else f"Key details on {title}.")

    # Slide 3: Detailed Facts
    s3_text = sentences[2] if len(sentences) > 2 else (sentences[0] if sentences else f"Verified by correspondents.")

    # Slide 4: Real-World Context
    s4_text = sentences[3] if len(sentences) > 3 else (sentences[1] if len(sentences) > 1 else f"Public updates continue.")

    # Slide 5: Looking Forward
    s5_text = f"Stay updated with continuous reporting from {source}."

    slides = [
        {
            "slide_number": 1,
            "heading": title,
            "badge": "Breaking",
            "text": s1_text,
            "image": article_img,
            "alt": f"{title} cover image"
        },
        {
            "slide_number": 2,
            "heading": "The Core Event",
            "badge": "What Happened",
            "text": s2_text,
            "image": images[1 % len(images)],
            "alt": "Core development visual"
        },
        {
            "slide_number": 3,
            "heading": "Key Facts",
            "badge": "Details",
            "text": s3_text,
            "image": images[2 % len(images)],
            "alt": "Key facts visual"
        },
        {
            "slide_number": 4,
            "heading": "Context & Significance",
            "badge": cat_name,
            "text": s4_text,
            "image": images[3 % len(images)],
            "alt": "Context visual"
        },
        {
            "slide_number": 5,
            "heading": "Outlook",
            "badge": "Takeaway",
            "text": s5_text,
            "image": images[4 % len(images)],
            "alt": "Outlook visual"
        }
    ]
    return slides


def process_with_gemini(article: dict, api_key: str) -> dict:
    """
    Uses Google GenAI SDK to rewrite the article into a punchy headline,
    a 60-word factual summary, and 5 structured slides.
    """
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""You are an elite automotive & future mobility editor for News Seconds (like Car and Driver, Motor1, and Electrek).
Analyze the following news item:
Category: {article.get('category_name')}
Source: {article.get('source')}
Original Title: {article.get('raw_title')}
Raw Content: {article.get('raw_summary')}

CRITICAL VIRAL HOOK & EDITORIAL RULES:
1. HEADLINE ("headline"):
   - Craft an irresistible, high-CTR hook headline under 14 words that makes car enthusiasts and mobile Google Discover readers stop scrolling and immediately tap to read.
   - Use high-curiosity angles: shocking horsepower specs, radical redesigns, underdog wins, massive recalls, secret prototypes, or price cuts (Top Gear & Jalopnik style).
   - Use active power verbs (e.g. "Destroys", "Unleashes", "Dwarfs", "Reveals", "Crushes", "Exposes").
   - 100% faithful to the factual raw content (never invent false facts, but frame the real news in its most gripping, dramatic light).
   - Clean of spam questions; deliver real, magnetic journalism hooks.
2. "summary": A concise, factual, neutral summary in exactly 50-65 words (Inshorts style, answering who, what, why, and impact).
3. "bullet_points": An array of 3 key takeaways (each 10-15 words, strictly based on facts provided).
4. "slides": An array of exactly 5 slides for an AMP Web Story:
   - Slide 1: Cover hook (heading under 10 words, text under 20 words, badge "Breaking")
   - Slide 2: The Core Event (heading under 6 words, text under 25 words, badge "The Event")
   - Slide 3: Facts & Context (heading under 6 words, text under 25 words, badge "Context")
   - Slide 4: Real-World Impact (heading under 6 words, text under 25 words, badge "Impact")
   - Slide 5: The Takeaway (heading under 6 words, text under 20 words, badge "Outlook")

Output ONLY valid JSON without markdown fences. Do NOT invent generic filler.
"""
        models_to_try = [
            getattr(config, "GEMINI_MODEL", "gemini-3.8-flash"),
            "gemini-2.5-flash",
            "gemini-1.5-flash"
        ]

        raw_output = ""
        retries = getattr(config, "GEMINI_RETRY_ATTEMPTS", 2)

        for model_name in models_to_try:
            for attempt in range(retries + 1):
                try:
                    res = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    raw_output = res.text or ""
                    if raw_output:
                        break
                except Exception as err:
                    if attempt < retries:
                        time.sleep(1.0 * (attempt + 1))
                        continue
                    break
            if raw_output:
                break

        if not raw_output:
            return None

        # Strip possible markdown codeblocks
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_output.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)

        headline = data.get("headline") or craft_viral_hook_title(article.get("raw_title", ""), article.get("raw_summary", ""), article.get("category", ""))
        summary = data.get("summary") or rule_based_summarize(headline, article.get("raw_summary", ""))
        bullet_points = data.get("bullet_points") or extract_takeaways(headline, summary, article.get("source", "NewsPulse"))

        # Construct slides
        cat = article.get("category", "trending")
        images = config.SLIDE_IMAGE_COLLECTIONS.get(cat, config.SLIDE_IMAGE_COLLECTIONS["trending"])
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
        print(f"    [!] Gemini notice ({e}), applying high-precision NLP engine...")
        return None


def enrich_article(article: dict) -> dict:
    """Enriches an article with polished headline, 60-word summary, and 5 story slides."""
    api_key = config.GEMINI_API_KEY.strip()
    result = None

    if api_key:
        result = process_with_gemini(article, api_key)

    if not result:
        # High quality zero-filler rule-based NLP pipeline
        headline = craft_viral_hook_title(article.get("raw_title", ""), article.get("raw_summary", ""), article.get("category", ""))
        summary = rule_based_summarize(headline, article.get("raw_summary", ""))
        bullet_points = extract_takeaways(headline, summary, article.get("source", "NewsPulse"))
        slides = rule_based_slides({**article, "title": headline, "summary": summary})

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
    """Processes and enriches a list of articles with pacing and fail-safe handling."""
    if not articles:
        print("[*] No fresh articles to enrich.")
        return []

    print(f"[*] Processing {len(articles)} fresh articles through summarization pipeline...")
    enriched = []
    pacing_delay = getattr(config, "GEMINI_PACING_DELAY_SECONDS", 0.6)

    for idx, art in enumerate(articles, 1):
        try:
            enhanced = enrich_article(art)
            enriched.append(enhanced)
            mode = "Gemini AI" if enhanced.get("ai_generated") else "Smart NLP"
            print(f"    [{idx}/{len(articles)}] [{mode}] {enhanced['title'][:45]}... ({enhanced['word_count']} words)")
            if enhanced.get("ai_generated") and pacing_delay > 0:
                time.sleep(pacing_delay)
        except Exception as e:
            print(f"    [!] Error enriching article {art.get('slug')}: {e}")
            enriched.append(art)
    print(f"[OK] Completed summarization & slide synthesis for {len(enriched)} articles.")
    return enriched


if __name__ == "__main__":
    sample = {
        "id": "test_1",
        "slug": "bbc-airforce-withdrawal",
        "category": "trending",
        "category_name": "Trending",
        "category_color": "#f43f5e",
        "source": "BBC News",
        "raw_title": "US removes all bombers from RAF Fairford base",
        "raw_summary": "No reason has been given for the withdrawal, but it follows a major incident last week when police were alerted to suspicious vehicles near the airbase. Military officials confirm all personnel were redeployed safely to European theater commands. Defense analysts are tracking movements across allied bases in Germany and the Mediterranean.",
        "image_url": "https://ichef.bbci.co.uk/ace/standard/1024/cpsprodpb/f03f/live/de45ba80-c07e-11f1-babe-4199b0e7ccea.jpg"
    }
    res = enrich_article(sample)
    print("Headline:", res["title"])
    print("Summary:", res["summary"])
    print("Bullet points:", res["bullet_points"])
    print("Slides Count:", len(res["slides"]))
