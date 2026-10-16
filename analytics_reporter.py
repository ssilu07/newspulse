"""
NewsPulse / News Seconds - Google Analytics 4 (GA4) Automated Reporter
Fetches realtime, traffic overview, top news stories, and traffic sources
directly from Google Analytics using the GA4 Data API (v1beta).
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_credentials_path() -> Optional[Path]:
    """Finds the Google Cloud service account credentials JSON file."""
    # 1. Check explicit environment variable or config
    explicit_path = getattr(config, "GA_CREDENTIALS_FILE", "ga_credentials.json")
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_absolute():
            p = config.BASE_DIR / p
        if p.exists():
            return p

    # 2. Check GOOGLE_APPLICATION_CREDENTIALS
    env_gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_gac and Path(env_gac).exists():
        return Path(env_gac)

    # 3. Check default candidate names in project root
    for candidate in ["ga_credentials.json", "service_account.json", "credentials.json"]:
        cand_path = config.BASE_DIR / candidate
        if cand_path.exists():
            return cand_path

    return None


def get_client():
    """Initializes and returns BetaAnalyticsDataClient."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    cred_path = get_credentials_path()
    if not cred_path:
        raise FileNotFoundError(
            f"Google Analytics credentials file not found!\n"
            f"Expected file at: {config.BASE_DIR / 'ga_credentials.json'}\n\n"
            f"--- KAISE SETUP KAREIN (3 Aasan Steps) ---\n"
            f"1. Google Cloud Console (https://console.cloud.google.com) me jayein aur 'Google Analytics Data API' enable karein.\n"
            f"2. IAM & Admin > Service Accounts me jakar ek Service Account banayein aur 'Keys' tab se JSON key download karein.\n"
            f"3. Uss JSON file ko project folder me 'ga_credentials.json' naam se save karein.\n"
            f"4. Service Account ka email (e.g. your-bot@project.iam.gserviceaccount.com) copy karke apne Google Analytics\n"
            f"   (Property ID: {getattr(config, 'GA_PROPERTY_ID', '558495815')}) ke Admin > Property Access Management me 'Viewer' role add kar dein."
        )

    return BetaAnalyticsDataClient.from_service_account_file(str(cred_path))


