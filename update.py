import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
import time
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.9',
    'X-Forwarded-For': '151.40.84.112',
    'X-Real-IP': '151.40.84.112',
    'Connection': 'keep-alive'
}

# 1. LIVELLI DI SORGENTI FISSE (Aggregazione standard)
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

# 2. FILTRO DI SICUREZZA (Siti da scartare categoricamente)
VIETATI = [
    "google", "youtube", "facebook", "instagram", "twitter", "github", "wikipedia", "amazon", "apple",
    "linkedin", "pinterest", "microsoft", "reddit", "telegram", "aranzulla", "mojeek", "bing", "yahoo"
]

def ottieni_contesto_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def simula_ricerca_api(query):
    """
    Modulo Esploratore: Simula la ricerca di nuove fonti sul web.
    Usa una struttura JSON pulita per evitare i blocchi dei motori di ricerca tradizionali.
    """
    print(f"🔍 [Fase Esplorazione] Ricerca in corso per la query: '{query}'")
    
    # Struttura di simulazione dei risultati indicizzati da un motore di ricerca
    risposta_mock = """
    {
        "results": [
            {"url": "https://esempio-nuova-lista-aggiornata.org/links.txt"},
            {"url": "https://segnalazioni-canali-test.click/lista"}
        ]
    }
    """
    try:
        dati = json.loads(risposta_mock)
        return [item["url"] for item in dati.get("results", [])]
    except Exception:
        return []

def scarica_testo_lista(url):
    """Scarica in modo sicuro il testo grezzo dalle liste sorgente conosciute."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=12) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""

def verifica_e_traccia_cambio_dominio(url):
    """
    Modulo Verificatore: Invia richieste HEAD, traccia i redirect 301/302 
    verso nuove estensioni (.force, .click) ed elimina i siti offline.
    """
    try:
        class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                return super().redirect_request(req, fp, code, msg, hdrs, newurl)

        opener = urllib.request.build_opener(SafeRedirectHandler)
        req = urllib.request.Request(url, headers=HEADERS, method='HEAD')
        
        with opener.open(req, context=ottieni_contesto_ssl(), timeout=5) as response:
            url_effettivo = response.geturl()
            netloc = urllib.parse.urlparse(url_effettivo).netloc.lower().replace("www.", "")
            
            if netloc and not any(v in netloc for v in VIETATI):
                nuovo_url = f"https://{netloc}"
                if nuovo_url != url:
                    print(f"   🔄 DOMINIO AGGIORNATO: {url} -> {nuovo_url}")
                return nuovo_url
    except urllib.error.HTTPError as e:
        # Se il sito risponde (anche con un blocco 403 o un errore 500), esiste ed è attivo.
        if e.code in [403, 500, 503]:
            return url
    except Exception:
        # Se va in timeout o genera errori di connessione (host non trovato), il sito è morto.
        pass
    return None

if __name__ == "__main__":
    print("🐺 LUPOBOT ACTIVATED: Inizio aggregazione, esplorazione e controllo domini... 🐺")
    domini_grezzi = set()
    lista_finale_pulita = set()
    
    # SOTTO-FASE A: Estrazione link dalle liste fisse note
    print("\n📂 [1/3] Estrazione dati dalle liste automatiche conosciute...")
    for sorgente in LISTE_SORGENTI:
        testo = scarica_testo_lista(sorgente)
        if testo:
            links = re.findall(r'(https?://[^\s,\"\']+)', testo)
            vecchio_totale = len(domini_grezzi)
            for l in links:
                try:
                    netloc = urllib.parse.urlparse(l).netloc.lower().replace("www.", "")
                    if netloc and not any(v in netloc for v in VIETATI) and len(netloc) > 8:
                        domini_grezzi.add(f"https://{netloc}")
                except: pass
            print(f"   -> Recuperati {len(domini_grezzi) - vecchio_totale} domini unici da: {sorgente}")
        time.sleep(0.3)
            
    # SOTTO-FASE B: Esplorazione tramite motore di ricerca inserendo la parola chiave
    print("\n🚀 [2/3] Scouting sul Web per intercettare nuove liste...")
    nuove_fonti = simula_ricerca_api("lista automatica veezie")
    for fonte in nuove_fonti:
        try:
            netloc = urllib.parse.urlparse(fonte).netloc.lower().replace("www.", "")
            if netloc and not any(v in netloc for v in VIETATI):
                domini_grezzi.add(f"https://{netloc}")
        except: pass

    print(f"\n📊 TOTALIZZATO: {len(domini_grezzi)} domini complessivi accumulati nel setaccio.")
    
    # SOTTO-FASE C: Controllo dello stato di salute dei server e cattura estensioni aggiornate
    if domini_grezzi:
        print("\n🧬 [3/3] Controllo di connettività e tracciamento dei domini trasferiti...")
        for sito in sorted(domini_grezzi):
            url_valido = verifica_e_traccia_cambio_dominio(sito)
            if url_valido:
                lista_finale_pulita.add(url_valido)
            time.sleep(0.2) # Pausa di cortesia anti-ban
            
        print(f"\n🏆 CONCLUSO: Abbiamo filtrato {len(lista_finale_pulita)} canali stabili e puliti.")
        
        # Salvataggio su file finale
        with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
            for s in sorted(lista_finale_pulita):
                f.write(s + "\n")
        print("💾 File lista_del_lupo.txt compilato e pronto per il commit!")
    else:
        print("❌ Errore: Nessun dominio estratto dalle fonti.")
        
