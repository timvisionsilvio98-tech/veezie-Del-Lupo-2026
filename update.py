import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
import time
import os
import json

HEADERS = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
    ('Accept', 'application/json,text/html;q=0.9,*/*;q=0.8'),
    ('Connection', 'keep-alive')
]

def ottieni_opener_senza_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    redirect_handler = urllib.request.HTTPRedirectHandler()
    cookie_handler = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(https_handler, redirect_handler, cookie_handler)
    opener.addheaders = HEADERS
    return opener

def scarica_siti_da_link(opener, url):
    try:
        req = urllib.request.Request(url)
        with opener.open(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""

def cerca_su_primo_funzionante(opener, query):
    """Trova il primo provider che risponde e prende i link delle pagine/guide allo streaming"""
    siti_trovati = set()
    
    istanze_provider = {
        "SearXNG (Rhscz)": f"https://search.rhscz.eu/search?q={urllib.parse.quote(query)}&format=json",
        "BareSearch": f"https://baresearch.org/search?q={urllib.parse.quote(query)}&format=json",
        "DuckDuckGo API": f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1",
        "SearXNG (Be)": f"https://searx.be/search?q={urllib.parse.quote(query)}&format=json"
    }
    
    print(f"\n🔍 [RICERCA WEB] Cerco pagine di riferimento per: '{query}'")
    print("-" * 60)
    
    for nome, url in istanze_provider.items():
        try:
            req = urllib.request.Request(url)
            with opener.open(req, timeout=5) as response:
                dati = json.loads(response.read().decode('utf-8', errors='ignore'))
                
                if "results" in dati:
                    for r in dati["results"]:
                        if "url" in r:
                            siti_trovati.add(r["url"])
                elif "RelatedTopics" in dati:
                    for topic in dati["RelatedTopics"]:
                        if "FirstURL" in topic:
                            siti_trovati.add(topic["FirstURL"])
            
            if siti_trovati:
                print(f"   🟢 {nome} HA RISPOSTO! Trovate {len(siti_trovati)} pagine/guide utili. Inizio a estrarre i siti da lì dentro.")
                break 
            else:
                print(f"   🟡 {nome}: Nessun risultato utile. Provo il successivo...")
        except Exception:
            continue
            
    print("-" * 60)
    return siti_trovati

if __name__ == "__main__":
    print("🐺 [LUPOBOT DEEP EXTRACTOR] Unione liste e scansione interna delle pagine web... 🐺")
    
    sorgenti = [
        "https://www.epgitalia.tv/wp-content/uploads/lista_domini.txt",
        "https://pastebin.com/raw/KgQ4jTy6",
        "https://dub.sh/t3kCLOUD-Veezie-Lista-Auto",
        "https://raw.githubusercontent.com/webassistance/lista-veezie/main/lista_domini.txt",
        "https://raw.githubusercontent.com/orandodm/veezie-channel-list/main/canali.txt",
        "https://raw.githubusercontent.com/ZzZ-Simone-ZzZ/Lista-Veezie/main/lista_canali.txt",
        "https://pastebin.com/raw/2b7X6g9F"
    ]
    
    tutti_i_siti_unici = set()
    lettore_url = ottieni_opener_senza_ssl()
    
    # 1. ESTRAZIONE DALLE LISTE FISSE DELLA COMMUNITY
    print("\n📦 [FASE 1] Lettura dei canali dalle liste fisse...")
    for i, url in enumerate(sorgenti, 1):
        testo_del_link = scarica_siti_da_link(lettore_url, url)
        if testo_del_link:
            siti_trovati = re.findall(r'(https?://[^\s,\"\']+)', testo_del_link)
            tutti_i_siti_unici.update(siti_trovati)
        
    # 2. RICERCA LIVE ED ESTRAZIONE MIRATA "DA DENTRO" LE PAGINE
    print("\n🌐 [FASE 2] Ricerca web ed estrazione siti interni...")
    chiavi_ricerca = [
        "lista siti streaming film gratis italia",
        "nuovi siti serie tv streaming"
    ]
    
    pagine_guide = set()
    for query in chiavi_ricerca:
        pagine_guide.update(cerca_su_primo_funzionante(lettore_url, query))
    
    # Entra dentro le singole pagine trovate per prendere i veri siti di streaming elencati
    if pagine_guide:
        print(f"\n🚀 [DEEP EXTRACTION] Scansiono l'interno delle pagine trovate per inserire i siti consigliati...")
        # Limite a 6 pagine per non appesantire troppo GitHub Actions
        for idx, url_pagina in enumerate(list(pagine_guide)[:6], 1):
            print(f"   [{idx}] Analizzo l'articolo: {url_pagina}")
            testo_html = scarica_siti_da_link(lettore_url, url_pagina)
            
            if testo_html:
                # Trova tutti i link ipertestuali presenti nel testo della pagina
                link_scovati = re.findall(r'(https?://[^\s,\"\']+)', testo_html)
                siti_inseriti_da_qui = 0
                
                for link in link_scovati:
                    # Isola il dominio pulito (es: https://sito-streaming.click)
                    match_dominio = re.match(r'(https?://[^/]+)', link)
                    if match_dominio:
                        dominio_pulito = match_dominio.group(1)
                        if dominio_pulito not in tutti_i_siti_unici:
                            tutti_i_siti_unici.add(dominio_pulito)
                            siti_inseriti_da_qui += 1
                print(f"      🔹 Fatto! Inseriti {siti_inseriti_da_qui} nuovi siti di streaming estratti dal testo.")
            else:
                print("      ⚠️ Pagina protetta o non raggiungibile.")
            time.sleep(0.5)

    # Rimuove dall'elenco i link delle liste di partenza
    for s in sorgenti:
        tutti_i_siti_unici.discard(s)

    # ⚠️ FILTRO DI SICUREZZA RIFINITO: Taglia fuori Torrent, Magnet e siti civetta
    PAROLE_BLOCCATE = [
        "1337x", "rargb", "rarbg", "torrent", "magnet", "yts", "limetorrents", 
        "thepiratebay", "searx", "wikipedia", "github", "google", "facebook", 
        "duckduckgo", "rhscz", "baresearch", "bing", "yahoo", "w3.org", "twitter",
        "instagram", "amazon", "cloudflare", "schema.org", "wordpress", "tg24"
    ]
    siti_filtrati = set()
    
    for sito in tutti_i_siti_unici:
        sito_lower = sito.lower()
        if any(parola in sito_lower for parola in PAROLE_BLOCCATE):
            continue
        # Salva solo domini reali e significativi
        if len(sito) > 9 and "." in sito: 
            siti_filtrati.add(sito)

    # 3. SALVATAGGIO FINALE E GENERAZIONE LINK VEEZIE
    file_uscita = "lista_del_lupo.txt"
    if siti_filtrati:
        with open(file_uscita, "w", encoding="utf-8") as f:
            for sito in sorted(siti_filtrati):
                f.write(sito + "\n")
        
        print(f"\n📊 [FASE 3] PROCESSO DI FUSIONE E DEEP-SEARCH TERMINATO!")
        print(f"   -> Canali unici pronti da inserire su Veezie: {len(siti_filtrati)}")
        print(f"🏆 SUCCESS: Il tuo file '{file_uscita}' è aggiornato con tutte le novità online.")
        
        repo = os.getenv("GITHUB_REPOSITORY")
        if repo:
            link_veezie = f"https://raw.githubusercontent.com/{repo}/main/{file_uscita}"
            print("\n" + "═"*60)
            print("🔗 COPIA QUESTO LINK E METTILO NELLA LISTA AUTOMATICA DI VEEZIE:")
            print(f"👉 {link_veezie}")
            print("═"*60 + "\n")
            
