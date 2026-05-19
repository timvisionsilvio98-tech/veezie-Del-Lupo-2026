import urllib.request
import re
import ssl
import time

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HEADERS = [('User-Agent', USER_AGENT)]

def ottieni_opener_senza_ssl():
    """Crea un opener che ignora i controlli SSL e supporta i redirect"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Applichiamo il contesto SSL direttamente all'handler HTTPS
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    redirect_handler = urllib.request.HTTPRedirectHandler()
    
    opener = urllib.request.build_opener(https_handler, redirect_handler)
    opener.addheaders = HEADERS
    return opener

def scarica_siti_da_link(opener, url):
    """Scarica il file TXT online e restituisce il testo contenuto"""
    try:
        with opener.open(url, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Impossibile leggere il link: {url} ({e})")
        return ""

if __name__ == "__main__":
    print("🐺 [LUPOBOT] Estrazione siti dai link e rimozione doppioni... 🐺")
    
    # I tuoi 4 link di partenza
    sorgenti = [
        "https://www.epgitalia.tv/wp-content/uploads/lista_domini.txt",
        "https://pastebin.com/raw/KgQ4jTy6",
        "https://dub.sh/t3kCLOUD-Veezie-Lista-Auto",
        "https://raw.githubusercontent.com/webassistance/lista-veezie/main/lista_domini.txt"
    ]
    
    # Contenitore unico per eliminare i duplicati in automatico
    tutti_i_siti_unici = set()
    
    # Inizializza il lettore di link corretto
    lettore_url = ottieni_opener_senza_ssl()
    
    for i, url in enumerate(sorgenti, 1):
        print(f"[{i}/{len(sorgenti)}] Scarico i siti da: {url}")
        
        # Scarica il testo contenuto nel link
        testo_del_link = scarica_siti_da_link(lettore_url, url)
        
        if testo_del_link:
            # Estrae tutti i link/siti streaming trovati dentro quel file TXT
            siti_trovati = re.findall(r'(https?://[^\s,\"\']+)', testo_del_link)
            print(f"   🔹 Trovati {len(siti_trovati)} siti dentro questo link.")
            
            # Li aggiunge al contenitore (i doppioni spariscono da soli)
            tutti_i_siti_unici.update(siti_trovati)
        
        time.sleep(0.5) # Pausa di sicurezza
        
    # Salvataggio finale
    file_uscita = "lista_del_lupo.txt"
    if tutti_i_siti_unici:
        with open(file_uscita, "w", encoding="utf-8") as f:
            for sito in sorted(tutti_i_siti_unici):
                f.write(sito + "\n")
        
        print(f"\n📊 FUSIONE COMPLETATA!")
        print(f"   -> Siti totali estratti (senza doppioni): {len(tutti_i_siti_unici)}")
        print(f"🏆 SUCCESS: Nuova lista creata in '{file_uscita}'!")
    else:
        print("❌ Errore: non è stato possibile estrarre nessun sito.")
        
