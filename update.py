import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
import time

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.9',
    'Connection': 'keep-alive'
}

# Il paniere delle migliori liste automatiche stabili da fondere insieme
LISTE_SORGENTI = [
    "https://raw.githubusercontent.com/LuFrAnNa/Veezie/main/Lista",
    "https://raw.githubusercontent.com/AlexS7/Lista-Veezie/main/lista.txt",
    "https://raw.githubusercontent.com/pndazz/veezie/main/lista.txt",
    "https://raw.githubusercontent.com/Gisgand/veezie-channels/main/channels.txt",
    "https://raw.githubusercontent.com/mttvll/veezie-urls/main/urls.txt",
    "https://pastebin.com/raw/K7XgY8Yw",
    "https://raw.githubusercontent.com/Yand94/veezie-list/main/lista.txt",
    "https://raw.githubusercontent.com/Kuro-01/veezie-ita/main/lista",
    "https://raw.githubusercontent.com/Tukkk/Veezie-Lists/main/channels.txt",
    "https://raw.githubusercontent.com/StreamIta/Streaming-Veezie/main/lista_automatica.txt"
]

VIETATI = [
    "google", "youtube", "facebook", "instagram", "twitter", "github", "wikipedia", "amazon", "apple",
    "linkedin", "pinterest", "microsoft", "reddit", "telegram", "aranzulla", "mojeek", "bing", "yahoo"
]

def ottieni_contesto_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def scarica_testo_lista(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Impossibile accedere alla sorgente: {url} -> {str(e)}")
        return ""

def estrai_domini_da_testo(testo):
    """Estrattore universale: trova domini validi anche se camuffati nel testo o senza http"""
    domini_trovati = set()
    # Trova pattern che assomigliano a domini (es: nome.estensione)
    pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)'
    
    for linea in testo.splitlines():
        linea = linea.strip()
        if not linea or any(v in linea.lower() for v in VIETATI):
            continue
            
        match = re.search(pattern, linea)
        if match:
            dominio = match.group(1).lower()
            # Evita falsi positivi basati su estensioni non web comuni nel testo
            if "." in dominio and not dominio.endswith(('.txt', '.md', '.json', '.xml', '.png', '.jpg')):
                if len(dominio.split('.')[-1]) >= 2:  # L'estensione deve avere almeno 2 caratteri (es. .cc, .com)
                    domini_trovati.add(f"https://{dominio}")
    return domini_trovati

def verifica_e_traccia_cambio_dominio(url):
    """Bussa al server con una richiesta rapida per convalidare lo stato o catturare il nuovo dominio"""
    try:
        req = urllib.request.Request(url, headers=HEADERS, method='HEAD')
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=6) as response:
            url_effettivo = response.geturl()
            netloc = urllib.parse.urlparse(url_effettivo).netloc.lower().replace("www.", "")
            if netloc and not any(v in netloc for v in VIETATI):
                return f"https://{netloc}"
    except urllib.error.HTTPError as e:
        # Se risponde con errore di protezione o server sovraccarico, il dominio è comunque attivo sul web
        if e.code in [403, 500, 503]:
            return url
    except Exception:
        pass
    return None

if __name__ == "__main__":
    print("🐺 LUPOBOT: Avvio aggregatore universale delle migliori liste... 🐺")
    domini_accumulati = set()
    lista_finale_pulita = set()
    
    # 1. Raccolta globale e unione delle liste
    print("\n📂 [1/2] Estrazione e unione dei link da tutte le liste automatiche...")
    for sorgente in LISTE_SORGENTI:
        contenuto = scarica_testo_lista(sorgente)
        if contenuto:
            estratti = estrai_domini_da_testo(contenuto)
            vecchio_totale = len(domini_accumulati)
            domini_accumulati.update(estratti)
            print(f"   -> Estratti {len(domini_accumulati) - vecchio_totale} nuovi canali unici da: {sorgente}")
        time.sleep(0.4)
            
    print(f"\n📊 TOTALIZZATO: {len(domini_accumulati)} domini unici pronti per il controllo stabilità.")
    
    # 2. Controllo filtri e selezione finale
    if domini_accumulati:
        print("\n🧬 [2/2] Verifica connettività e tracciamento delle nuove estensioni...")
        for i, sito in enumerate(sorted(domini_accumulati), 1):
            url_valido = verifica_e_traccia_cambio_dominio(sito)
            if url_valido:
                lista_finale_pulita.add(url_valido)
            if i % 15 == 0 or i == len(domini_accumulati):
                print(f"   ...elaborazione: {i}/{len(domini_accumulati)} domini verificati...")
            time.sleep(0.15)
            
        print(f"\n🏆 COMPILAZIONE COMPLETATA: Ristretti {len(lista_finale_pulita)} canali di qualità pronti all'uso.")
        
        # Scrittura fisica del file finale nel tuo repository
        with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
            for s in sorted(lista_finale_pulita):
                f.write(s + "\n")
        print("💾 Il file 'lista_del_lupo.txt' è stato sovrascritto e aggiornato con la super-lista!")
    else:
        print("❌ Errore critico: Nessun dato estratto. Controllare le connessioni delle liste sorgenti.")
        
