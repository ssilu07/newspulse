"""
Generate ultra-crisp, high-contrast, multi-resolution Favicons, App Icons, and Logos
for News Seconds (newsseconds.com) optimized for:
- Google Search Console property selector (16x16, 32x32, 48x48)
- Google Search Results mobile & desktop snippets
- Apple Touch Icon (180x180)
- PWA / Android Chrome (192x192, 512x512)
- Multi-resolution Windows/Browser favicon.ico
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DIST_DIR = BASE_DIR / "dist"
STATIC_ASSETS = STATIC_DIR / "assets"
DIST_ASSETS = DIST_DIR / "static" / "assets"

STATIC_ASSETS.mkdir(parents=True, exist_ok=True)
DIST_ASSETS.mkdir(parents=True, exist_ok=True)

SIZE = 2048

def create_master_icon() -> Image.Image:
    # 1. Base canvas
    master = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    # 2. Rounded squircle mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    pad = 64
    radius = 460
    mask_draw.rounded_rectangle([pad, pad, SIZE - pad, SIZE - pad], radius=radius, fill=255)

    # 3. Rich deep obsidian / space navy background
    bg = Image.new("RGBA", (SIZE, SIZE), (7, 10, 19, 255))
    bg_draw = ImageDraw.Draw(bg)
    for y in range(SIZE):
        t = y / SIZE
        r = int(10 * (1 - t) + 4 * t)
        g = int(16 * (1 - t) + 7 * t)
        b = int(32 * (1 - t) + 14 * t)
        bg_draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

    # Ambient center-top glow
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([SIZE//2 - 650, 100, SIZE//2 + 650, 1400], fill=(56, 189, 248, 55))
    glow_draw.ellipse([SIZE//2 - 400, 400, SIZE//2 + 400, 1200], fill=(244, 63, 94, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    bg.alpha_composite(glow)
    bg.putalpha(mask)
    master.alpha_composite(bg)

    # 4. Glowing vibrant outer border
    border_mask = Image.new("L", (SIZE, SIZE), 0)
    b_draw = ImageDraw.Draw(border_mask)
    b_draw.rounded_rectangle([pad, pad, SIZE - pad, SIZE - pad], radius=radius, outline=255, width=44)

    border_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bi_draw = ImageDraw.Draw(border_img)
    for y in range(SIZE):
        t = y / SIZE
        if t < 0.5:
            st = t / 0.5
            r = int(56 * (1 - st) + 168 * st)
            g = int(189 * (1 - st) + 85 * st)
            b = int(248 * (1 - st) + 247 * st)
        else:
            st = (t - 0.5) / 0.5
            r = int(168 * (1 - st) + 244 * st)
            g = int(85 * (1 - st) + 63 * st)
            b = int(247 * (1 - st) + 94 * st)
        bi_draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))
    border_img.putalpha(border_mask)
    master.alpha_composite(border_img)

    # 5. Seconds / Timer Outer Dial Accent (Tick marks ring)
    dial_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dial_draw = ImageDraw.Draw(dial_layer)
    cx, cy = SIZE // 2, SIZE // 2
    dial_r = 740
    # Draw 12 subtle stylish minute/second ticks
    for i in range(12):
        angle = i * (360 / 12) - 90
        rad = math.radians(angle)
        x1 = cx + (dial_r - 40) * math.cos(rad)
        y1 = cy + (dial_r - 40) * math.sin(rad)
        x2 = cx + dial_r * math.cos(rad)
        y2 = cy + dial_r * math.sin(rad)
        alpha = 180 if i % 3 == 0 else 80
        dial_draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, alpha), width=18 if i % 3 == 0 else 10)
    master.alpha_composite(dial_layer)

    # 6. Central Bold Iconography: The High-Speed "N" with Second Hand & Pulse
    # Coordinates for thick, high-contrast, scalable "N"
    # Left stem: x from 480 to 710, y from 480 to 1568
    # Right stem: x from 1338 to 1568, y from 480 to 1568
    # Diagonal: from (480, 480) down to (1568, 1568)
    n_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(n_layer)

    stem_w = 210
    top_y = 520
    bot_y = 1528
    left_x = 510
    right_x = 1328

    # Shadow/Glow under the N
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    # Left vertical
    s_draw.rounded_rectangle([left_x, top_y, left_x + stem_w, bot_y], radius=stem_w//2, fill=(0, 0, 0, 160))
    # Right vertical
    s_draw.rounded_rectangle([right_x, top_y, right_x + stem_w, bot_y], radius=stem_w//2, fill=(0, 0, 0, 160))
    # Diagonal polygon
    s_draw.polygon([
        (left_x, top_y + 120),
        (left_x + stem_w, top_y),
        (right_x + stem_w, bot_y - 120),
        (right_x, bot_y),
    ], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    master.alpha_composite(shadow)

    # Left stem: Crisp pure white with subtle cyan rim
    n_draw.rounded_rectangle([left_x, top_y, left_x + stem_w, bot_y], radius=stem_w//2, fill=(255, 255, 255, 255))

    # Right stem: Crisp pure white with subtle rose rim
    n_draw.rounded_rectangle([right_x, top_y, right_x + stem_w, bot_y], radius=stem_w//2, fill=(255, 255, 255, 255))

    # Diagonal: Dynamic High-Energy Gradient (Electric Cyan -> Royal Violet -> Hot Rose)
    diag_mask = Image.new("L", (SIZE, SIZE), 0)
    dm_draw = ImageDraw.Draw(diag_mask)
    dm_draw.polygon([
        (left_x + 10, top_y + 90),
        (left_x + stem_w + 30, top_y + 20),
        (right_x + stem_w - 10, bot_y - 90),
        (right_x - 30, bot_y - 20),
    ], fill=255)

    diag_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    di_draw = ImageDraw.Draw(diag_img)
    for y in range(top_y, bot_y):
        prog = (y - top_y) / (bot_y - top_y)
        if prog < 0.5:
            sp = prog / 0.5
            r = int(56 * (1 - sp) + 168 * sp)
            g = int(189 * (1 - sp) + 85 * st)
            b = int(248 * (1 - sp) + 247 * sp)
        else:
            sp = (prog - 0.5) / 0.5
            r = int(168 * (1 - sp) + 244 * sp)
            g = int(85 * (1 - sp) + 63 * sp)
            b = int(247 * (1 - sp) + 94 * sp)
        di_draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255), width=2)
    diag_img.putalpha(diag_mask)
    n_layer.alpha_composite(diag_img)

    master.alpha_composite(n_layer)

    # 7. Hot Red / Ruby LIVE Beacon Dot in top right
    dot_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dot_draw = ImageDraw.Draw(dot_layer)
    dot_cx = right_x + stem_w // 2
    dot_cy = top_y + 105
    dot_r = 75

    # Glowing halo
    dot_glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dg_draw = ImageDraw.Draw(dot_glow)
    dg_draw.circle((dot_cx, dot_cy), dot_r + 80, fill=(244, 63, 94, 180))
    dg_draw.circle((dot_cx, dot_cy), dot_r + 140, fill=(239, 68, 68, 90))
    dot_glow = dot_glow.filter(ImageFilter.GaussianBlur(40))
    master.alpha_composite(dot_glow)

    # Core ruby dot
    dot_draw.circle((dot_cx, dot_cy), dot_r, fill=(239, 68, 68, 255))
    dot_draw.circle((dot_cx - 20, dot_cy - 20), dot_r // 3, fill=(255, 255, 255, 220))
    master.alpha_composite(dot_layer)

    return master

if __name__ == "__main__":
    print("[*] Generating master 2048x2048 icon...")
    master = create_master_icon()

    # Resample sizes
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "favicon-48x48.png": 48,  # Critical for Googlebot
        "apple-touch-icon.png": 180,
        "android-chrome-192x192.png": 192,
        "android-chrome-512x512.png": 512,
        "logo.png": 512,
    }

    # Save PNGs to both static/ and dist/ and static/assets/
    for name, sz in sizes.items():
        resized = master.resize((sz, sz), Image.Resampling.LANCZOS)
        # Root static & dist
        resized.save(STATIC_DIR / name, "PNG", optimize=True)
        resized.save(DIST_DIR / name, "PNG", optimize=True)
        # Also in assets for backward compat
        if name in ["logo.png", "apple-touch-icon.png"]:
            resized.save(STATIC_ASSETS / name, "PNG", optimize=True)
            resized.save(DIST_ASSETS / name, "PNG", optimize=True)
        print(f"  [OK] Generated {name} ({sz}x{sz})")

    # Multi-resolution favicon.ico (16, 32, 48, 64, 128, 256)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_imgs = [master.resize(s, Image.Resampling.LANCZOS) for s in ico_sizes]
    
    # Save favicon.ico to static/ and dist/
    ico_imgs[0].save(
        STATIC_DIR / "favicon.ico",
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_imgs[1:]
    )
    ico_imgs[0].save(
        DIST_DIR / "favicon.ico",
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_imgs[1:]
    )
    print("  [OK] Generated multi-size favicon.ico (16, 32, 48, 64, 128, 256)")

    # Also generate high-res SVG logo with the matching icon emblem
    svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <defs>
    <linearGradient id="iconN" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#a855f7" />
      <stop offset="100%" stop-color="#f43f5e" />
    </linearGradient>
    <filter id="liveGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <rect width="64" height="64" rx="16" fill="#070a13" />
  <rect x="2" y="2" width="60" height="60" rx="14" stroke="url(#iconN)" stroke-width="2" />
  <!-- Letter N -->
  <rect x="15" y="16" width="6.5" height="32" rx="3.25" fill="#ffffff" />
  <rect x="42.5" y="16" width="6.5" height="32" rx="3.25" fill="#ffffff" />
  <polygon points="17,19 22.5,17 47,45 41.5,47" fill="url(#iconN)" />
  <!-- Live Beacon -->
  <circle cx="45.5" cy="19" r="4.5" fill="#ef4444" filter="url(#liveGlow)" />
  <circle cx="44.5" cy="18" r="1.5" fill="#ffffff" />
</svg>'''

    svg_logo = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 64" fill="none">
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#a855f7" />
      <stop offset="100%" stop-color="#f43f5e" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <!-- Emblem -->
  <rect x="6" y="8" width="48" height="48" rx="14" fill="#070a13" stroke="url(#brandGrad)" stroke-width="2.2" />
  <rect x="18" y="20" width="5" height="24" rx="2.5" fill="#ffffff" />
  <rect x="39" y="20" width="5" height="24" rx="2.5" fill="#ffffff" />
  <polygon points="19.5,22 24,20.5 42.5,42 38,43.5" fill="url(#brandGrad)" />
  <circle cx="41.5" cy="22" r="3.5" fill="#ef4444" filter="url(#glow)">
    <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
  </circle>
  <circle cx="40.5" cy="21" r="1.2" fill="#ffffff" />
  
  <!-- Wordmark -->
  <text x="66" y="37" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="22" fill="#ffffff" letter-spacing="0.5">NEWS<tspan fill="url(#brandGrad)">SECONDS</tspan></text>
  <text x="67" y="49" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="8.5" fill="#94a3b8" letter-spacing="2.2">BITE-SIZED NEWS IN SECONDS</text>
</svg>'''

    with open(STATIC_ASSETS / "icon.svg", "w", encoding="utf-8") as f:
        f.write(svg_icon)
    with open(DIST_ASSETS / "icon.svg", "w", encoding="utf-8") as f:
        f.write(svg_icon)

    with open(STATIC_ASSETS / "logo.svg", "w", encoding="utf-8") as f:
        f.write(svg_logo)
    with open(DIST_ASSETS / "logo.svg", "w", encoding="utf-8") as f:
        f.write(svg_logo)

    print("[OK] Generated static/assets/icon.svg and logo.svg")
    print("[SUCCESS] All icons and favicons generated successfully!")
