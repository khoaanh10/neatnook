import csv
import json
import os
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
}


def load_font(style: str, size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS[style]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_wrapped(draw, text, font, box_x, box_y, max_chars, fill, line_spacing=1.22, align="left"):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=max_chars))
    y = box_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = box_x
        if align == "center":
            x = (W - lw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += int(lh * line_spacing) + 8
    return y


THEMES = [
    {
        "name": "editorial_cream",
        "bg": "#F7F3EC",
        "card": "#FFFFFF",
        "accent": "#B85D3B",
        "ink": "#1E1D1B",
        "muted": "#5E5850",
        "pill_bg": "#EFE5DA",
    },
    {
        "name": "sage_checklist",
        "bg": "#2E473D",
        "card": "#F8FAF9",
        "accent": "#3F6154",
        "ink": "#1C2924",
        "muted": "#52665E",
        "pill_bg": "#E1ECE7",
    },
    {
        "name": "terracotta_bold",
        "bg": "#A74E2F",
        "card": "#FFFDF9",
        "accent": "#A74E2F",
        "ink": "#1E1D1B",
        "muted": "#665B53",
        "pill_bg": "#F7E5DC",
    },
    {
        "name": "charcoal_modern",
        "bg": "#1F2326",
        "card": "#2B3136",
        "accent": "#E08E63",
        "ink": "#FAF8F5",
        "muted": "#C8C3BC",
        "pill_bg": "#3A4249",
    },
    {
        "name": "sand_minimal",
        "bg": "#EDE6DB",
        "card": "#FFFFFF",
        "accent": "#3C5A4F",
        "ink": "#1E1D1B",
        "muted": "#5E5850",
        "pill_bg": "#E3ECE8",
    },
]


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


def render_photo_pin(post: dict, variant_idx: int, bg_path: Path, out_path: Path):
    base = Image.open(bg_path).convert("RGB")
    base = ImageOps.fit(base, (W, H), method=Image.Resampling.LANCZOS)
    img = base.convert("RGBA")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    variants = post.get("pinHooks") or [post["title"]]
    headline = variants[variant_idx % len(variants)]
    cat_text = (post.get("categoryLabel") or post.get("category") or "ORGANIZATION").upper()
    brand_domain = SITE_CONFIG["baseUrl"].replace("https://", "").replace("http://", "").rstrip("/")

    style = variant_idx % 3
    if style == 0:
        # Center frosted magazine card over photo
        odraw.rectangle([0, 0, W, H], fill=(20, 18, 16, 48))
        card_top, card_bot = 430, 1080
        odraw.rounded_rectangle([68, card_top, W - 68, card_bot], radius=32, fill=(250, 248, 244, 238))
        img = Image.alpha_composite(img, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        f_pill = load_font("bold", 26)
        tb = draw.textbbox((0, 0), cat_text, font=f_pill)
        pw = (tb[2] - tb[0]) + 48
        px = (W - pw) // 2
        draw.rounded_rectangle([px, card_top + 48, px + pw, card_top + 102], radius=27, fill="#EFE5DA")
        draw.text((px + 24, card_top + 60), cat_text, font=f_pill, fill="#B85D3B")

        f_title = load_font("serif_bold", 62)
        draw_wrapped(draw, headline, f_title, 100, card_top + 140, max_chars=21, fill="#1E1D1B", line_spacing=1.2, align="center")

        draw.rounded_rectangle([240, card_bot - 140, W - 240, card_bot - 66], radius=37, fill="#B85D3B")
        f_cta = load_font("bold", 28)
        cta_t = "SEE ALL PICKS  ->"
        cb = draw.textbbox((0, 0), cta_t, font=f_cta)
        draw.text(((W - (cb[2] - cb[0])) // 2, card_bot - 122), cta_t, font=f_cta, fill="#FFFFFF")

        f_dom = load_font("regular", 24)
        db = draw.textbbox((0, 0), brand_domain, font=f_dom)
        draw.text(((W - (db[2] - db[0])) // 2, card_bot - 46), brand_domain, font=f_dom, fill="#625D56")

    elif style == 1:
        # Bottom dark editorial gradient band
        for yy in range(620, H):
            alpha = int(225 * ((yy - 620) / (H - 620)) ** 1.15)
            odraw.line([(0, yy), (W, yy)], fill=(20, 22, 20, alpha))
        img = Image.alpha_composite(img, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        f_pill = load_font("bold", 26)
        tb = draw.textbbox((0, 0), cat_text, font=f_pill)
        pw = (tb[2] - tb[0]) + 44
        draw.rounded_rectangle([72, 860, 72 + pw, 914], radius=27, fill="#B85D3B")
        draw.text((94, 872), cat_text, font=f_pill, fill="#FFFFFF")

        f_title = load_font("bold", 64)
        draw_wrapped(draw, headline, f_title, 72, 945, max_chars=22, fill="#FFFFFF", line_spacing=1.18)

        f_dom = load_font("regular", 26)
        draw.text((72, H - 78), f"READ THE FULL GUIDE  |  {brand_domain}", font=f_dom, fill="#E5DFD6")

    else:
        # Top cream header banner + full photo below
        odraw.rectangle([0, 0, W, 520], fill=(247, 243, 236, 245))
        odraw.rectangle([0, 520, W, 528], fill=(184, 93, 59, 255))
        odraw.rounded_rectangle([210, H - 120, W - 210, H - 46], radius=37, fill=(30, 29, 27, 225))
        img = Image.alpha_composite(img, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        f_pill = load_font("bold", 24)
        tb = draw.textbbox((0, 0), cat_text, font=f_pill)
        pw = (tb[2] - tb[0]) + 44
        px = (W - pw) // 2
        draw.rounded_rectangle([px, 54, px + pw, 104], radius=25, fill="#E3ECE8")
        draw.text((px + 22, 65), cat_text, font=f_pill, fill="#3F6154")

        f_title = load_font("serif_bold", 62)
        draw_wrapped(draw, headline, f_title, 80, 134, max_chars=22, fill="#1E1D1B", line_spacing=1.18, align="center")

        f_cta = load_font("bold", 28)
        cta_t = f"TAP FOR GUIDE  |  {SITE_CONFIG['siteName'].upper()}"
        cb = draw.textbbox((0, 0), cta_t, font=f_cta)
        draw.text(((W - (cb[2] - cb[0])) // 2, H - 101), cta_t, font=f_cta, fill="#FFFFFF")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def render_checklist_pin(post: dict, variant_idx: int, out_path: Path):
    theme = THEMES[variant_idx % len(THEMES)]
    img = Image.new("RGB", (W, H), theme["bg"])
    draw = ImageDraw.Draw(img)

    pad = 64
    draw.rounded_rectangle([pad, pad, W - pad, H - pad], radius=36, fill=theme["card"])
    draw.rounded_rectangle([pad + 48, pad + 48, pad + 200, pad + 60], radius=6, fill=theme["accent"])

    f_pill = load_font("bold", 26)
    cat_text = (post.get("categoryLabel") or post.get("category") or "ORGANIZATION").upper()
    tb = draw.textbbox((0, 0), cat_text, font=f_pill)
    pw = (tb[2] - tb[0]) + 44
    draw.rounded_rectangle([pad + 48, pad + 92, pad + 48 + pw, pad + 146], radius=27, fill=theme["pill_bg"])
    draw.text((pad + 70, pad + 104), cat_text, font=f_pill, fill=theme["accent"])

    variants = post.get("pinHooks") or [post["title"]]
    headline = variants[variant_idx % len(variants)]
    f_title = load_font("serif_bold" if variant_idx % 2 == 0 else "bold", 66)
    y = draw_wrapped(draw, headline, f_title, pad + 48, pad + 190, max_chars=20, fill=theme["ink"], line_spacing=1.18)

    y += 26
    draw.line([(pad + 48, y), (W - pad - 48, y)], fill=theme["pill_bg"], width=4)
    y += 40

    f_item = load_font("bold", 34)
    f_sub = load_font("regular", 25)
    picks = post.get("items", [])[:4]
    for idx, item in enumerate(picks, start=1):
        cx, cy = pad + 72, y + 22
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=theme["accent"])
        f_num = load_font("bold", 24)
        nb = draw.textbbox((0, 0), str(idx), font=f_num)
        draw.text((cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - 2), str(idx), font=f_num, fill="#FFFFFF")
        name_short = item["name"] if len(item["name"]) <= 38 else item["name"][:35] + "..."
        draw.text((pad + 112, y), name_short, font=f_item, fill=theme["ink"])
        draw.text((pad + 112, y + 46), item.get("badge", "Space-Saving Pick"), font=f_sub, fill=theme["muted"])
        y += 116
        if y > H - pad - 240:
            break

    cta_y = H - pad - 165
    draw.rounded_rectangle([pad + 48, cta_y, W - pad - 48, cta_y + 84], radius=42, fill=theme["accent"])
    f_cta = load_font("bold", 32)
    cta_text = "TAP TO SEE ALL PICKS  ->"
    cb = draw.textbbox((0, 0), cta_text, font=f_cta)
    draw.text(((W - (cb[2] - cb[0])) // 2, cta_y + 22), cta_text, font=f_cta, fill="#FFFFFF")

    f_brand = load_font("regular", 24)
    brand_domain = SITE_CONFIG["baseUrl"].replace("https://", "").replace("http://", "").rstrip("/")
    bb = draw.textbbox((0, 0), brand_domain, font=f_brand)
    draw.text(((W - (bb[2] - bb[0])) // 2, H - pad - 56), brand_domain, font=f_brand, fill=theme["muted"])

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

        for i in range(5):
            pin_path = OUT_DIR / slug / f"pin-{i + 1}.png"
            # Mix: 3 Photo-Backed Pins (using distinct backgrounds when -2/-3 exist) + 2 Checklist Pins
            if bgs and i < 3:
                bg_for_pin = bgs[i % len(bgs)]
                render_photo_pin(post, i, bg_for_pin, pin_path)
                pin_style = f"photo_{i + 1}"
            else:
                render_checklist_pin(post, i, pin_path)
                pin_style = f"checklist_{i + 1}"

            hook = hooks[i % len(hooks)]
            queue.append(
                {
                    "slug": slug,
                    "pin_index": i + 1,
                    "pin_style": pin_style,
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

    print(f"Generated {len(queue)} vertical 1000x1500 Pinterest Pins into {OUT_DIR}")


if __name__ == "__main__":
    main()
