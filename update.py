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
        with opener.open(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""

def cerca_su_provider_libero(opener, query):
    """Interroga un'istanza pubblica e libera di SearXNG per trovare nuovi siti senza blocchi corporativi"""
    siti_trovati = set()
    print(f"🔍 Ricerca su Provider Libero (SearXNG) per: '{query}'...")
    
    # Utilizziamo un'istanza pubblica nota di SearXNG che espone le API in JSON
    url_provider = f"https://searx.space/search?q={urllib.parse.quote(query)}&format=json"
    
    try:
        req = urllib.request.Request(url_provider)
        with opener.open(req, timeout=12) as response:
            dati = json.loads(response.read().decode('utf-8', errors='ignore'))
            if "results" in dati:
                for risultato in dati["results"]:
                    if "url" in risultato:
                        siti_trovati.add(risultato["url"])
    except Exception as e:
        # Se la prima istanza è temporaneamente offline, proviamo un'alternativa comune
        try:
            url_alternativo = f"https://baresearch.org/search?q={urllib.parse.quote(query)}&format=json"
            req = urllib.request.Request(url_alternativo)
            with opener.open(req, timeout=10) as response:
                dati = json.loads(response.read().decode('utf-8', errors='ignore'))
                if "results" in dati:
                    for risultato in dati["results"]:
                        if "url" in risultato:
                            siti_trovati.add(risultato["url"])
        except Exception:
            print("   ⚠️ Il provider libero non ha risposto in tempo. Salto la ricerca web.")
            
    return siti_trovati

if __name__ == "__main__":
    print("🐺 [LUPOBOT + SEARXNG] Unione liste storiche e scansione web libera... 🐺")
    
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
    
    # 1. FASE DI ESTRAZIONE DALLE LISTE FISSE
    for i, url in enumerate(sorgenti, 1):
        print(f"[{i}/{len(sorgenti)}] Estrazione da lista: {url}")
        testo_del_link = scarica_siti_da_link(lettore_url, url)
        if testo_del_link:
            siti_trovati = re.findall(r'(https?://[^\s,\"\']+)', testo_del_link)
            tutti_i_siti_unici.update(siti_trovati)
        time.sleep(0.5) 
        
    # 2. FASE DI RICERCA LIVE SUL PROVIDER LIBERO
    chiavi_ricerca = [
        "migliori siti streaming film gratis",
        "serie tv streaming italia"
    ]
    
    for query in chiavi_ricerca:
        risultati_web = cerca_su_provider_libero(lettore_url, query)
        for link in risultati_web:
            # Pulisce l'URL per estrarre solo la radice del sito (es. https://nome-nuovo-sito.com)
            match = re.match(r'(https?://[^/]+)', link)
            if match:
                tutti_i_siti_unici.add(match.group(1))
        time.sleep(1)

    # Rimozione delle liste sorgenti di partenza per evitare disordine su Veezie
    for s in sorgenti:
        tutti_i_siti_unici.discard(s)

    # ⚠️ BLOCCO DI SICUREZZA: Scarta i siti Torrent/Magnet rilevati e i motori stessi
    PAROLE_BLOCCATE = [
        "1337x", "rargb", "rarbg", "torrent", "magnet", "yts", "limetorrents", 
        "thepiratebay", "searx", "wikipedia", "github", "google", "facebook"
    ]
    siti_filtrati = set()
    
    for sito in tutti_i_siti_unici:
        sito_lower = sito.lower()
        if any(parola in sito_lower for parola in PAROLE_BLOCCATE):
            continue
        siti_filtrati.add(sito)

    # 3. SALVATAGGIO FINALE E GENERAZIONE LINK VEEZIE
    file_uscita = "lista_del_lupo.txt"
    if siti_filtrati:
        with open(file_uscita, "w", encoding="utf-8") as f:
            for sito in sorted(siti_filtrati):
                f.write(sito + "\n")
        
        print(f"\n📊 ELABORAZIONE COMPLETATA CON SUCCESSO!")
        print(f"   -> Siti totali pronti (Liste + Ricerca Libera): {len(siti_filtrati)}")
        print(f"🏆 SUCCESS: Aggiornato file '{file_uscita}'!")
        
        # Output automatico del link finale da copiare su Veezie
        repo = os.getenv("GITHUB_REPOSITORY")
        if repo:
            link_veezie = f"https://raw.githubusercontent.com/{repo}/main/{file_uscita}"
            print("\n" + "═"*60)
            print("🔗 COPIA QUESTO LINK E METTILO NELLA LISTA AUTOMATICA DI VEEZIE:")
            print(f"👉 {link_veezie}")
            print("═"*60 + "\n")
    else:
        print("❌ Nessun link valido estratto.")
