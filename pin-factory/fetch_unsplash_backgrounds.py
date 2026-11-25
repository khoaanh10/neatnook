"""
Auto-fetch unique real interior photography backgrounds from Unsplash API (Free)
so every Pin for the same article gets a distinct real background photo (Fresh Pin).

Usage:
  1. Set UNSPLASH_ACCESS_KEY in .env or environment
  2. Run: python pin-factory/fetch_unsplash_backgrounds.py
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "site" / "content" / "posts"
BG_DIR = Path(__file__).resolve().parent / "backgrounds"
ENV_FILE = ROOT / ".env"

QUERY_BY_SLUG = {
    "small-kitchen-under-sink-organizers": "organized kitchen cabinet shelves clean",
    "minimalist-desk-cable-management-under-30": "minimalist home office desk setup wood",
    "renter-friendly-no-drill-bathroom-storage": "minimalist small bathroom tidy shelves",
    "january-reset-fridge-pantry-organization": "organized kitchen pantry glass jars",
    "small-kitchen-countertop-declutter-ideas": "clean minimalist kitchen countertop wood",
    "tiny-apartment-entryway-storage-hacks": "minimalist apartment entryway wooden bench",
    "small-bathroom-vanity-counter-organizers": "spa bathroom vanity sink skincare tidy",
    "amazon-home-organization-finds-under-30": "minimalist living room shelves storage baskets",
    "calm-workspace-january-desk-reset-guide": "cozy calm wooden desk workspace plant",
    "small-closet-vertical-storage-hacks-renters": "organized minimalist wardrobe closet hangers",
}


def load_env_key(key: str) -> str:
    if os.environ.get(key):
        return os.environ[key].strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return ""


def search_unsplash(query: str, access_key: str, per_page: int = 8):
    params = urllib.parse.urlencode(
        {"query": query, "orientation": "portrait", "per_page": per_page, "content_filter": "high"}
    )
    req = urllib.request.Request(
        f"https://api.unsplash.com/search/photos?{params}",
        headers={
            "Authorization": f"Client-ID {access_key}",
            "Accept-Version": "v1",
            "User-Agent": "NeatNookPinFactory/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8")).get("results", [])


def trigger_download_event(download_location: str, access_key: str):
    if not download_location:
        return
    try:
        req = urllib.request.Request(
            download_location,
            headers={"Authorization": f"Client-ID {access_key}", "Accept-Version": "v1"},
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass


def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "NeatNookPinFactory/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())


def main():
    access_key = load_env_key("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("Set UNSPLASH_ACCESS_KEY in .env to auto-fetch real backgrounds.")
        sys.exit(1)

    BG_DIR.mkdir(parents=True, exist_ok=True)
    used_ids = set()
    total_saved = 0

    for post_file in sorted(POSTS_DIR.glob("*.json")):
        post = json.loads(post_file.read_text(encoding="utf-8"))
        slug = post["slug"]
        query = post.get("unsplashQuery") or QUERY_BY_SLUG.get(slug, "minimalist home organization")

        needed = []
        if not (BG_DIR / f"{slug}.jpg").exists() and not (BG_DIR / f"{slug}.png").exists():
            needed.append("")
        for v in ("-2", "-3"):
            if not (BG_DIR / f"{slug}{v}.jpg").exists():
                needed.append(v)
        if not needed:
            print(f"Skip {slug} (already has 3 backgrounds)")
            continue

        photos = search_unsplash(query, access_key, per_page=10)
        for suffix in needed:
            dest = BG_DIR / f"{slug}{suffix}.jpg"
            for p in photos:
                pid = p.get("id")
                if pid in used_ids:
                    continue
                img_url = (p.get("urls") or {}).get("regular")
                if not img_url:
                    continue
                download(img_url, dest)
                trigger_download_event((p.get("links") or {}).get("download_location"), access_key)
                used_ids.add(pid)
                total_saved += 1
                print(f"Downloaded {dest.name} (Unsplash #{pid})")
                break

    print(f"Done! Downloaded {total_saved} unique Unsplash interior backgrounds.")


if __name__ == "__main__":
    main()
