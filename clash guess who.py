#!/usr/bin/env python3
"""
download_card_images.py

Downloads official card art images from the Clash Royale Wiki (Fandom).
It scrapes each card's wiki page for the main og:image meta tag and saves the image
into ./images/<slugified-card-name>.png

Usage:
    python download_card_images.py

You can edit the CARDS list to add/remove card names.
"""

import os
import re
import requests
from urllib.parse import quote_plus

# Small set of cards used by the app — add more as needed
CARDS = [
    "Knight",
    "Archers",
    "Giant",
    "Baby Dragon",
    "Hog Rider",
    "Wizard",
    "Inferno Tower",
    "Balloon",
    "Electro Wizard",
    "Skeletons",
    "P.E.K.K.A",
    "Minions",
]

HEADERS = {
    "User-Agent": "ClashGuessWhoImageDownloader/1.0 (+https://example.com)"
}

OUT_DIR = "images"
WIKI_BASE = "https://clashroyale.fandom.com/wiki/"

def slugify(name: str) -> str:
    # create a filename friendly slug
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s

def find_og_image_url(html: str) -> str:
    # Look for og:image meta tag (common on fandom)
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if m:
        return m.group(1)
    # fallback: look for card image link patterns sometimes used
    m2 = re.search(r'(https://static\.wikia\.nocookie\.net/[^"\s]+/(?:revision|latest)[^"\s]+)', html)
    if m2:
        return m2.group(1)
    return None

def download_image(url: str, out_path: str):
    print(f"Downloading: {url}")
    r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(1024*8):
            if chunk:
                f.write(chunk)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for card in CARDS:
        page_url = WIKI_BASE + quote_plus(card.replace(" ", "_"))
        print(f"Fetching wiki page for '{card}': {page_url}")
        try:
            r = requests.get(page_url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except Exception as ex:
            print("  ERROR fetching page:", ex)
            continue

        img_url = find_og_image_url(r.text)
        if not img_url:
            print("  Could not find image on page, skipping.")
            continue

        filename = slugify(card) + os.path.splitext(img_url.split("?")[0])[-1]
        out_path = os.path.join(OUT_DIR, filename)
        try:
            download_image(img_url, out_path)
        except Exception as ex:
            print("  ERROR downloading image:", ex)
            continue

        print(f"Saved {card} -> {out_path}")

    print("Done. Images saved to the 'images' folder. If some cards are missing, try checking the card name/spelling or add other cards to CARDS list.")

if __name__ == "__main__":
    main()
