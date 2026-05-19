import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
CHIAVI = ["film streaming gratis senza registrazione", "guardare serie tv streaming ita gratis", "altadefinizione nuovo indirizzo", "cb01 nuovo dominio"]
VIETATI = ["netflix", "primevideo", "disneyplus", "raiplay", "mediaset", "wikipedia", "google", "youtube", "mymovies", "movieplayer"]

def cerca():
    siti = set()
    # Canali stabili di riserva per non lasciare mai il file vuoto
    riserva = ["https://tantifilm.com", "https://altadefinizione.tours", "https://cb01.zone"]
    for r in riserva:
        siti.add(r)

    for q in CHIAVI:
        try:
            url = f"https://html.duckduckgo.com/html/?q={q.replace(' ', '+')}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    m = re.search(r'uddg=(https?://[^&]+)', a['href'])
                    if m:
                        link = requests.utils.unquote(m.group(1))
                        dom = f"{urlparse(link).scheme}://{urlparse(link).netloc}".lower().replace("www.", "")
                        if not any(v in dom for v in VIETATI) and len(dom) > 10:
                            siti.add(dom)
            time.sleep(1)
        except:
            pass
    return siti

if __name__ == "__main__":
    risultati = cerca()
    with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
        for s in risultati:
            f.write(s + "\n")
            