def format_duration(seconds: float) -> str:
    """Formats seconds into readable mm:ss format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}m {secs}s"


def fetch_realtime_report(property_id: str = None) -> Dict[str, Any]:
    """
    Fetches real-time active users right now (last 30 minutes)
    and current active pages/stories.
    """
    from google.analytics.data_v1beta.types import (
        Dimension,
        Metric,
        RunRealtimeReportRequest,
    )

    prop_id = property_id or getattr(config, "GA_PROPERTY_ID", "558495815")
    client = get_client()

    request = RunRealtimeReportRequest(
        property=f"properties/{prop_id}",
        dimensions=[
            Dimension(name="unifiedScreenName"),
            Dimension(name="country"),
        ],
        metrics=[Metric(name="activeUsers")],
    )

    response = client.run_realtime_report(request)

    total_active_users = 0
    pages_active: List[Dict[str, Any]] = []

    for row in response.rows:
        screen_name = row.dimension_values[0].value
        country = row.dimension_values[1].value
        users = int(row.metric_values[0].value)
        total_active_users += users
        pages_active.append({
            "page": screen_name,
            "country": country,
            "users": users
        })

    return {
        "property_id": prop_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_active_users_30m": total_active_users,
        "active_pages": pages_active,
    }


def fetch_overview_report(days: int = 7, property_id: str = None) -> Dict[str, Any]:
    """
    Fetches overview traffic metrics: Active Users, Total Sessions,
    Pageviews, Average Session Duration, Bounce Rate.
    """
    from google.analytics.data_v1beta.types import (
        DateRange,
        Metric,
        RunReportRequest,
    )

    prop_id = property_id or getattr(config, "GA_PROPERTY_ID", "558495815")
    client = get_client()

    start_date = "today" if days == 0 else f"{days}daysAgo"
    request = RunReportRequest(
        property=f"properties/{prop_id}",
        date_ranges=[DateRange(start_date=start_date, end_date="today")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
        ],
    )

    response = client.run_report(request)

    if not response.rows:
        return {
            "property_id": prop_id,
            "days": days,
            "active_users": 0,
            "sessions": 0,
            "pageviews": 0,
            "avg_duration": "0m 0s",
            "bounce_rate": "0.0%",
        }

    row = response.rows[0]
    active_users = int(row.metric_values[0].value)
    sessions = int(row.metric_values[1].value)
    pageviews = int(row.metric_values[2].value)
    avg_duration_sec = float(row.metric_values[3].value)
    bounce_rate = float(row.metric_values[4].value) * 100

    return {
        "property_id": prop_id,
        "days": days,
        "active_users": active_users,
        "sessions": sessions,
        "pageviews": pageviews,
        "avg_duration": format_duration(avg_duration_sec),
        "bounce_rate": f"{bounce_rate:.1f}%",
    }


def fetch_top_stories_report(days: int = 7, limit: int = 10, property_id: str = None) -> List[Dict[str, Any]]:
    """
    Fetches top-performing news articles and AMP Stories sorted by page views.
    """
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
        OrderBy,
    )

    prop_id = property_id or getattr(config, "GA_PROPERTY_ID", "558495815")
    client = get_client()

    start_date = "today" if days == 0 else f"{days}daysAgo"
    request = RunReportRequest(
        property=f"properties/{prop_id}",
        date_ranges=[DateRange(start_date=start_date, end_date="today")],
        dimensions=[
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
        ],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
        ],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)
        ],
        limit=limit,
    )

    response = client.run_report(request)
    results = []

    for row in response.rows:
        path = row.dimension_values[0].value
        title = row.dimension_values[1].value
        views = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        is_story = "/stories/" in path
        results.append({
            "path": path,
            "title": title,
            "views": views,
            "users": users,
            "type": "AMP Story" if is_story else "Article / Page"
        })

    return results


def fetch_traffic_sources_report(days: int = 7, property_id: str = None) -> List[Dict[str, Any]]:
    """
    Fetches traffic source acquisition breakdown (Google Search, Direct, Social, etc.).
    """
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
        OrderBy,
    )

    prop_id = property_id or getattr(config, "GA_PROPERTY_ID", "558495815")
    client = get_client()

    start_date = "today" if days == 0 else f"{days}daysAgo"
    request = RunReportRequest(
        property=f"properties/{prop_id}",
        date_ranges=[DateRange(start_date=start_date, end_date="today")],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
        ],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)
        ],
        limit=10,
    )

    response = client.run_report(request)
    results = []

    for row in response.rows:
        source = row.dimension_values[0].value
        medium = row.dimension_values[1].value
        sessions = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        results.append({
            "source": source,
            "medium": medium,
            "sessions": sessions,
            "users": users,
        })

    return results


def print_full_report(days: int = 7):
    """Prints a beautiful, comprehensive terminal report."""
    prop_id = getattr(config, "GA_PROPERTY_ID", "558495815")
    range_label = "Today" if days == 0 else f"Past {days} Days"
    print("\n" + "=" * 65)
    print(f"📊 {config.SITE_NAME} - Google Analytics 4 Report (Property: {prop_id})")
    print(f"🕒 Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')} | Range: {range_label}")
    print("=" * 65)

    try:
        # 1. Realtime
        rt = fetch_realtime_report(prop_id)
        print(f"\n⚡ REALTIME (Last 30 Minutes):")
        print(f"   👥 Active Users Right Now: {rt['total_active_users_30m']}")
        if rt["active_pages"]:
            for item in rt["active_pages"][:5]:
                print(f"   • {item['users']} user(s) | {item['page']} ({item['country']})")
        else:
            print("   • No active visitors in the last 30 minutes.")

        # 2. Overview
        ov = fetch_overview_report(days=days, property_id=prop_id)
        print(f"\n📈 TRAFFIC OVERVIEW (Past {days} Days):")
        print(f"   👥 Active Users:            {ov['active_users']:,}")
        print(f"   🔄 Total Sessions:          {ov['sessions']:,}")
        print(f"   📄 Page Views:              {ov['pageviews']:,}")
        print(f"   ⏱️ Avg Engagement Time:     {ov['avg_duration']}")
        print(f"   📉 Bounce Rate:             {ov['bounce_rate']}")

        # 3. Top Stories & Pages
        stories = fetch_top_stories_report(days=days, limit=7, property_id=prop_id)
        print(f"\n🔥 TOP PERFORMING STORIES & PAGES:")
        if stories:
            for idx, s in enumerate(stories, 1):
                print(f"   {idx}. [{s['type']}] {s['views']:,} views ({s['users']} users)")
                print(f"      {s['title'][:55]}...")
                print(f"      URL: {s['path']}")
        else:
            print("   • No pageview data recorded for this period yet.")

        # 4. Traffic Sources
        sources = fetch_traffic_sources_report(days=days, property_id=prop_id)
        print(f"\n🌐 TRAFFIC SOURCES & CHANNELS:")
        if sources:
            for src in sources[:5]:
                channel = f"{src['source']} / {src['medium']}"
                print(f"   • {channel:<28} : {src['sessions']:,} sessions ({src['users']:,} users)")
        else:
            print("   • No traffic source data recorded yet.")

        print("\n" + "=" * 65)

    except FileNotFoundError as fnf_err:
        print("\n⚠️ SETUP REQUIRED:")
        print(str(fnf_err))
        print("=" * 65 + "\n")
    except Exception as e:
        err_msg = str(e)
        if "403" in err_msg or "permission" in err_msg.lower():
            print(f"\n⚠️ PERMISSION REQUIRED IN GOOGLE ANALYTICS:")
            print(f"Service account connect ho chuka hai, lekin Property ID '{prop_id}' ka access nahi mila.")
            print(f"\nBas ye 2 step karein:")
            print(f"1. Service Account Email copy karein:")
            print(f"   ga-reporter@spry-notch-511410-v5.iam.gserviceaccount.com")
            print(f"2. Google Analytics Admin > 'Account Access Management' (ya Property Access Management)")
            print(f"   me jakar is email ko 'Viewer' role add kar dein.")
        else:
            print(f"\n❌ Error fetching GA4 reports: {e}")
        print("=" * 65 + "\n")


def export_markdown_report(days: int = 7, output_path: Optional[Path] = None) -> Path:
    """Exports a formatted markdown report to disk."""
    if output_path is None:
        output_path = config.DATA_DIR / "ga_report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prop_id = getattr(config, "GA_PROPERTY_ID", "558495815")
    rt = fetch_realtime_report(prop_id)
    ov = fetch_overview_report(days=days, property_id=prop_id)
    stories = fetch_top_stories_report(days=days, limit=10, property_id=prop_id)
    sources = fetch_traffic_sources_report(days=days, property_id=prop_id)

    range_label = "Today" if days == 0 else f"Past {days} Days"
    lines = [
        f"# 📊 {config.SITE_NAME} - Google Analytics 4 Report",
        f"**Property ID:** `{prop_id}` | **Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Time Window:** {range_label}\n",
        "## ⚡ Realtime Visitors (Last 30 Minutes)",
        f"- **Active Users:** {rt['total_active_users_30m']}",
    ]
    if rt["active_pages"]:
        for item in rt["active_pages"]:
            lines.append(f"  - `{item['page']}` ({item['country']}): **{item['users']} user(s)**")
    else:
        lines.append("  - *No active users in the last 30 minutes.*")

    lines.extend([
        f"\n## 📈 Performance Overview ({range_label})",
        f"| Metric | Value |",
        f"|---|---|",
        f"| 👥 Active Users | **{ov['active_users']:,}** |",
        f"| 🔄 Total Sessions | **{ov['sessions']:,}** |",
        f"| 📄 Page Views | **{ov['pageviews']:,}** |",
        f"| ⏱️ Avg Session Duration | **{ov['avg_duration']}** |",
        f"| 📉 Bounce Rate | **{ov['bounce_rate']}** |",
        f"\n## 🔥 Top Performing Stories & Pages",
        f"| # | Type | Pageviews | Users | Title & URL |",
        f"|---|---|---|---|---|",
    ])
    if stories:
        for idx, s in enumerate(stories, 1):
            lines.append(f"| {idx} | `{s['type']}` | {s['views']:,} | {s['users']} | [{s['title']}]({s['path']}) |")
    else:
        lines.append("| - | - | 0 | 0 | *No pageviews recorded yet* |")

    lines.extend([
        f"\n## 🌐 Traffic Sources & Acquisition",
        f"| Source / Medium | Sessions | Active Users |",
        f"|---|---|---|",
    ])
    if sources:
        for src in sources:
            lines.append(f"| `{src['source']} / {src['medium']}` | {src['sessions']:,} | {src['users']:,} |")
    else:
        lines.append("| *None* | 0 | 0 |")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Google Analytics 4 Automated Reporter for NewsPulse")
    parser.add_argument("--today", action="store_true", help="Show today's traffic report")
    parser.add_argument("--days", type=int, default=7, help="Number of days for traffic report (default: 7)")
    parser.add_argument("--realtime", action="store_true", help="Show real-time active users only")
    parser.add_argument("--overview", action="store_true", help="Show overview metrics only")
    parser.add_argument("--top-stories", action="store_true", help="Show top stories only")
    parser.add_argument("--sources", action="store_true", help="Show traffic sources only")
    parser.add_argument("--export", action="store_true", help="Export summary to data/ga_report.md")

    args = parser.parse_args()

    cred_path = get_credentials_path()
    if not cred_path:
        print("\n" + "=" * 65)
        print(f"⚠️  Google Analytics credentials JSON nahi mila!")
        print("=" * 65)
        print(f"File expected at: {config.BASE_DIR / 'ga_credentials.json'}\n")
        print("Service Account setup karne ke 4 aasan steps:")
        print("1. Google Cloud Console (https://console.cloud.google.com) par jayein.")
        print("2. 'Google Analytics Data API' ko enable karein.")
        print("3. IAM & Admin > Service Accounts me ek naya Service Account banakar JSON key download karein.")
        print("4. Uss JSON file ko rename karke 'ga_credentials.json' naam se project me paste kar dein.")
        print(f"5. Service Account email ko Google Analytics (Property: {getattr(config, 'GA_PROPERTY_ID', '558495815')})")
        print("   me jakar 'Viewer' permission de dein.")
        print("=" * 65 + "\n")
        sys.exit(1)

    effective_days = 0 if args.today else args.days

    if args.export:
        out_file = export_markdown_report(days=effective_days)
        print(f"✅ Analytics report successfully exported to: {out_file}")
    elif args.realtime:
        rt = fetch_realtime_report()
        print(f"\n⚡ Realtime Active Users (Last 30 mins): {rt['total_active_users_30m']}")
        for p in rt["active_pages"]:
            print(f"  • {p['users']} user(s) on {p['page']} ({p['country']})")
    elif args.overview:
        ov = fetch_overview_report(days=effective_days)
        print(f"\n📈 Overview ({'Today' if effective_days == 0 else f'Past {effective_days} Days'}):")
        print(f"  Users: {ov['active_users']} | Sessions: {ov['sessions']} | Views: {ov['pageviews']} | Avg Time: {ov['avg_duration']}")
    elif args.top_stories:
        stories = fetch_top_stories_report(days=effective_days)
        print(f"\n🔥 Top Stories ({'Today' if effective_days == 0 else f'Past {effective_days} Days'}):")
        for s in stories:
            print(f"  • {s['views']} views - {s['title']} ({s['path']})")
    elif args.sources:
        sources = fetch_traffic_sources_report(days=effective_days)
        print(f"\n🌐 Traffic Sources ({'Today' if effective_days == 0 else f'Past {effective_days} Days'}):")
        for src in sources:
            print(f"  • {src['source']}/{src['medium']}: {src['sessions']} sessions")
    else:
        print_full_report(days=effective_days)



if __name__ == "__main__":
    main()

