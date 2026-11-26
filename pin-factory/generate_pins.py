import csv
import json
import os
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SITE_CONFIG = json.loads((ROOT / "site" / "site.config.json").read_text(encoding="utf-8"))
POSTS_DIR = ROOT / "site" / "content" / "posts"
BG_DIR = Path(__file__).resolve().parent / "backgrounds"
OUT_DIR = Path(__file__).resolve().parent / "output"

W, H = 1000, 1500

FONT_PATHS = {
    "bold": [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ],
    "regular": [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ],
    "serif_bold": [
        r"C:\Windows\Fonts\georgiab.ttf",
        r"C:\Windows\Fonts\timesbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
    ],
    "serif_italic": [
        r"C:\Windows\Fonts\georgiai.ttf",
        r"C:\Windows\Fonts\timesi.ttf",
        r"C:\Windows\Fonts\georgia.ttf",
    ],
}


def load_font(style: str, size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS[style]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_brand_footer() -> str:
    if SITE_CONFIG.get("showDomainOnPins"):
        return SITE_CONFIG["baseUrl"].replace("https://", "").replace("http://", "").rstrip("/")
    return SITE_CONFIG["siteName"].upper()


def extract_lead_number(post: dict, headline: str) -> str:
    m = re.search(r"\b(\d{1,2})\b", headline)
    if m:
        return m.group(1).zfill(2)
    return str(len(post.get("items", []))).zfill(2)


def draw_wrapped(draw, text, font, box_x, box_y, max_chars, fill, line_spacing=1.18, align="left", box_w=W):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=max_chars))
    y = box_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = box_x if align == "left" else box_x + (box_w - lw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += int(lh * line_spacing) + 8
    return y


def find_backgrounds(slug: str):
    if not BG_DIR.exists():
        return []
    found = []
    for suffix in ("", "-2", "-3", "-4"):
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            cand = BG_DIR / f"{slug}{suffix}{ext}"
            if cand.exists():
                found.append(cand)
                break
    return found


def load_fit(path: Path, w: int, h: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS)


def render_collage_2photo(post: dict, headline: str, bgs: list[Path], out_path: Path):
    """Style 1: High-CTR 2-Photo Vertical Collage + Center Editorial Band + Big Number."""
    img = Image.new("RGB", (W, H), "#FAF7F2")
    gap = 18
    half_h = (H - gap * 3) // 2
    p1 = load_fit(bgs[0], W - gap * 2, half_h)
    p2 = load_fit(bgs[1 % len(bgs)], W - gap * 2, half_h)
    img.paste(p1, (gap, gap))
    img.paste(p2, (gap, gap * 2 + half_h))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    band_top, band_bot = 495, 1005
    od.rounded_rectangle([54, band_top, W - 54, band_bot], radius=24, fill=(253, 251, 247, 246))
    od.rounded_rectangle([54, band_top, W - 54, band_bot], radius=24, outline=(218, 208, 194, 255), width=3)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    cat = (post.get("categoryLabel") or "ORGANIZATION").upper()
    f_cat = load_font("bold", 24)
    cb = d.textbbox((0, 0), cat, font=f_cat)
    cw = (cb[2] - cb[0]) + 44
    d.rounded_rectangle([(W - cw) // 2, band_top + 34, (W + cw) // 2, band_top + 82], radius=24, fill="#EFE5DA")
    d.text(((W - (cb[2] - cb[0])) // 2, band_top + 44), cat, font=f_cat, fill="#A65336")

    f_title = load_font("serif_bold", 58)
    draw_wrapped(d, headline, f_title, 90, band_top + 110, max_chars=23, fill="#1A1917", line_spacing=1.18, align="center", box_w=W - 180)

    cta_y = band_bot - 122
    d.rounded_rectangle([250, cta_y, W - 250, cta_y + 66], radius=33, fill="#2C4A3E")
    f_cta = load_font("bold", 26)
    ct = "READ THE GUIDE  ->"
    ctb = d.textbbox((0, 0), ct, font=f_cta)
    d.text(((W - (ctb[2] - ctb[0])) // 2, cta_y + 17), ct, font=f_cta, fill="#FFFFFF")

    br = get_brand_footer()
    f_br = load_font("bold", 20)
    brb = d.textbbox((0, 0), br, font=f_br)
    d.text(((W - (brb[2] - brb[0])) // 2, band_bot - 40), br, font=f_br, fill="#7A7267")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def render_collage_3photo(post: dict, headline: str, bgs: list[Path], out_path: Path):
    """Style 2: High-CTR 3-Photo Magazine Grid (1 large top + 2 side-by-side bottom) + Dark Ribbon."""
    img = Image.new("RGB", (W, H), "#FAF7F2")
    gap = 16
    top_h = 840
    bot_h = H - top_h - gap * 3
    bot_w = (W - gap * 3) // 2

    img.paste(load_fit(bgs[1 % len(bgs)], W - gap * 2, top_h), (gap, gap))
    img.paste(load_fit(bgs[0], bot_w, bot_h), (gap, top_h + gap * 2))
    img.paste(load_fit(bgs[2 % len(bgs)], bot_w, bot_h), (gap * 2 + bot_w, top_h + gap * 2))

    # Crisp dark ribbon right over the horizontal seam
    ribbon_top, ribbon_bot = 665, 1025
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, ribbon_top, W, ribbon_bot], fill=(24, 24, 22, 232))
    od.rectangle([0, ribbon_top, W, ribbon_top + 6], fill=(184, 93, 59, 255))
    od.rectangle([0, ribbon_bot - 6, W, ribbon_bot], fill=(184, 93, 59, 255))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    num = extract_lead_number(post, headline)
    f_num = load_font("serif_bold", 118)
    d.text((62, ribbon_top + 92), num, font=f_num, fill="#E08E63")

    d.line([(235, ribbon_top + 56), (235, ribbon_bot - 56)], fill="#555049", width=3)

    cat = (post.get("categoryLabel") or "ORGANIZATION").upper()
    d.text((268, ribbon_top + 48), cat, font=load_font("bold", 24), fill="#E08E63")

    f_title = load_font("bold", 48)
    draw_wrapped(d, headline, f_title, 268, ribbon_top + 92, max_chars=23, fill="#FFFFFF", line_spacing=1.18)

    d.text((268, ribbon_bot - 54), f"TAP FOR ALL PICKS  ·  {get_brand_footer()}", font=load_font("regular", 22), fill="#D0C9BF")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def render_bignum_hero(post: dict, headline: str, bgs: list[Path], out_path: Path):
    """Style 3: Full-bleed Photo 3 + Dark Editorial Gradient + Huge Number Callout + CTA Pill."""
    base = load_fit(bgs[2 % len(bgs)], W, H).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for yy in range(560, H):
        alpha = int(238 * ((yy - 560) / (H - 560)) ** 1.1)
        od.line([(0, yy), (W, yy)], fill=(18, 20, 18, alpha))
    img = Image.alpha_composite(base, overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    num = extract_lead_number(post, headline)
    f_big = load_font("serif_bold", 136)
    d.text((68, 720), num, font=f_big, fill="#E08E63")

    cat = (post.get("categoryLabel") or "ORGANIZATION").upper()
    f_cat = load_font("bold", 25)
    cb = d.textbbox((0, 0), cat, font=f_cat)
    d.rounded_rectangle([264, 782, 264 + (cb[2] - cb[0]) + 44, 834], radius=26, fill="#A65336")
    d.text((286, 794), cat, font=f_cat, fill="#FFFFFF")

    f_title = load_font("bold", 60)
    draw_wrapped(d, headline, f_title, 68, 895, max_chars=22, fill="#FFFFFF", line_spacing=1.16)

    d.rounded_rectangle([68, H - 156, 460, H - 86], radius=35, fill="#FFFFFF")
    d.text((104, H - 138), "SEE ALL PICKS  ->", font=load_font("bold", 26), fill="#1A1917")

    br = get_brand_footer()
    f_br = load_font("bold", 22)
    brb = d.textbbox((0, 0), br, font=f_br)
    d.text((W - 68 - (brb[2] - brb[0]), H - 134), br, font=f_br, fill="#DCD5CB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def render_polaroid_editorial(post: dict, headline: str, bgs: list[Path], out_path: Path):
    """Style 4: Kinfolk / Framed Gallery Polaroid Layout (Warm cream frame + clean photo + serif below)."""
    img = Image.new("RGB", (W, H), "#F4EFE6")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill="#2C4A3E")

    # Top subtle brand + category
    cat = (post.get("categoryLabel") or "ORGANIZATION").upper()
    d.text((70, 48), cat, font=load_font("bold", 24), fill="#A65336")
    br = get_brand_footer()
    f_br = load_font("serif_bold", 26)
    brb = d.textbbox((0, 0), br, font=f_br)
    d.text((W - 70 - (brb[2] - brb[0]), 46), br, font=f_br, fill="#1A1917")

    # Framed gallery photo
    photo = load_fit(bgs[1 % len(bgs)], W - 140, 820)
    d.rectangle([66, 106, W - 66, 934], fill="#FFFFFF", outline="#DDD5C9", width=3)
    img.paste(photo, (70, 110))

    # Crisp editorial serif title below photo
    f_title = load_font("serif_bold", 58)
    draw_wrapped(d, headline, f_title, 70, 975, max_chars=24, fill="#1A1917", line_spacing=1.18, align="center", box_w=W - 140)

    d.rounded_rectangle([260, H - 132, W - 260, H - 62], radius=35, fill="#1A1917")
    f_cta = load_font("bold", 26)
    ct = "SAVE & READ GUIDE  ->"
    ctb = d.textbbox((0, 0), ct, font=f_cta)
    d.text(((W - (ctb[2] - ctb[0])) // 2, H - 114), ct, font=f_cta, fill="#FFFFFF")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def render_checklist_pin(post: dict, headline: str, out_path: Path):
    """Style 5: High-Save Editorial Checklist Card."""
    img = Image.new("RGB", (W, H), "#233A31")
    d = ImageDraw.Draw(img)
    pad = 64
    d.rounded_rectangle([pad, pad, W - pad, H - pad], radius=32, fill="#FAF8F4")
    d.rounded_rectangle([pad + 48, pad + 48, pad + 210, pad + 58], radius=5, fill="#A65336")

    cat = (post.get("categoryLabel") or "ORGANIZATION").upper()
    f_pill = load_font("bold", 25)
    tb = d.textbbox((0, 0), cat, font=f_pill)
    pw = (tb[2] - tb[0]) + 44
    d.rounded_rectangle([pad + 48, pad + 90, pad + 48 + pw, pad + 142], radius=26, fill="#EAE1D6")
    d.text((pad + 70, pad + 101), cat, font=f_pill, fill="#A65336")

    y = draw_wrapped(d, headline, load_font("serif_bold", 62), pad + 48, pad + 182, max_chars=21, fill="#1A1917", line_spacing=1.16)
    y += 22
    d.line([(pad + 48, y), (W - pad - 48, y)], fill="#E2DAD0", width=3)
    y += 38

    f_item = load_font("bold", 33)
    f_sub = load_font("regular", 24)
    for idx, item in enumerate(post.get("items", [])[:4], start=1):
        cx, cy = pad + 72, y + 22
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill="#2C4A3E")
        f_num = load_font("bold", 23)
        nb = d.textbbox((0, 0), str(idx), font=f_num)
        d.text((cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - 2), str(idx), font=f_num, fill="#FFFFFF")
        name_short = item["name"] if len(item["name"]) <= 38 else item["name"][:35] + "..."
        d.text((pad + 112, y), name_short, font=f_item, fill="#1A1917")
        d.text((pad + 112, y + 44), item.get("badge", "Space-Saving Pick"), font=f_sub, fill="#6E685F")
        y += 116
        if y > H - pad - 240:
            break

    cta_y = H - pad - 165
    d.rounded_rectangle([pad + 48, cta_y, W - pad - 48, cta_y + 82], radius=41, fill="#A65336")
    ct = "TAP TO SEE ALL PICKS  ->"
    f_cta = load_font("bold", 30)
    cb = d.textbbox((0, 0), ct, font=f_cta)
    d.text(((W - (cb[2] - cb[0])) // 2, cta_y + 22), ct, font=f_cta, fill="#FFFFFF")

    br = get_brand_footer()
    f_br = load_font("bold", 22)
    bb = d.textbbox((0, 0), br, font=f_br)
    d.text(((W - (bb[2] - bb[0])) // 2, H - pad - 56), br, font=f_br, fill="#6E685F")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    queue = []
    base_url = SITE_CONFIG["baseUrl"].rstrip("/")

    for post_file in sorted(POSTS_DIR.glob("*.json")):
        post = json.loads(post_file.read_text(encoding="utf-8"))
        slug = post["slug"]
        hooks = post.get("pinHooks") or [post["title"]]
        bgs = find_backgrounds(slug)

        styles = ["collage_2photo", "collage_3photo", "bignum_hero", "polaroid_editorial", "checklist"]
        for i, style_name in enumerate(styles):
            pin_path = OUT_DIR / slug / f"pin-{i + 1}.png"
            hook = hooks[i % len(hooks)]
            if bgs and style_name == "collage_2photo":
                render_collage_2photo(post, hook, bgs, pin_path)
            elif bgs and style_name == "collage_3photo":
                render_collage_3photo(post, hook, bgs, pin_path)
            elif bgs and style_name == "bignum_hero":
                render_bignum_hero(post, hook, bgs, pin_path)
            elif bgs and style_name == "polaroid_editorial":
                render_polaroid_editorial(post, hook, bgs, pin_path)
            else:
                render_checklist_pin(post, hook, pin_path)

            queue.append(
                {
                    "slug": slug,
                    "pin_index": i + 1,
                    "pin_style": style_name,
                    "image_path": str(pin_path),
                    "board": post.get("pinterestBoard", "Small Kitchen Organization Ideas"),
                    "pin_title": hook[:100],
                    "pin_description": f"{post['metaDescription']} Tap to see all {len(post['items'])} renter-friendly picks on {SITE_CONFIG['siteName']}."[:500],
                    "alt_text": f"{hook} — visual guide of practical small-space organization picks",
                    "destination_url": f"{base_url}/posts/{slug}/",
                    "status": "ready",
                }
            )

    (OUT_DIR / "schedule_queue.json").write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    with (OUT_DIR / "schedule_queue.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(queue[0].keys()) if queue else [])
        if queue:
            writer.writeheader()
            writer.writerows(queue)

    print(f"Generated {len(queue)} high-CTR collage & editorial Pinterest Pins into {OUT_DIR}")


if __name__ == "__main__":
    main()
