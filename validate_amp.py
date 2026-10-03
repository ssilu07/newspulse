"""
NewsPulse - AMP Compliance Validator
Validates generated AMP Web Stories using both:
1. Python structural and heuristic rule verification
2. Official Google AMP Validator CLI (npx amphtml-validator)
"""

import sys
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def validate_single_story_rules(file_path: Path) -> tuple[bool, list[str]]:
    """Runs strict structural AMP checks on an individual HTML file."""
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # 1. Boilerplate check
    if not (content.startswith("<!doctype html>") or content.startswith("<!DOCTYPE html>")):
        issues.append("Missing <!doctype html>")

    if not ("<html ⚡" in content or "<html amp" in content):
        issues.append("Missing ⚡ or amp attribute on <html> tag")

    if '<style amp-boilerplate>' not in content or '<style amp-boilerplate>' not in content:
        issues.append("Missing standard amp-boilerplate style tag")

    if '<script async src="https://cdn.ampproject.org/v0.js"></script>' not in content:
        issues.append("Missing core AMP runtime script (v0.js)")

    if 'custom-element="amp-story"' not in content:
        issues.append("Missing custom-element='amp-story' script")

    # 2. BeautifulSoup DOM inspection
    soup = BeautifulSoup(content, "html.parser")

    # Canonical
    canonical = soup.find("link", rel="canonical")
    if not canonical or not canonical.get("href"):
        issues.append("Missing or empty <link rel='canonical'>")

    # Charset
    charset = soup.find("meta", charset=True)
    if not charset:
        issues.append("Missing <meta charset='utf-8'>")

    # Story Element
    story = soup.find("amp-story")
    if not story:
        issues.append("Missing <amp-story> element")
    else:
        if not story.has_attr("standalone"):
            issues.append("<amp-story> must contain 'standalone' attribute")
        if not story.get("title"):
            issues.append("<amp-story> missing required 'title' attribute")
        if not story.get("publisher"):
            issues.append("<amp-story> missing required 'publisher' attribute")
        if not story.get("publisher-logo-src"):
            issues.append("<amp-story> missing required 'publisher-logo-src' attribute")
        if not story.get("poster-portrait-src"):
            issues.append("<amp-story> missing required 'poster-portrait-src' attribute")

        # Pages
        pages = story.find_all("amp-story-page")
        if not pages:
            issues.append("<amp-story> has no <amp-story-page> children")

        page_ids = set()
        for idx, page in enumerate(pages):
            pid = page.get("id")
            if not pid:
                issues.append(f"Page #{idx+1} missing unique 'id' attribute")
            elif pid in page_ids:
                issues.append(f"Duplicate page id '{pid}'")
            else:
                page_ids.add(pid)

            # Check that <a> is not inside amp-story-grid-layer
            grid_layers = page.find_all("amp-story-grid-layer")
            for gl in grid_layers:
                links_in_grid = gl.find_all("a")
                if links_in_grid:
                    issues.append(f"Page '{pid}' has <a> tag directly inside amp-story-grid-layer (only allowed in amp-story-cta-layer)")

        # Images
        amp_imgs = story.find_all("amp-img")
        for img in amp_imgs:
            if not img.get("src"):
                issues.append("Found <amp-img> without 'src'")
            if not img.get("layout") and (not img.get("width") or not img.get("height")):
                issues.append(f"<amp-img src='{img.get('src', '')}'> requires layout or width/height")

    # Check for !important in style amp-custom
    custom_style = soup.find("style", {"amp-custom": True})
    if custom_style and "!important" in custom_style.text:
        issues.append("Custom CSS contains prohibited '!important' declaration")

    return len(issues) == 0, issues


def run_official_amp_validator(file_path: Path) -> tuple[bool, str]:
    """Invokes npx amphtml-validator CLI if Node/npx is present."""
    try:
        cmd = ["npx", "amphtml-validator", str(file_path)]
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=25
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        passed = (proc.returncode == 0) and ("PASS" in output)
        return passed, output.strip()
    except Exception as e:
        return False, f"Could not run npx amphtml-validator: {e}"


def validate_all_stories(dist_dir: Path = None) -> bool:
    """Validates all generated stories in dist/stories/."""
    if dist_dir is None:
        dist_dir = config.DIST_DIR

    stories_dir = dist_dir / "stories"
    if not stories_dir.exists():
        print(f"[!] Warning: Stories directory not found at {stories_dir}")
        return False

    story_files = list(stories_dir.glob("*/index.html"))
    if not story_files:
        print("[!] No story index.html files found to validate.")
        return False

    print(f"[*] Validating {len(story_files)} AMP Stories...")
    all_passed = True

    for sfile in story_files:
        slug = sfile.parent.name
        # 1. Structural rule validation
        ok_rules, issues = validate_single_story_rules(sfile)
        if not ok_rules:
            all_passed = False
            print(f"    [FAIL] {slug} structural checks:")
            for iss in issues:
                print(f"           - {iss}")
            continue

        # 2. Official Google validator
        ok_official, official_msg = run_official_amp_validator(sfile)
        if ok_official:
            print(f"    [PASS] {slug} -> 100% Valid Google AMP Story (PASS)")
        else:
            all_passed = False
            print(f"    [FAIL] {slug} official validator failure:\n{official_msg}")

    if all_passed:
        print(f"[OK] ALL {len(story_files)} AMP Stories PASSED 100% Google AMP Validation!")
    else:
        print("[!] Some stories did not pass full validation. Please review above.")

    return all_passed


if __name__ == "__main__":
    success = validate_all_stories()
    sys.exit(0 if success else 1)
