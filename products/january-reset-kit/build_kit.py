"""
NeatNook Digital Product Builder:
Generates a 12-page print-ready US Letter PDF:
  "The January Apartment Reset Kit + 72 Minimalist Pantry & Fridge Labels"
Plus a 1280x720 Gumroad cover mockup image using the real rendered pages.
"""
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent / "dist"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# US Letter at 150 DPI -> crisp, fast, lightweight (~3-5MB total)
PW, PH = 1275, 1650

BG = "#FDFCF9"
TINT = "#F5F1EA"
INK = "#1A1917"
BODY = "#3A3631"
MUTED = "#6E685F"
RULE = "#DDD6CA"
ACCENT = "#2C4A3E"
WARM = "#A65336"


def font(style: str, size: int):
    paths = {
        "serif_b": [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\timesbd.ttf"],
        "serif_i": [r"C:\Windows\Fonts\georgiai.ttf", r"C:\Windows\Fonts\timesi.ttf"],
        "serif": [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\times.ttf"],
        "sans_b": [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
        "sans": [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"],
    }
    for p in paths[style]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def new_page(title_kicker: str = "", page_num: int = 0):
    img = Image.new("RGB", (PW, PH), BG)
    d = ImageDraw.Draw(img)
    if title_kicker:
        d.text((88, 62), title_kicker.upper(), font=font("sans_b", 20), fill=WARM)
        d.text((PW - 260, 62), "NEATNOOK", font=font("serif_b", 22), fill=INK)
        d.line([(88, 102), (PW - 88, 102)], fill=RULE, width=2)
    if page_num > 0:
        d.line([(88, PH - 96), (PW - 88, PH - 96)], fill=RULE, width=2)
        d.text((88, PH - 78), "The January Apartment Reset Kit  |  For personal use only", font=font("sans", 18), fill=MUTED)
        pt = f"Page {page_num}"
        tb = d.textbbox((0, 0), pt, font=font("sans", 18))
        d.text((PW - 88 - (tb[2] - tb[0]), PH - 78), pt, font=font("sans", 18), fill=MUTED)
    return img, d


def draw_checkbox(d, x, y, size=24):
    d.rounded_rectangle([x, y, x + size, y + size], radius=4, outline=ACCENT, width=2)


def make_cover():
    img = Image.new("RGB", (PW, PH), "#F4EFE6")
    d = ImageDraw.Draw(img)
    d.rectangle([54, 54, PW - 54, PH - 54], fill=BG, outline=RULE, width=3)
    d.rectangle([54, 54, PW - 54, 72], fill=ACCENT)

    d.text((120, 150), "NEATNOOK  ·  PRINTABLE EDITION", font=font("sans_b", 24), fill=WARM)
    d.line([(120, 198), (360, 198)], fill=WARM, width=4)

    f_h1 = font("serif_b", 96)
    y = 250
    for line in ["The January", "Apartment", "Reset Kit"]:
        d.text((120, y), line, font=f_h1, fill=INK)
        y += 116

    f_sub = font("sans", 32)
    y += 28
    for line in textwrap.wrap(
        "A calm, renter-friendly 30-day declutter plan, room-by-room reset checklists, cabinet measurement cards, and 72 printable minimalist pantry & fridge labels.",
        width=48,
    ):
        d.text((120, y), line, font=f_sub, fill=MUTED)
        y += 48

    # What's inside box
    box_top = 860
    d.rounded_rectangle([120, box_top, PW - 120, box_top + 480], radius=16, fill=TINT)
    d.text((168, box_top + 42), "WHAT'S INSIDE THIS 12-PAGE KIT", font=font("sans_b", 22), fill=ACCENT)
    d.line([(168, box_top + 82), (PW - 168, box_top + 82)], fill=RULE, width=2)

    inside = [
        ("01", "30-Day January Reset Calendar — 15-minute daily micro-tasks"),
        ("02", "Small Kitchen & Under-Sink Reset + Cabinet Measuring Card"),
        ("03", "Calm Desk, Cable Management & 2-Minute Shutdown Ritual"),
        ("04", "Tiny Bathroom & No-Drill Closet Reset Checklists"),
        ("05", "Weekly 15-Minute Maintenance & Pantry Restock Tracker"),
        ("06", "72 Printable Minimalist Labels (Pantry, Fridge, Spices & Cleaning)"),
    ]
    iy = box_top + 114
    for num, desc in inside:
        d.text((168, iy), num, font=font("serif_i", 28), fill=WARM)
        d.text((228, iy + 2), desc, font=font("sans", 25), fill=INK)
        iy += 56

    d.text((120, PH - 160), "US LETTER (8.5 x 11 IN)  ·  PRINT ON PLAIN OR FULL-SHEET STICKER PAPER", font=font("sans_b", 20), fill=MUTED)
    return img


def make_30_day_calendar():
    img, d = new_page("30-Day Declutter Plan", 2)
    d.text((88, 128), "30-Day January Apartment Reset", font=font("serif_b", 52), fill=INK)
    d.text((88, 198), "One 15-minute task per day. Check off each box as you reclaim calm in your space.", font=font("sans", 24), fill=MUTED)

    tasks = [
        "Clear kitchen counters completely", "Toss expired fridge condiments", "Wipe & line under-sink cabinet",
        "Sort utensil & cutlery drawer", "Group baking & dry pantry goods", "Match & purge Tupperware lids",
        "Wipe microwave & coffee zone", "Clear desktop to bare wood", "Hide power strip & loose cables",
        "Sort desk drawers & pens", "Delete 200 phone screenshots", "Create daily top-3 notepad zone",
        "Purge expired bathroom skincare", "Organize vanity sink ledge", "Fold & stack bath towels neatly",
        "Check medicine & first-aid box", "Wipe shower caddy & bottles", "Clear entryway shoe pile",
        "Create key & mail drop zone", "Sort winter coats & tote bags", "Pull out 10 unworn closet items",
        "Switch to uniform slim hangers", "Fold sweaters into vertical stacks", "Organize socks & undergarments",
        "Pack off-season items under bed", "Clear nightstand & cords", "Sort junk drawer & batteries",
        "Wipe light switches & handles", "Label pantry & fridge bins", "15-min whole-home calm walk"
    ]

    cols, rows = 5, 6
    margin_x = 88
    start_y = 266
    gap = 16
    cw = (PW - margin_x * 2 - gap * (cols - 1)) // cols
    ch = 196

    for idx, task in enumerate(tasks):
        r, c = divmod(idx, cols)
        x = margin_x + c * (cw + gap)
        y = start_y + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=10, fill="#FFFFFF", outline=RULE, width=2)
        d.text((x + 16, y + 14), f"DAY {idx + 1:02d}", font=font("sans_b", 18), fill=WARM)
        draw_checkbox(d, x + cw - 38, y + 14, size=22)
        d.line([(x + 14, y + 48), (x + cw - 14, y + 48)], fill=TINT, width=2)
        ty = y + 62
        for line in textwrap.wrap(task, width=16):
            d.text((x + 16, ty), line, font=font("sans", 20), fill=INK)
            ty += 28
    return img


def make_checklist_page(kicker, title, subtitle, sections, bottom_box_title, bottom_lines, page_num):
    img, d = new_page(kicker, page_num)
    d.text((88, 128), title, font=font("serif_b", 48), fill=INK)
    d.text((88, 194), subtitle, font=font("sans", 23), fill=MUTED)

    y = 264
    for sec_title, items in sections:
        d.rounded_rectangle([88, y, PW - 88, y + 44], radius=6, fill=TINT)
        d.text((108, y + 8), sec_title.upper(), font=font("sans_b", 20), fill=ACCENT)
        y += 62
        for item in items:
            draw_checkbox(d, 96, y + 3, size=24)
            d.text((136, y), item, font=font("sans", 23), fill=BODY)
            y += 44
        y += 18

    # Bottom utility card
    by = max(y + 12, 1170)
    d.rounded_rectangle([88, by, PW - 88, PH - 132], radius=12, fill="#FFFFFF", outline=ACCENT, width=2)
    d.text((118, by + 24), bottom_box_title.upper(), font=font("sans_b", 21), fill=ACCENT)
    ly = by + 68
    for line in bottom_lines:
        d.text((118, ly), line, font=font("sans", 22), fill=BODY)
        ly += 44
    return img


def make_label_sheet(sheet_title: str, labels: list[tuple[str, str]], page_num: int):
    img, d = new_page(f"Printable Labels  ·  {sheet_title}", page_num)
    d.text((88, 124), f"Minimalist Labels: {sheet_title}", font=font("serif_b", 42), fill=INK)
    d.text((88, 180), "Print on full-sheet matte sticker paper (8.5 x 11 in) and trim along the light outer guide.", font=font("sans", 21), fill=MUTED)

    cols, rows = 2, 6
    mx = 88
    sy = 236
    gx, gy = 36, 26
    lw = (PW - mx * 2 - gx) // 2
    lh = 186

    for idx, (main_txt, sub_txt) in enumerate(labels[:12]):
        r, c = divmod(idx, cols)
        x = mx + c * (lw + gx)
        y = sy + r * (lh + gy)
        # Outer cut guide
        d.rectangle([x, y, x + lw, y + lh], fill="#FFFFFF", outline="#C9C2B6", width=2)
        # Inner decorative frame
        d.rectangle([x + 14, y + 14, x + lw - 14, y + lh - 14], outline=INK, width=2)
        d.line([(x + lw // 2 - 42, y + 116), (x + lw // 2 + 42, y + 116)], fill=WARM, width=2)

        f_m = font("serif_b", 38 if len(main_txt) <= 15 else 31)
        mb = d.textbbox((0, 0), main_txt, font=f_m)
        d.text((x + (lw - (mb[2] - mb[0])) // 2, y + 48), main_txt, font=f_m, fill=INK)

        f_s = font("sans_b", 16)
        st = sub_txt.upper()
        sb = d.textbbox((0, 0), st, font=f_s)
        d.text((x + (lw - (sb[2] - sb[0])) // 2, y + 132), st, font=f_s, fill=MUTED)

    return img


def make_gumroad_cover(pages):
    CW, CH = 1280, 720
    cov = Image.new("RGB", (CW, CH), "#EDE7DC")
    d = ImageDraw.Draw(cov)
    d.rectangle([0, 0, CW, 12], fill=ACCENT)

    # Left typography column
    d.text((68, 72), "INSTANT DIGITAL DOWNLOAD  ·  12 PAGES", font=font("sans_b", 20), fill=WARM)
    y = 120
    for line in ["The January", "Apartment", "Reset Kit"]:
        d.text((68, y), line, font=font("serif_b", 66), fill=INK)
        y += 76

    y += 18
    bullets = [
        "30-Day 15-Minute Declutter Calendar",
        "Room-by-Room Renter Checklists",
        "72 Minimalist Pantry & Fridge Labels",
        "US Letter Print-Ready PDF (8.5 x 11\")",
    ]
    for b in bullets:
        d.ellipse([70, y + 10, 82, y + 22], fill=ACCENT)
        d.text((98, y), b, font=font("sans", 24), fill=BODY)
        y += 42

    d.rounded_rectangle([68, CH - 110, 380, CH - 52], radius=29, fill=INK)
    d.text((112, CH - 95), "NEATNOOK EDITION", font=font("sans_b", 20), fill="#FFFFFF")

    # Right side: 3 crisp fanned page previews
    previews = [
        (pages[6], (920, 120), 6, 300),
        (pages[1], (760, 100), -5, 320),
        (pages[0], (600, 78), 0, 355),
    ]
    for pg, pos, angle, target_w in previews:
        th = int(target_w * (PH / PW))
        thumb = pg.resize((target_w, th), Image.Resampling.LANCZOS)
        bordered = Image.new("RGBA", (target_w + 16, th + 16), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bordered)
        bd.rectangle([8, 8, target_w + 14, th + 14], fill=(20, 18, 16, 48))
        bordered.paste(thumb, (0, 0))
        if angle != 0:
            bordered = bordered.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        cov.paste(bordered, pos, bordered)

    cov.save(OUT_DIR / "cover-january-reset-kit.png", "PNG", optimize=True)


def main():
    pages = []
    pages.append(make_cover())
    pages.append(make_30_day_calendar())

    pages.append(
        make_checklist_page(
            "Small Kitchen & Under-Sink",
            "Kitchen & Under-Sink Reset",
            "Clear counters and maximize vertical cabinet space in under 45 minutes.",
            [
                ("1. Countertop Declutter", [
                    "Remove everything from counters; wipe backsplash and corners clean",
                    "Keep only daily-use essentials (coffee maker, dish caddy, salt/oil)",
                    "Move knives to a magnetic strip and drying dishes to a roll-up sink rack",
                ]),
                ("2. Under-Sink Cabinet Zone", [
                    "Empty cabinet completely and check pipes for slow leaks",
                    "Lay down a waterproof silicone drip mat to protect wood",
                    "Place L-shaped 2-tier pull-out shelf beside the drain pipe",
                    "Hang daily spray bottles on an expandable tension rod",
                    "Group sponges, pods, and trash bags in clear handled bins",
                ]),
            ],
            "Measure Before You Buy (Cabinet Card)",
            [
                "Interior Width: ______ in    |    Interior Depth: ______ in",
                "Left of Pipe: ______ in      |    Right of Pipe: ______ in",
                "Floor to Sink Bottom: ______ in   (Leave 1\" clearance for door hinges!)",
            ],
            3,
        )
    )

    pages.append(
        make_checklist_page(
            "Calm Workspace & Desk",
            "Minimalist Desk & Cable Reset",
            "Build a distraction-free work zone that switches off cleanly at 5 PM.",
            [
                ("1. Cable & Tech Cleanup", [
                    "Unplug every cord, wipe desktop, and remove unused adapters",
                    "Mount a clamp-on under-desk tray for your power strip & bricks",
                    "Snap daily charging cords into magnetic edge clips",
                    "Stand closed laptops vertically or use a monitor riser with drawer",
                ]),
                ("2. Daily 2-Minute Shutdown Ritual", [
                    "Clear mugs, glasses, and loose papers off the desk mat",
                    "Tuck notebooks & headphones into under-desk storage",
                    "Write tomorrow's Top 3 Priorities on your desktop whiteboard",
                    "Switch monitor light bar to warm evening mode",
                ]),
            ],
            "Top 3 Focus Priorities (Weekly Template)",
            [
                "Priority 1: ________________________________________________",
                "Priority 2: ________________________________________________",
                "Priority 3: ________________________________________________",
            ],
            4,
        )
    )

    pages.append(
        make_checklist_page(
            "Bathroom & Tiny Closet",
            "No-Drill Bathroom & Closet Reset",
            "Renter-friendly vertical upgrades that protect your security deposit.",
            [
                ("1. Small Bathroom Spa Reset", [
                    "Toss expired skincare, half-empty samples, and dried-out products",
                    "Group daily skincare on a 360-degree rotating tray or 2-tier stand",
                    "Decant cotton swabs & pads into lidded apothecary jars",
                    "Mount rustproof adhesive corner caddies for shower bottles",
                    "Roll extra towels vertically on an over-the-toilet rack",
                ]),
                ("2. Tiny Closet Double-Space Method", [
                    "Pull out anything unworn in the past 12 months to donate",
                    "Swap bulky hangers for uniform ultra-thin velvet hangers",
                    "Add a clip-on double-hang rod extender for shirts & pants",
                    "Store off-season sweaters in breathable under-bed bags",
                ]),
            ],
            "The 1-In, 1-Out Apartment Rule",
            [
                "Whenever a new item enters your closet or bathroom, donate or recycle",
                "one older item the same week. Keep a small donation bag on the closet",
                "floor so decluttering stays automatic all year long.",
            ],
            5,
        )
    )

    pages.append(
        make_checklist_page(
            "Weekly Maintenance",
            "15-Minute Sunday Home Reset",
            "Keep your apartment effortlessly tidy all year without marathon cleanings.",
            [
                ("1. Quick 15-Minute Loop", [
                    "Min 01–03: Clear kitchen sink, wipe counters & stove top",
                    "Min 04–06: Scan fridge for leftovers & wipe one sticky shelf",
                    "Min 07–09: Reset desk surface, coil cords & empty small bins",
                    "Min 10–12: Straighten entryway shoes, coats & mail drop zone",
                    "Min 13–15: Wipe bathroom sink, swap hand towel & take out trash",
                ]),
                ("2. Running Restock List (Check Before Shopping)", [
                    "Kitchen: Dish soap · Sponges · Trash bags · Paper towels · Olive oil",
                    "Pantry: Oats · Rice · Pasta · Coffee · Flour · Cooking spray",
                    "Bathroom: Hand soap · Cotton pads · Toilet paper · Toothpaste",
                ]),
            ],
            "Custom Notes & Next Upgrade Goals",
            [
                "Zone to upgrade next: _______________________________________",
                "Measurements / Notes: _______________________________________",
                "Budget cap: $________    Target Date: _______________________",
            ],
            6,
        )
    )

    label_sheets = [
        ("Baking & Grains", [
            ("All-Purpose Flour", "Pantry Staple"), ("Whole Wheat Flour", "Baking"),
            ("Granulated Sugar", "Baking"), ("Brown Sugar", "Keep Airtight"),
            ("Powdered Sugar", "Baking"), ("Rolled Oats", "Breakfast"),
            ("Baking Soda", "Baking"), ("Baking Powder", "Baking"),
            ("Cornstarch", "Pantry"), ("Cocoa Powder", "Baking"),
            ("Chocolate Chips", "Baking"), ("Breadcrumbs", "Pantry"),
        ]),
        ("Pasta, Rice & Dry Goods", [
            ("Jasmine Rice", "Grains"), ("Brown Rice", "Grains"),
            ("Quinoa", "Grains"), ("Spaghetti", "Pasta"),
            ("Penne Pasta", "Pasta"), ("Macaroni", "Pasta"),
            ("Red Lentils", "Legumes"), ("Black Beans", "Legumes"),
            ("Chickpeas", "Legumes"), ("Couscous", "Grains"),
            ("Chia Seeds", "Superfoods"), ("Flax Seeds", "Superfoods"),
        ]),
        ("Spices & Herbs", [
            ("Sea Salt", "Everyday"), ("Black Pepper", "Everyday"),
            ("Garlic Powder", "Seasoning"), ("Onion Powder", "Seasoning"),
            ("Smoked Paprika", "Spice"), ("Ground Cumin", "Spice"),
            ("Italian Herbs", "Blend"), ("Chili Flakes", "Heat"),
            ("Cinnamon", "Sweet Spice"), ("Dried Oregano", "Herb"),
            ("Turmeric", "Spice"), ("Curry Powder", "Blend"),
        ]),
        ("Breakfast, Coffee & Snacks", [
            ("Coffee Beans", "Morning"), ("Ground Coffee", "Morning"),
            ("Green Tea", "Tea Bar"), ("Herbal Tea", "Tea Bar"),
            ("Granola", "Breakfast"), ("Cereal", "Breakfast"),
            ("Almonds", "Nuts & Seeds"), ("Walnuts", "Nuts & Seeds"),
            ("Trail Mix", "Snacks"), ("Crackers", "Snacks"),
            ("Popcorn Kernels", "Snacks"), ("Dried Fruit", "Snacks"),
        ]),
        ("Fridge & Produce Zones", [
            ("Fresh Produce", "Eat First"), ("Leafy Greens", "Crisper"),
            ("Berries & Fruit", "Wash & Drain"), ("Dairy & Cheese", "Cold Zone"),
            ("Eggs", "Middle Shelf"), ("Condiments", "Door / Turntable"),
            ("Beverages", "Chilled"), ("Meal Prep", "Ready to Eat"),
            ("Leftovers", "Eat Within 3 Days"), ("Snacks & Grab", "Quick Access"),
            ("Meat & Protein", "Bottom Shelf"), ("Freezer Backups", "Frozen"),
        ]),
        ("Under-Sink & Home Care", [
            ("Dishwasher Pods", "Under Sink"), ("Sponges & Brushes", "Kitchen"),
            ("Trash Bags", "Refills"), ("All-Purpose Spray", "Cleaning"),
            ("Microfiber Cloths", "Cleaning"), ("Laundry Pods", "Utility"),
            ("Extra Soap", "Backups"), ("Paper Towels", "Refills"),
            ("First Aid", "Bathroom"), ("Cotton Swabs", "Vanity"),
            ("Travel Minis", "Bathroom"), ("Batteries & Cords", "Utility"),
        ]),
    ]

    for idx, (stitle, slabels) in enumerate(label_sheets, start=7):
        pages.append(make_label_sheet(stitle, slabels, idx))

    pdf_path = OUT_DIR / "NeatNook-January-Apartment-Reset-Kit.pdf"
    pages[0].save(
        pdf_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=pages[1:],
    )
    make_gumroad_cover(pages)
    print(f"Built {len(pages)}-page PDF: {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
    print(f"Built Gumroad cover: {OUT_DIR / 'cover-january-reset-kit.png'}")


if __name__ == "__main__":
    main()
