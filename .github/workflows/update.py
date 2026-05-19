import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
CHIAVI_RICERCA = ["film streaming gratis senza registrazione", "guardare serie tv streaming ita gratis", "altadefinizione nuovo indirizzo", "cb01 nuovo dominio"]
SITI_VIETATI = ["netflix", "primevideo", "disneyplus", "chili", "rakuten", "raiplay", "mediaset", "sky", "nowtv", "paramountplus", "google", "youtube", "wikipedia", "facebook", "instagram", "twitter", "tiktok", "mymovies", "movieplayer", "imdb", "comingsoon", "amazon", "apple", "github"]

def scansiona_il_web():
    sites = set()
    for q in CHIAVI_RICERCA:
        try:
            r = requests.get(f"https://html.duckduckgo.com/html/?q={q.replace(' ', '+')}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                for a in BeautifulSoup(r.text, 'html.parser').find_all('a', href=True):
                    m = re.search(r'uddg=(https?://[^&]+)', a['href'])
                    if m:
                        dom = f"{urlparse(requests.utils.unquote(m.group(1))).scheme}://{urlparse(requests.utils.unquote(m.group(1))).netloc}".lower().replace("www.", "")
                        if not any(v in dom for v in SITI_VIETATI): sites.add(dom)
            time.sleep(2)
        except: pass
    return sites

def filtra_canali(lista):
    validi = []
    for url in lista:
        try:
            r = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                u = r.url.rstrip('/').replace("www.", "")
                txt = r.text.lower()
                if "scopri i piani" in txt or "abbonamento" in txt: continue
                if any(p in txt for p in ["streaming", "altadefinizione", "cb01", "film gratis"]):
                    if u not in validi and not any(v in u for v in SITI_VIETATI): validi.append(u)
        except: pass
    return validi

if __name__ == "__main__":
    canali = filtra_canali(scansiona_il_web())
    with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
        for c in canali: f.write(c + "\n")
          
