import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

# 1. PAROLE CHIAVE TOTALI PER CATTURARE I DOMINI NUOVI DAL WEB
CHIAVI_RICERCA = [
    "film streaming gratis senza registrazione 2026", 
    "guardare serie tv streaming ita gratis", 
    "altadefinizione nuovo indirizzo", 
    "cb01 nuovo dominio",
    "streamingcommunity nuovo indirizzo",
    "il genio dello streaming nuovo dominio",
    "tantifilm nuovo sito",
    "eurostreaming nuovo indirizzo",
    "filmpertutti nuovo dominio",
    "lista canali veezie aggiornata txt",
    "guardare film streaming gratis italiano"
]

# 2. TUTTE LE LISTE AUTOMATICHE VEEZIE ESISTENTI IN ITALIA DA SACCHEGGIARE
LISTE_VEEZIE_ITALIA = [
    "https://raw.githubusercontent.com/LuFrAnNa/Veezie/main/Lista",
    "https://raw.githubusercontent.com/AlexS7/Lista-Veezie/main/lista.txt",
    "https://raw.githubusercontent.com/pndazz/veezie/main/lista.txt",
    "https://raw.githubusercontent.com/Gisgand/veezie-channels/main/channels.txt",
    "https://raw.githubusercontent.com/mttvll/veezie-urls/main/urls.txt",
    "https://pastebin.com/raw/K7XgY8Yw",
    "https://raw.githubusercontent.com/Yand94/veezie-list/main/lista.txt",
    "https://raw.githubusercontent.com/Kuro-01/veezie-ita/main/lista"
]

# Filtro di protezione per cancellare giornali, blog e siti inutili
VIETATI = [
    "google", "youtube", "facebook", "instagram", "twitter", "tiktok", "amazon", "apple", "github", 
    "linkedin", "pinterest", "microsoft", "wikipedia", "w3.org", "schema", "reddit", "telegram",
    "mymovies", "movieplayer", "comingsoon", "imdb", "netflix", "primevideo", "disneyplus", "raiplay", 
    "mediaset", "chili", "rakuten", "sky", "nowtv", "paramount", "timvision",
    "aranzulla", "computermagazine", "telefonino", "webnews", "informarea", "giardiniblog", "infodrones", 
    "infotelematico", "soluzionecomputer", "chiccheinformatiche", "weareblog", "outofbit", "tuttotek", 
    "breakingsocial", "lamenteemeravigliosa", "mojeek", "yahoo", "bing", "msn", "libero", "virgilio", 
    "repubblica", "corriere", "gazzetta", "wired", "huffingtonpost", "ilfattoquotidiano", "tgcom24", 
    "tomshw", "hdblog", "everyeye", "multiplayer", "smartworld", "androidworld", "techzilla", "insidetechnology",
    "geek", "hardware", "software", "blog", "news", "magazine", "giornale", "forum", "guida", "trucchi",
    "pastebin", "pastenow", "githubusercontent", "hosting", "domain", "altervista", "wordpress", "blogger"
]

# Impronte digitali dei player e dei flussi video reali (film e serie tv)
IMPRONTE_VIDEO = [
    "mixdrop", "easybytez", "supervideo", "vidoza", "voe.sx", "streamtape", 
    "doodstream", "embed", "player", "video", "mp4", "m3u8", "streamhls", 
    "videomega", "faststream", "maxstream", "wstream", "iframe"
]

def estrai_e_pulisci(link):
    if link and (link.startswith("http://") or link.startswith("https://")):
        link = link.split()[0].split(",")[0].split('"')[0].strip()
        try:
            dom = f"{urlparse(link).scheme}://{urlparse(link).netloc}".lower().replace("www.", "")
            if any(v in dom for v in VIETATI):
                return None
            if len(dom) > 10:
                return dom
        except: pass
    return None

def ispeziona_sito_per_video(url):
    """Controlla l'HTML del sito: se ci sono player video, passa il test!"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            html = r.text.lower()
            if any(impronta in html for impronta in IMPRONTE_VIDEO):
                return url
    except: pass
    return None

def giga_scanner_totale():
    siti_potenziali = set()
    siti_certificati_cinema = set()

    # FASE 1: Saccheggio totale di TUTTE le liste Veezie automatiche in Italia
    for url in LISTE_VEEZIE_ITALIA:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                trovati = re.findall(r'(https?://[^\s,\"\']+)', r.text)
                for l in trovati:
                    dom = estrai_e_pulisci(l)
                    if dom: siti_potenziali.add(dom)
        except: pass

    # FASE 2: Scansione dei motori di ricerca per i domini nuovissimi
    for q in CHIAVI_RICERCA:
        query_formattata = q.replace(' ', '+')
        
        # Mojeek
        try:
            r = requests.get(f"https://www.mojeek.com/search?q={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True, class_="ob"):
                    dom = estrai_e_pulisci(a['href'])
                    if dom: siti_potenziali.add(dom)
        except: pass
        time.sleep(1.5)

        # DuckDuckGo
        try:
            r = requests.get(f"https://html.duckduckgo.com/html/?q={query_formattata}", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    m = re.search(r'uddg=(https?://[^&]+)', a['href'])
                    if m:
                        dom = estrai_e_pulisci(requests.utils.unquote(m.group(1)))
                        if dom: siti_potenziali.add(dom)
        except: pass
        time.sleep(1.5)

    # FASE 3: Ispezione profonda simultanea in parallelo (Multithreading accelerato a 15 canali)
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(ispeziona_sito_per_video, sito): sito for sito in siti_potenziali}
        for future in as_completed(futures):
            risultato = future.result()
            if risultato:
                siti_certificati_cinema.add(risultato)

    return siti_certificati_cinema

if __name__ == "__main__":
    risultati_finali = giga_scanner_totale()
    with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
        for s in risultati_finali:
            f.write(s + "\n")
            
