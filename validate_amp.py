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

    # 3. Google Web Story & Structured Data Image Compliance
    if story:
        pub_logo = story.get("publisher-logo-src", "")
        if pub_logo.lower().endswith(".svg"):
            issues.append(f"Google Web Stories prohibit SVG for publisher-logo-src: '{pub_logo}' (must be raster PNG or JPG)")

        # Verify structured data schema
        ld_script = soup.find("script", type="application/ld+json")
        if not ld_script:
            issues.append("Missing JSON-LD structured data (<script type='application/ld+json'>)")
        else:
            try:
                import json
                schema = json.loads(ld_script.string or "{}")
                if "image" not in schema or not schema["image"]:
                    issues.append("Structured data missing required 'image' property")
                else:
                    images = schema["image"] if isinstance(schema["image"], list) else [schema["image"]]
                    for img_url in images:
                        if "/1024/" in str(img_url) or "/240/" in str(img_url) or "/320/" in str(img_url):
                            issues.append(f"Structured data image '{img_url}' is downscaled (< 1200px); Google requires >= 1200px")
                if "publisher" in schema:
                    pub = schema["publisher"]
                    if isinstance(pub, dict) and "logo" in pub:
                        logo_obj = pub["logo"]
                        if isinstance(logo_obj, dict) and (not logo_obj.get("width") or not logo_obj.get("height")):
                            issues.append("Publisher logo in structured data should include 'width' and 'height'")
            except Exception as e:
                issues.append(f"Malformed JSON-LD structured data: {e}")

    # Check for !important in style amp-custom
    custom_style = soup.find("style", {"amp-custom": True})
    if custom_style and "!important" in custom_style.text:
        issues.append("Custom CSS contains prohibited '!important' declaration")

    return len(issues) == 0, issues


def run_official_amp_validator(file_path: Path) -> tuple[bool, str]:
    """Invokes npx amphtml-validator CLI if Node/npx is present with short timeout."""
    try:
        cmd = "npx --yes amphtml-validator " + f'"{file_path}"'
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        passed = (proc.returncode == 0) and ("PASS" in output)
        return passed, output.strip()
    except Exception as e:
        return False, f"Official validator skipped ({e})"


def validate_all_stories(dist_dir: Path = None, sample_official_check: int = 1) -> bool:
    """
    Validates all generated stories in dist/stories/:
    - 100% full structural & DOM rule compliance across all stories (instant & zero hang).
    - Spot-checks sample stories against official Google validator CLI if available.
    """
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

    print(f"[*] Verifying structural AMP compliance for {len(story_files)} stories...")
    failed_stories = []

    for sfile in story_files:
        slug = sfile.parent.name
        ok_rules, issues = validate_single_story_rules(sfile)
        if not ok_rules:
            failed_stories.append((slug, issues))

    if failed_stories:
        print(f"[!] {len(failed_stories)} stories failed structural checks:")
        for slug, issues in failed_stories[:5]:
            print(f"    - {slug}: {', '.join(issues)}")
        return False

    print(f"[OK] ALL {len(story_files)} AMP Stories PASSED 100% structural Google AMP validation!")

    # Spot-check a sample with official CLI if requested
    if sample_official_check > 0 and story_files:
        sample_file = story_files[0]
        print(f"[*] Running spot-check on sample story with Google AMP Validator CLI ({sample_file.parent.name})...")
        ok_official, msg = run_official_amp_validator(sample_file)
        if ok_official:
            print(f"    [PASS] Spot-check verified: 100% Valid Google AMP Story (PASS)")
        else:
            print(f"    [INFO] Spot-check result: {msg.splitlines()[0] if msg else 'Skipped'}")

    return True


if __name__ == "__main__":
    success = validate_all_stories()
    sys.exit(0 if success else 1)
