import urllib.request
import re
import ssl
import time

# Intestazioni per camuffarsi da vero browser ed evitare i blocchi (es. 429)
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
    """Scarica il contenuto dei tuoi 4 link di partenza"""
    try:
        req = urllib.request.Request(url)
        with opener.open(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Impossibile leggere il link sorgente: {url} ({e})")
        return ""

def verifica_sito_online(opener, url):
    """Verifica se il singolo sito streaming è online e funzionante"""
    try:
        # Metodo HEAD: rapido, controlla solo se il server risponde senza scaricare la pagina
        req = urllib.request.Request(url, method='HEAD')
        with opener.open(req, timeout=5) as response:
            if response.status < 400:
                return True
    except Exception:
        # Se HEAD fallisce (alcuni server lo bloccano), proviamo con GET prima di darlo per morto
        try:
            req = urllib.request.Request(url, method='GET')
            with opener.open(req, timeout=5) as response:
                if response.status < 400:
                    return True
        except Exception:
            pass
    return False

if __name__ == "__main__":
    print("🐺 [LUPOBOT] Estrazione siti dai link e rimozione doppioni... 🐺")
    
    sorgenti = [
        "https://www.epgitalia.tv/wp-content/uploads/lista_domini.txt",
        "https://pastebin.com/raw/KgQ4jTy6",
        "https://dub.sh/t3kCLOUD-Veezie-Lista-Auto",
        "https://raw.githubusercontent.com/webassistance/lista-veezie/main/lista_domini.txt"
    ]
    
    tutti_i_siti_unici = set()
    lettore_url = ottieni_opener_senza_ssl()
    
    # 1. FASE DI ESTRAZIONE
    for i, url in enumerate(sorgenti, 1):
        print(f"[{i}/{len(sorgenti)}] Scarico i siti da: {url}")
        testo_del_link = scarica_siti_da_link(lettore_url, url)
        
        if testo_del_link:
            siti_trovati = re.findall(r'(https?://[^\s,\"\']+)', testo_del_link)
            print(f"   🔹 Trovati {len(siti_trovati)} siti dentro questo link.")
            tutti_i_siti_unici.update(siti_trovati)
        
        time.sleep(1.5) 
        
    # 2. FASE DI VERIFICA ONLINE
    siti_funzionanti = []
    if tutti_i_siti_unici:
        print(f"\n🔍 Avvio verifica dello stato dei link ({len(tutti_i_siti_unici)} siti da controllare)...")
        
        for idx, sito in enumerate(sorted(tutti_i_siti_unici), 1):
            # Salta i tuoi link di partenza se per caso finiscono nel calderone
            if sito in sorgenti:
                continue
                
            print(f"   [{idx}/{len(tutti_i_siti_unici)}] Controllo: {sito} ", end="")
            
            if verifica_sito_online(lettore_url, sito):
                print("🟢 ONLINE")
                siti_funzionanti.append(sito)
            else:
                print("🔴 OFFLINE (Scartato)")
                
            time.sleep(0.1) # Micro pausa per non sovraccaricare le richieste
            
    # 3. SALVATAGGIO FINALE
    file_uscita = "lista_del_lupo.txt"
    if siti_funzionanti:
        with open(file_uscita, "w", encoding="utf-8") as f:
            for sito in siti_funzionanti:
                f.write(sito + "\n")
        
        print(f"\n📊 FUSIONE E VERIFICA COMPLETATE!")
        print(f"   -> Siti totali trovati nelle sorgenti: {len(tutti_i_siti_unici)}")
        print(f"   -> Siti realmente FUNZIONANTI salvati: {len(siti_funzionanti)}")
        print(f"🏆 SUCCESS: Lista pulita creata in '{file_uscita}'!")
    else:
        print("❌ Errore: nessun sito è risultato online.")
