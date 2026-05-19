import urllib.request
import urllib.parse
import re
import ssl
import time
import os

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT, 'Connection': 'keep-alive'}

def ottieni_contesto_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def scarica_lista_automatica(url):
    """Scarica il testo gestendo automaticamente i redirect e i link grezzi"""
    try:
        handler = urllib.request.HTTPRedirectHandler()
        opener = urllib.request.build_opener(handler)
        req = urllib.request.Request(url, headers=HEADERS)
        with opener.open(req, context=ottieni_contesto_ssl(), timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Impossibile leggere o seguire il link: {url} ({e})")
        return ""

def estrai_tutti_i_link(testo):
    """Estrae qualsiasi URL valido trovato nel testo, senza filtri"""
    return re.findall(r'(https?://[^\s,\"\']+)', testo)

if __name__ == "__main__":
    print("🐺 [LUPOBOT] Avvio unione globale e rimozione doppioni... 🐺")
    
    file_ingresso = "le_mie_sorgenti.txt"
    file_uscita = "lista_del_lupo.txt"
    
    # Se il file delle sorgenti non esiste, lo crea pre-popolato con le tue 4 fonti attuali
    if not os.path.exists(file_ingresso):
        print(f"⚠️ Crea il file '{file_ingresso}' e incolla dentro i tuoi link.")
        with open(file_ingresso, "w", encoding="utf-8") as f:
            f.write("https://www.epgitalia.
                    
