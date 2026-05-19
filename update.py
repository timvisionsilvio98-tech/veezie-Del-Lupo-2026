import urllib.request
import urllib.parse
import re
import ssl
import time
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# 1. CACCIA BASATA SUI PLAYER: Cerchiamo nel web i siti che contengono queste impronte nei testi/codici
QUERIES_PLAYER = [
    'film streaming gratis "streamtape" OR "mixdrop"',
    'guarda serie tv gratis "voe.sx" OR "doodstream"',
    'streaming ita "filemoon" OR "supervideo"',
    'film gratis senza registrazione "vidguard" OR "vidoza"',
    'lista canali veezie "m3u8" OR "wstream"'
]

# Filtro di protezione per evitare di infilare nella lista colossi o blog inutili
VIETATI = [
    "google", "youtube", "facebook", "instagram", "twitter", "github", "wikipedia", "amazon", "apple",
    "linkedin", "pinterest", "microsoft", "reddit", "telegram", "aranzulla", "mojeek", "bing", "yahoo",
    "mymovies", "movieplayer", "comingsoon", "imdb", "netflix", "primevideo", "disneyplus", "raiplay",
    "gazzetta", "repubblica", "corriere", "wired", "everyeye", "multiplayer", "hdblog", "android"
]

# Tutti i player da verificare dentro i siti scovati per confermare che siano di streaming cinema
IMPRONTE_VIDEO = [
    "mixdrop", "streamtape", "voe", "voe.sx", "doodstream", "dood", "supervideo", 
    "vidoza", "easybytez", "wstream", "faststream", "maxstream", "videomega",
    "filemoon", "vidguard", "vidsrc", "embedwish", "lulustream", "streamsb", 
    "sbembed", "streamhide", "vidhide", "player", "embed", "iframe", "video", 
    "source src", "type=", "video/mp4", "m3u8", "m3u"
]

def ottieni_contesto_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def cerca_siti_tramite_player(query):
    """Scava su Mojeek cercando le impronte dei player lasciate dai siti di streaming"""
    siti_trovati = set()
    try:
        query_encoded = urllib.parse.quote_plus(query)
        url = f"https://www.mojeek.com/search?q={query_encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith("http"):
                    netloc = urllib.parse.urlparse(href).netloc.lower().replace("www.", "")
                    if netloc and not any(v in netloc for v in VIETATI) and len(netloc) > 8:
                        siti_trovati.add(f"https://{netloc}")
    except Exception as e:
        print(f"   ⚠️ Errore di ricerca: {str(e)}")
    return siti_trovati

def verifica_presenza_player(url):
    """Entra nel codice del sito scovato e verifica se ospita davvero un player video"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=7) as response:
            html = response.read().decode('utf-8', errors='ignore').lower()
            if any(impronta in html for impronta in IMPRONTE_VIDEO):
                print(f"🔥 SITO INEDITO CERTIFICATO (Trovato Player): {url}")
                return url
        print(f"❌ SCARTATO (Nessun player attivo): {url}")
    except:
        pass
    return None

if __name__ == "__main__":
    print("🐺 LUPOBOT 2026: Avvio scansione globale basata sulle impronte dei Player Video... 🐺")
    
    domini_grezzi = set()
    lista_lupo_finale = set()
    
    # FASE 1: Interrogazione del web usando i player come parole chiave
    for query in QUERIES_PLAYER:
        print(f"🔍 Ricerca sul web con esca: '{query}'")
        risultati = cerca_siti_tramite_player(query)
        domini_grezzi.update(risultati)
        print(f"   -> Domini grezzi accumulati finora: {len(domini_grezzi)}")
        time.sleep(2.5) # Pausa strategica anti-capcha
        
    print(f"\n📊 FINE RACCOLTA WEB: Trovati {len(domini_grezzi)} potenziali candidati da ispezionare.")
    
    # FASE 2: Ispezione del codice sorgente di ogni sito trovato
    if domini_grezzi:
        print("\n🧬 Inizio analisi interna dei codici HTML alla ricerca di flussi video...")
        for sito in sorted(domini_grezzi):
            risultato = verifica_presenza_player(sito)
            if risultato:
                lista_lupo_finale.add(risultato)
            time.sleep(0.5)
            
        print(f"\n🏆 OPERAZIONE COMPLETATA! Scoperti {len(lista_lupo_finale)} nuovi canali streaming funzionanti.")
        
        # Scrittura della lista finale pulita e ordinata
        with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
            for s in sorted(lista_lupo_finale):
                f.write(s + "\n")
        print("💾 File lista_del_lupo.txt aggiornato con i canali scovati dal web!")
    else:
        print("❌ La caccia non ha rilevato nuovi domini grezzi dai motori di ricerca.")
        
