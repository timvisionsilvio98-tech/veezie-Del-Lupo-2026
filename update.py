import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

# 1. PAROLE CHIAVE PER I MOTORI DI RICERCA
CHIAVI = [
    "film streaming gratis senza registrazione", 
    "guardare serie tv streaming ita gratis", 
    "altadefinizione nuovo indirizzo", 
    "cb01 nuovo dominio",
    "streamingcommunity nuovo indirizzo"
]

# 2. LISTE PUBBLICHE DA SACCHEGGIARE (GitHub, Pastenow, Pastebin, ecc.)
LISTE_SORGENTE = [
    "https://pastebin.com/raw/K7XgY8Yw",        # Esempio lista m3u/veezie comune
    "https://pastenow.ru/raw/",                  # Directory paste comuni
    "https://raw.githubusercontent.com/LuFrAnNa/Veezie/main/Lista", # Altre liste su GitHub
    "https://raw.githubusercontent.com/AlexS7/Lista-Veezie/main/lista.txt"
]

VIETATI = [
    "netflix", "primevideo", "disneyplus", "raiplay", "mediaset", "wikipedia", 
    "google", "youtube", "facebook", "instagram", "twitter", "tiktok", "amazon", 
    "apple", "github", "linkedin", "pinterest", "mymovies", "movieplayer", 
    "comingsoon", "imdb", "yahoo", "bing", "aranzulla", "computermagazine", 
    "telefonino", "webnews", "informarea", "giardiniblog", "infodrones", 
    "infotelematico", "soluzionecomputer", "chiccheinformatiche", "weareblog",
    "outofbit", "tuttotek", "breakingsocial", "lamenteemeravigliosa", "mojeek",
    "pastebin", "pastenow", "githubusercontent", "reddit", "telegram"
]

def estrai_dominio(link):
    if link and (link.startswith("http://") or link.startswith("https://")):
        # Pulizia da caratteri strani o rimasugli di liste m3u
        link = link.split()[0].split(",")[0].strip()
        try:
            dom = f"{urlparse(link).scheme}://{urlparse(link).netloc}".lower().replace("www.", "")
            if not any(v in dom for v in VIETATI) and len(dom) > 10:
                return dom
        except: pass
    return None

def cerca_e_ruba():
    siti = set()
    
    # Canali storici inseriti di base
    riserva = [
        "https://tantifilm.com", 
        "https://altadefinizione.tours", 
        "https://cb01.zone",
        "https://streamingcommunity.computer",
        "https://ilgeniodellostreaming.moe"
    ]
    for r in riserva:
        siti.add(r)

    # --- FASE 1: "RUBA" DALLE LISTE ESISTENTI ---
    for url_lista in LISTE_SORGENTE:
        try:
            r = requests.get(url_lista, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                # Trova qualsiasi cosa sembri un link HTTP/HTTPS dentro il testo della lista
                links = re.findall(r'(https?://[^\s,\"\']+)', r.text)
                for l in links:
                    d = estrai_dominio(l)
                    if d: siti.add(d)
        except: pass

    # --- FASE 2: SCANSIONE DEI MOTORI DI RICERCA ---
    for q in CHIAVI:
        query_formattata = q.replace(' ', '+')
        
        # Cerca su Mojeek
        try:
            r = requests.get(f"https://www.mojeek.com/search?q={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True, class_="ob"):
                    d = estrai_dominio(a['href'])
                    if d: siti.add(d)
        except: pass
        time.sleep(1)

        # Cerca su DuckDuckGo
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
        time.sleep(1)

    return siti

if __name__ == "__main__":
    risultati = cerca_e_ruba()
    with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
        for s in risultati:
            f.write(s + "\n")
            
