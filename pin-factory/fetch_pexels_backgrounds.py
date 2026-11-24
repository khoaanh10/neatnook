"""
Auto-fetch unique real interior photography backgrounds from Pexels API (Free)
so every Pin for the same article gets a distinct real background photo (Fresh Pin).

Usage:
  1. Get a free API key at https://www.pexels.com/api/
  2. Set PEXELS_API_KEY in .env or environment
  3. Run: python pin-factory/fetch_pexels_backgrounds.py
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

QUERY_BY_CATEGORY = {
    "kitchen": "organized small kitchen shelves modern",
    "desk": "minimalist wooden desk workspace calm",
    "apartment": "cozy minimalist apartment storage interior",
    "under-30": "home organization baskets shelves tidy",
}


def fetch_pexels(query: str, api_key: str, per_page: int = 6):
    params = urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": per_page})
    req = urllib.request.Request(
        f"https://api.pexels.com/v1/search?{params}",
        headers={"Authorization": api_key, "User-Agent": "NeatNookPinFactory/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8")).get("photos", [])


def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "NeatNookPinFactory/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())


def main():
    api_key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not api_key:
        print("Set PEXELS_API_KEY (free at https://www.pexels.com/api/) to auto-download real extra backgrounds.")
        sys.exit(0)

    BG_DIR.mkdir(parents=True, exist_ok=True)
    used_ids = set()

    for post_file in sorted(POSTS_DIR.glob("*.json")):
        post = json.loads(post_file.read_text(encoding="utf-8"))
        slug = post["slug"]
        cat = post.get("category", "apartment")
        query = post.get("pexelsQuery") or QUERY_BY_CATEGORY.get(cat, "minimalist home organization")
        photos = fetch_pexels(query, api_key, per_page=10)

        saved = 0
        for variant in (2, 3):
            dest = BG_DIR / f"{slug}-{variant}.jpg"
            if dest.exists():
                continue
            for p in photos:
                pid = p.get("id")
                if pid in used_ids:
                    continue
                img_url = (p.get("src") or {}).get("large2x") or (p.get("src") or {}).get("portrait")
                if not img_url:
                    continue
                download(img_url, dest)
                used_ids.add(pid)
                saved += 1
                print(f"Downloaded {dest.name} (Pexels #{pid})")
                break
        if saved == 0:
            print(f"Skipped {slug} (extra backgrounds already exist)")


if __name__ == "__main__":
    main()
