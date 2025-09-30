import time
import json
import requests
from bs4 import BeautifulSoup

LINKS_FILE = "testlink.txt"
OUT_JSONL = "program_descriptions2.jsonl"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LLMcouse-chatbot/1.0)"}

# ---------------- Hjälpfunktioner ----------------

def normspace(s: str) -> str:
    import re
    return re.sub(r"\s+", " ", s or "").strip()

def get_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return normspace(h1.get_text(" ", strip=True))
    if soup.title:
        return normspace(soup.title.get_text(" ", strip=True))
    return ""

def extract_program_description(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    texts = []

    # 1️ Försök hitta innersta div (huvudbeskrivningen)
    primary = soup.select_one("div.sv-text-portlet.sv-use-margins.sv-skip-spacer")
    if primary:
        for el in primary.find_all(["p", "li", "h3"]):
            txt = el.get_text(" ", strip=True)
            if txt:
                texts.append(txt)

    # 2️ Fallback: yttercontainern om det inte hittades något
    if not texts:
        fallback = soup.select_one("div.sv-text-portlet-content")
        if fallback:
            for el in fallback.find_all(["p", "li", "h3"]):
                txt = el.get_text(" ", strip=True)
                if txt:
                    texts.append(txt)

    return " ".join(texts)

# ---------------- Körning ----------------

with open(LINKS_FILE, "r", encoding="utf-8") as f:
    urls = [normspace(line) for line in f if line.strip()]

rows = []
for i, url in enumerate(urls, 1):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        title = get_title(soup)
        description = extract_program_description(url, r.text)

        print(f"\n=== {i}. {url} ===")
        print(f"TITLE: {title}")
        print(f"DESCRIPTION (first 200 chars): {description[:200]}")

        rows.append({"url": url, "title": title, "description": description})
    except Exception as e:
        print(f" ERROR {i}. {url}: {e}")
        rows.append({"url": url, "title": "", "description": f"ERROR: {e}"})

    time.sleep(0.7)  # snäll mot servern

# spara JSONL
with open(OUT_JSONL, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"\n Sparade {len(rows)} program till {OUT_JSONL}")