import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

CHIAVI = [
    "film streaming gratis senza registrazione", 
    "guardare serie tv streaming ita gratis", 
    "altadefinizione nuovo indirizzo", 
    "cb01 nuovo dominio",
    "lista canali veezie aggiornata",
    "siti film streaming gratis italiano",
    "streamingcommunity nuovo indirizzo",
    "il genio dello streaming nuovo dominio"
]

# Filtro potenziato per eliminare blog, notizie e motori di ricerca inutili per Veezie
VIETATI = [
    "netflix", "primevideo", "disneyplus", "raiplay", "mediaset", "wikipedia", 
    "google", "youtube", "facebook", "instagram", "twitter", "tiktok", "amazon", 
    "apple", "github", "linkedin", "pinterest", "mymovies", "movieplayer", 
    "comingsoon", "imdb", "yahoo", "bing", "aranzulla", "computermagazine", 
    "telefonino", "webnews", "informarea", "giardiniblog", "infodrones", 
    "infotelematico", "soluzionecomputer", "chiccheinformatiche", "weareblog",
    "outofbit", "tuttotek", "breakingsocial", "lamenteemeravigliosa", "mojeek"
]

def estrai_dominio(link):
    if link and link.startswith("http"):
        dom = f"{urlparse(link).scheme}://{urlparse(link).netloc}".lower().replace("www.", "")
        if not any(v in dom for v in VIETATI) and len(dom) > 10:
            return dom
    return None

def cerca_multi_provider():
    siti = set()
    
    # I pilastri fondamentali dello streaming in Italia inseriti di base
    riserva = [
        "https://tantifilm.com", 
        "https://altadefinizione.tours", 
        "https://cb01.zone",
        "https://streamingcommunity.computer",
        "https://ilgeniodellostreaming.moe"
    ]
    for r in riserva:
        siti.add(r)

    for q in CHIAVI:
        query_formattata = q.replace(' ', '+')
        
        # PROVIDER 1: MOJEEK
        try:
            r = requests.get(f"https://www.mojeek.com/search?q={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True, class_="ob"):
                    d = estrai_dominio(a['href'])
                    if d: siti.add(d)
        except: pass
        time.sleep(1.5)

        # PROVIDER 2: DUCKDUCKGO LITE / HTML
        try:
            r = requests.get(f"https://html.duckduckgo.com/html/?q={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    m = re.search(r'uddg=(https?://[^&]+)', a['href'])
                    if m:
                        d = estrai_dominio(requests.utils.unquote(m.group(1)))
                        if d: siti.add(d)
        except: pass
        time.sleep(1.5)

        # PROVIDER 3: YAHOO
        try:
            r = requests.get(f"https://it.search.yahoo.com/search?p={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = a['href']
                    if "RU=" in link:
                        m = re.search(r'RU=([^/]+)', link)
                        if m:
                            link = requests.utils.unquote(m.group(1))
                    d = estrai_dominio(link)
                    if d: siti.add(d)
        except: pass
        time.sleep(1.5)

    return siti

if __name__ == "__main__":
    risultati = cerca_multi_provider()
    with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
        for s in risultati:
            f.write(s + "\n")
            
