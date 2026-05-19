import urllib.request
import urllib.error
import re
import ssl
import time
import os

HEADERS = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
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
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"   ⚠️ Nota: {url} ha temporaneamente limitato la richiesta (Errore 429). Salto.")
        else:
            print(f"   ⚠️ Impossibile leggere la sorgente: {url} (Errore HTTP {e.code})")
        return ""
    except Exception as e:
        print(f"   ⚠️ Errore di connessione per: {url} ({e})")
        return ""

if __name__ == "__main__":
    print("🐺 [LUPOBOT] Estrazione globale e pulizia siti Torrent/Magnet... 🐺")
    
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
    
    # 1. SCARICAMENTO E UNIONE GLOBALE
    for i, url in enumerate(sorgenti, 1):
        print(f"[{i}/{len(sorgenti)}] Analisi sorgente: {url}")
        testo_del_link = scarica_siti_da_link(lettore_url, url)
        
        if testo_del_link:
            siti_trovati = re.findall(r'(https?://[^\s,\"\']+)', testo_del_link)
            print(f"   🔹 Estratti {len(siti_trovati)} canali streaming.")
            tutti_i_siti_unici.update(siti_trovati)
        
        time.sleep(1) 
        
    # Pulizia di sicurezza: evita che le sorgenti stesse finiscano dentro Veezie
    for s in sorgenti:
        tutti_i_siti_unici.discard(s)

    # ⚠️ FILTRO INTELLIGENTE: Elimina i siti basati su Torrent e Magnet
    PAROLE_BLOCCATE = ["1337x", "rargb", "rarbg", "torrent", "magnet", "yts", "limetorrents", "thepiratebay"]
    siti_filtrati = set()
    
    for sito in tutti_i_siti_unici:
        sito_lower = sito.lower()
        # Se il sito contiene una delle parole collegate ai torrent, viene scartato
        if any(parola in sito_lower for parola in PAROLE_BLOCCATE):
            continue
        siti_filtrati.add(sito)

    # 2. SALVATAGGIO E GENERAZIONE LINK PER VEEZIE
    file_uscita = "lista_del_lupo.txt"
    if siti_filtrati:
        with open(file_uscita, "w", encoding="utf-8") as f:
            for sito in sorted(siti_filtrati):
                f.write(sito + "\n")
        
        print(f"\n📊 FUSIONE TOTALE COMPLETATA!")
        print(f"   -> Canali salvati (Siti Torrent/Magnet rimossi con successo): {len(siti_filtrati)}")
        print(f"🏆 SUCCESS: Aggiornato file '{file_uscita}'!")
        
        # Genera il link automatico leggendo i tuoi dati GitHub
        repo = os.getenv("GITHUB_REPOSITORY")
        if repo:
            link_veezie = f"https://raw.githubusercontent.com/{repo}/main/{file_uscita}"
            print("\n" + "═"*60)
            print("🔗 COPIA QUESTO LINK E METTILO NELLA LISTA AUTOMATICA DI VEEZIE:")
            print(f"👉 {link_veezie}")
            print("═"*60 + "\n")
        else:
            print(f"\nℹ️ (In locale) Su GitHub qui vedrai il link pronto per Veezie.")
            
    else:
        print("❌ Nessun link trovato analizzando le sorgenti.")
        
