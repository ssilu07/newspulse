"""
Tumblr OAuth 1.0a 1-Click Authenticator & Setup Helper
Helps you connect News Seconds to your Tumblr blog in under 60 seconds.
"""

import os
import sys
import re
import urllib.parse
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

def update_env_file(key: str, value: str):
    """Safely updates or appends key-value pair in .env file."""
    if not ENV_FILE.exists():
        ENV_FILE.write_text(f"{key}={value}\n", encoding="utf-8")
        return

    content = ENV_FILE.read_text(encoding="utf-8")
    pattern = rf"^{key}=.*$"
    
    if re.search(pattern, content, flags=re.MULTILINE):
        new_content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\n{key}={value}\n"
        
    ENV_FILE.write_text(new_content, encoding="utf-8")


def main():
    print("=" * 65)
    print("  🚀 TUMBLR AUTO-POSTER SETUP WIZARD")
    print("=" * 65)
    print("\n[Step 1] Register a Free Tumblr App:")
    print("  1. Open: https://www.tumblr.com/oauth/apps")
    print("  2. Click 'Register Application'")
    print("  3. Fill in:")
    print("     - Application Name: News Seconds Bot")
    print("     - Application Website: https://newsseconds.com")
    print("     - Default Callback URL: https://newsseconds.com (or http://localhost)")
    print("  4. Save and copy your 'OAuth Consumer Key' and 'Secret Key'.\n")

    consumer_key = os.getenv("TUMBLR_CONSUMER_KEY", "").strip()
    consumer_secret = os.getenv("TUMBLR_CONSUMER_SECRET", "").strip()

    if not consumer_key:
        consumer_key = input("Enter your Tumblr OAuth Consumer Key: ").strip()
    else:
        print(f"Found Consumer Key in .env: {consumer_key[:8]}...{consumer_key[-4:]}")
        change = input("Use this key? (Y/n): ").strip().lower()
        if change == "n":
            consumer_key = input("Enter your Tumblr OAuth Consumer Key: ").strip()

    if not consumer_secret:
        consumer_secret = input("Enter your Tumblr OAuth Secret Key: ").strip()
    else:
        print(f"Found Secret Key in .env: {consumer_secret[:4]}...****")
        change = input("Use this secret? (Y/n): ").strip().lower()
        if change == "n":
            consumer_secret = input("Enter your Tumblr OAuth Secret Key: ").strip()

    if not consumer_key or not consumer_secret:
        print("[!] Error: Consumer Key and Secret Key are required.")
        return

    update_env_file("TUMBLR_CONSUMER_KEY", consumer_key)
    update_env_file("TUMBLR_CONSUMER_SECRET", consumer_secret)

    try:
        from requests_oauthlib import OAuth1Session
    except ImportError:
        print("[!] Installing requests-oauthlib...")
        os.system(f"{sys.executable} -m pip install requests-oauthlib")
        from requests_oauthlib import OAuth1Session

    print("\n[Step 2] Requesting Authorization from Tumblr...")
    callback_uri = "https://newsseconds.com"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_uri)

    try:
        fetch_response = oauth.fetch_request_token("https://www.tumblr.com/oauth/request_token")
    except Exception as e:
        print(f"\n[!] Failed to get request token from Tumblr: {e}")
        print("Please double check your Consumer Key and Consumer Secret.")
        return

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")

    authorization_url = oauth.authorization_url("https://www.tumblr.com/oauth/authorize")
    print(f"\n👉 Opening authorization link in your web browser:\n   {authorization_url}\n")
    try:
        webbrowser.open(authorization_url)
    except Exception:
        pass

    print("Please click 'Allow' in your browser.")
    print("Tumblr will redirect you to your callback URL (e.g. https://newsseconds.com/?oauth_token=...&oauth_verifier=...)")
    redirect_input = input("\nPaste the full redirected URL (or just the oauth_verifier): ").strip()

    verifier = None
    if "oauth_verifier=" in redirect_input:
        parsed = urllib.parse.urlparse(redirect_input)
        params = urllib.parse.parse_qs(parsed.query)
        verifier = params.get("oauth_verifier", [None])[0]
    else:
        verifier = redirect_input

    if not verifier:
        print("[!] Error: Could not determine oauth_verifier.")
        return

    print("\n[Step 3] Exchanging verifier for permanent Access Token...")
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )

    try:
        tokens = oauth.fetch_access_token("https://www.tumblr.com/oauth/access_token")
    except Exception as e:
        print(f"[!] Token exchange failed: {e}")
        return

    oauth_token = tokens.get("oauth_token")
    oauth_token_secret = tokens.get("oauth_token_secret")

    print("[OK] Access tokens generated successfully!")
    update_env_file("TUMBLR_OAUTH_TOKEN", oauth_token)
    update_env_file("TUMBLR_OAUTH_SECRET", oauth_token_secret)

    print("\n[Step 4] Fetching your Tumblr Blog Name...")
    user_info_resp = oauth.get("https://api.tumblr.com/v2/user/info")
    blog_name = ""
    if user_info_resp.status_code == 200:
        data = user_info_resp.json()
        blogs = data.get("response", {}).get("user", {}).get("blogs", [])
        if blogs:
            print(f"Found {len(blogs)} blog(s) linked to this account:")
            for idx, b in enumerate(blogs, 1):
                is_primary = " (Primary)" if b.get("primary") else ""
                print(f"  [{idx}] {b.get('name')} - {b.get('url')}{is_primary}")
            
            if len(blogs) == 1:
                blog_name = blogs[0].get("name")
            else:
                choice = input(f"Choose blog number [1-{len(blogs)}] (Default: 1): ").strip()
                try:
                    idx = int(choice) - 1 if choice else 0
                    blog_name = blogs[idx].get("name")
                except Exception:
                    blog_name = blogs[0].get("name")
    
    if not blog_name:
        blog_name = input("Enter your Tumblr blog name (e.g. mynewsblog or mynewsblog.tumblr.com): ").strip()

    # Clean blog name
    blog_name = re.sub(r"^https?://", "", blog_name).rstrip("/")
    update_env_file("TUMBLR_BLOG_NAME", blog_name)
    update_env_file("ENABLE_TUMBLR_POSTING", "true")

    print("\n" + "=" * 65)
    print("  🎉 TUMBLR SETUP COMPLETE!")
    print(f"  Target Blog: {blog_name}")
    print("  Configuration saved to .env")
    print("=" * 65)

    test_choice = input("\nWould you like to send a test post right now? (y/N): ").strip().lower()
    if test_choice == "y":
        print("\nSending test article to Tumblr...")
        import config
        # Reload config module
        import importlib
        importlib.reload(config)
        import social_poster
        importlib.reload(social_poster)

        test_article = {
            "title": "Welcome to News Seconds - Real-Time AI News & Visual Stories",
            "summary": "News Seconds delivers concise, verified 60-word news summaries and immersive visual AMP Web Stories across tech, world news, business, and entertainment.",
            "bullet_points": [
                "Bite-sized verified 60-word news updates",
                "Visual AMP Web Stories designed for mobile speed",
                "Automated real-time syndication engine"
            ],
            "slug": "welcome-to-news-seconds",
            "category": "trending",
            "source": "News Seconds",
            "original_url": "https://newsseconds.com",
            "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1600&h=900&fit=crop"
        }
        res = social_poster.post_to_tumblr(test_article)
        if res:
            print("\n✨ Test post successfully published on your Tumblr blog!")
        else:
            print("\n[!] Test post failed. Please check the logs above.")


if __name__ == "__main__":
    main()
