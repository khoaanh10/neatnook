import csv
import json
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE_CONFIG = json.loads((ROOT / "site" / "site.config.json").read_text(encoding="utf-8"))
POSTS_DIR = ROOT / "site" / "content" / "posts"
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


def render_pin(post: dict, variant_idx: int, out_path: Path):
    theme = THEMES[variant_idx % len(THEMES)]
    img = Image.new("RGB", (W, H), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Outer editorial card
    pad = 64
    draw.rounded_rectangle(
        [pad, pad, W - pad, H - pad],
        radius=36,
        fill=theme["card"],
    )

    # Top accent bar
    draw.rounded_rectangle(
        [pad + 48, pad + 48, pad + 200, pad + 60],
        radius=6,
        fill=theme["accent"],
    )

    # Category pill
    f_pill = load_font("bold", 26)
    cat_text = (post.get("categoryLabel") or post.get("category") or "ORGANIZATION").upper()
    tb = draw.textbbox((0, 0), cat_text, font=f_pill)
    pw = (tb[2] - tb[0]) + 44
    draw.rounded_rectangle(
        [pad + 48, pad + 92, pad + 48 + pw, pad + 146],
        radius=27,
        fill=theme["pill_bg"],
    )
    draw.text((pad + 70, pad + 104), cat_text, font=f_pill, fill=theme["accent"])

    # Pin headline variant
    variants = post.get("pinHooks") or [post["title"]]
    headline = variants[variant_idx % len(variants)]
    f_title = load_font("serif_bold" if variant_idx % 2 == 0 else "bold", 68)
    y = draw_wrapped(
        draw,
        headline,
        f_title,
        pad + 48,
        pad + 190,
        max_chars=20,
        fill=theme["ink"],
        line_spacing=1.18,
    )

    # Divider line
    y += 26
    draw.line([(pad + 48, y), (W - pad - 48, y)], fill=theme["pill_bg"], width=4)
    y += 40

    # Top 4 preview picks as scannable checklist
    f_item = load_font("bold", 34)
    f_sub = load_font("regular", 25)
    picks = post.get("items", [])[:4]
    for idx, item in enumerate(picks, start=1):
        # Number circle
        cx, cy = pad + 72, y + 22
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=theme["accent"])
        f_num = load_font("bold", 24)
        nb = draw.textbbox((0, 0), str(idx), font=f_num)
        draw.text(
            (cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - 2),
            str(idx),
            font=f_num,
            fill="#FFFFFF",
        )
        name_short = item["name"] if len(item["name"]) <= 38 else item["name"][:35] + "..."
        draw.text((pad + 112, y), name_short, font=f_item, fill=theme["ink"])
        badge = item.get("badge", "Space-Saving Pick")
        draw.text((pad + 112, y + 46), badge, font=f_sub, fill=theme["muted"])
        y += 116
        if y > H - pad - 240:
            break

    # Bottom CTA pill & brand footer
    cta_y = H - pad - 165
    draw.rounded_rectangle(
        [pad + 48, cta_y, W - pad - 48, cta_y + 84],
        radius=42,
        fill=theme["accent"],
    )
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
        num_pins = max(5, len(hooks))

        for i in range(5):
            pin_path = OUT_DIR / slug / f"pin-{i + 1}.png"
            render_pin(post, i, pin_path)
            hook = hooks[i % len(hooks)]
            queue.append(
                {
                    "slug": slug,
                    "pin_index": i + 1,
                    "image_path": str(pin_path),
                    "board": post.get("pinterestBoard", "Small Kitchen Organization Ideas"),
                    "pin_title": hook[:100],
                    "pin_description": f"{post['metaDescription']} Tap to see all {len(post['items'])} renter-friendly picks on {SITE_CONFIG['siteName']}."[:500],
                    "alt_text": f"{hook} — checklist of practical small-space organization picks",
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
