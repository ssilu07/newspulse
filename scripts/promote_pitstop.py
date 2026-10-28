"""
Promotion Generator & Syndication for NewsSeconds "Pit Stop Lab"
Generates viral, high-CTR copy for X/Twitter, Reddit, Telegram, Threads & LinkedIn.
Can broadcast directly to configured channels or export ready-to-use posts.
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config

PITSTOP_URL = f"{config.SITE_URL}/#interactiveGarage"

TEMPLATES = {
    "twitter": [
        {
            "hook": "🏎️ The Ultimate 1/4-Mile EV vs Gas Showdown",
            "text": (
                "Tesla Model S Plaid (1,020 HP) vs Porsche 911 Turbo S (640 HP) — who actually takes the quarter-mile trap speed?\n\n"
                "We just launched the 1/4-Mile Drag Simulator on NewsSeconds with real test-track telemetry & live Christmas tree countdown lights.\n\n"
                f"Pick your contender & launch here: {PITSTOP_URL}\n\n"
                "#Tesla #Porsche #Supercars #DragRace #ElectricVehicles"
            )
        },
        {
            "hook": "⚡ Is an EV actually cheaper for your daily commute?",
            "text": (
                "Gas prices are volatile. Calculate your EXACT monthly & 5-year fuel savings based on your real daily driving distance and local electricity rates.\n\n"
                "Interactive EPA-benchmarked EV calculator live on NewsSeconds:\n"
                f"{PITSTOP_URL}\n\n"
                "#EV #Tesla #CleanEnergy #CarTech #PersonalFinance"
            )
        },
        {
            "hook": "🔥 1,914 HP Rimac Nevera vs 1,234 HP Lucid Sapphire",
            "text": (
                "Can anything touch the Rimac Nevera's 8.25s quarter-mile? Put it head-to-head against the Ferrari SF90, Lambo Revuelto, or Dodge Demon 170.\n\n"
                f"Test your dream matchups on the Pit Stop Drag Simulator: {PITSTOP_URL}\n\n"
                "#Rimac #Ferrari #Lamborghini #Hypercar"
            )
        }
    ],
    "reddit": [
        {
            "title": "Built an interactive 1/4-mile drag race simulator & EV savings calculator using real EPA & test telemetry",
            "subreddit": "r/cars / r/electricvehicles",
            "text": (
                "Hey everyone,\n\n"
                "I built an interactive web simulator comparing 1/4-mile times, 0-60, and trap speeds between modern supercars and performance EVs "
                "(Tesla Plaid, Porsche 911 Turbo S, Lucid Sapphire, Ferrari SF90, Rimac Nevera, Corvette Z06, etc.) with NHRA-style Christmas tree staging lights.\n\n"
                "It also includes an interactive EV vs Gas fuel savings calculator that factors in daily commute distance, gas price/gal, and home Level 2 charging rates.\n\n"
                f"It's 100% free with zero downloads: {PITSTOP_URL}\n\n"
                "Would love your feedback on additional cars or telemetry metrics to add next!"
            )
        }
    ],
    "telegram": [
        {
            "text": (
                "🏎️ <b>THE PIT STOP LAB IS NOW LIVE!</b> ⚡\n\n"
                "Test your favorite supercars in head-to-head 1/4-mile drag battles or calculate your real-world EV fuel savings:\n\n"
                "🏁 <b>1/4-Mile Drag Simulator:</b>\n"
                "• Tesla Plaid vs Porsche 911 Turbo S\n"
                "• Rimac Nevera vs Ferrari SF90 Stradale\n"
                "• Live Christmas tree countdown & telemetry HUD\n\n"
                "🔋 <b>EV Fuel Savings Calculator:</b>\n"
                "• Instant monthly & 5-year fuel savings estimate\n"
                "• EPA efficiency benchmarks & charging time\n\n"
                f"👉 <b>Experience It Here:</b> <a href=\"{PITSTOP_URL}\">newsseconds.com/pitstop</a>"
            )
        }
    ],
    "threads_instagram": [
        {
            "caption": (
                "Who takes the crown in a 1/4-mile drag? 🏎️💨\n\n"
                "1️⃣ Tesla Model S Plaid (1,020 HP)\n"
                "2️⃣ Porsche 911 Turbo S (640 HP)\n"
                "3️⃣ Lucid Air Sapphire (1,234 HP)\n"
                "4️⃣ Ferrari SF90 Stradale (986 HP)\n\n"
                "We just launched the interactive 1/4-Mile Drag Strip Simulator on NewsSeconds! Pick any two cars, hit Launch Control, and see live telemetry + winner celebration.\n\n"
                f"Tap the link to race: {PITSTOP_URL}\n\n"
                "#supercars #dragrace #teslaplaid #porsche911 #carswithoutlimits #hypercar #ev"
            )
        }
    ]
}

def post_to_telegram(message_text: str) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("[!] Telegram credentials not found in env.")
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[!] Error posting to Telegram: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 NewsSeconds - 'Pit Stop Lab' Viral Promotion Templates")
    print(f"Target URL: {PITSTOP_URL}")
    print("=" * 60)

    if "--telegram" in sys.argv:
        print("[*] Broadcasting to Telegram Channel...")
        success = post_to_telegram(TEMPLATES["telegram"][0]["text"])
        if success:
            print("[OK] Successfully posted to Telegram!")
        return

    print("\n[1] 🐦 TWITTER / X POST TEMPLATES:")
    for i, t in enumerate(TEMPLATES["twitter"], 1):
        print(f"\n--- Option {i}: {t['hook']} ---")
        print(t["text"])

    print("\n" + "=" * 60)
    print("[2] 💬 REDDIT COMMUNITY TEMPLATE (r/cars, r/electricvehicles):")
    r = TEMPLATES["reddit"][0]
    print(f"Title: {r['title']}\n")
    print(r["text"])

    print("\n" + "=" * 60)
    print("[3] ✈️ TELEGRAM CHANNEL BROADCAST:")
    print(TEMPLATES["telegram"][0]["text"])

    print("\n" + "=" * 60)
    print("[4] 📸 INSTAGRAM / THREADS CAPTION:")
    print(TEMPLATES["threads_instagram"][0]["caption"])

if __name__ == "__main__":
    main()
