import urllib.request
import urllib.parse
import re
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurazione finta identità umana
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# FONTI PULITE: Rimosso completamente GitHub per evitare l'auto-blocco delle Actions
FONTI = [
    "https://www.epgitalia.tv/wp-content/uploads/lista_domini.txt",
    "https://pastebin.com/raw/K7XgY8Yw"
]

VIETATI = [
    "google", "youtube", "facebook", "instagram", "twitter", "github", "wikipedia", "amazon", "apple",
    "linkedin", "pinterest", "microsoft", "reddit", "telegram", "aranzulla", "epgitalia"
]

# Elenco dei player video per certificare i siti di streaming veri
IMPRONTE_VIDEO = [
    "mixdrop", "streamtape", "voe", "voe.sx", "doodstream", "dood", "supervideo", 
    "vidoza", "easybytez", "wstream", "faststream", "maxstream", "videomega",
    "filemoon", "vidguard", "vidsrc", "embedwish", "lulustream", "streamsb", 
    "sbembed", "streamhide", "vidhide", "player", "embed", "iframe", "video", 
    "source src", "type=", "video/mp4", "m3u8", "m3u", "cloudflare", "sucuri"
]

def ottieni_contesto_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def scarica_testo_sicuro(url):
    """Scarica la lista aggirando i blocchi dei firewall"""
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'it-IT,it;q=0.9'
            }
        )
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=12) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Errore di rete su: {url} -> {str(e)}")
        return ""

def ispeziona_sito_per_video(url):
    """Verifica se il sito risponde ed è un sito di streaming valido"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, context=ottieni_contesto_ssl(), timeout=6) as response:
            html = response.read().decode('utf-8', errors='ignore').lower()
            if any(impronta in html for impronta in IMPRONTE_VIDEO):
                print(f"✅ CERTIFICATO: {url} contiene player validi.")
                return url
        print(f"❌ SCARTATO: {url} non ha player video.")
    except:
        # Se un sito dà errore ma è nella lista di EPGItalia, potrebbe usare Cloudflare protetto
        # Lo teniamo comunque come valido per evitare di perdere domini buoni
        if "epgitalia" in url:
            return url
    return None

if __name__ == "__main__":
    print("🐺 LUPOBOT: Avvio caccia mirata (Solo fonti esterne)... 🐺")
    domini_potenziali = set()
    siti_certificati = set()
    
    for fonte in FONTI:
        print(f"📥 Lettura risorsa esterna: {fonte}")
        testo = scarica_testo_sicuro(fonte)
        if testo:
            links = re.findall(r'(https?://[^\s,\"\']+)', testo)
            vecchio_totale = len(domini_potenziali)
            for l in links:
                try:
                    netloc = urllib.parse.urlparse(l).netloc.lower().replace("www.", "")
                    if netloc and not any(v in netloc for v in VIETATI) and len(netloc) > 8:
                        domini_potenziali.add(f"https://{netloc}")
                except: pass
            print(f"   🎉 Estratti {len(domini_potenziali) - vecchio_totale} domini unici da questa fonte.")
            
    print(f"\n📊 Totale domini grezzi accumulati: {len(domini_potenziali)}")
    
    if len(domini_potenziali) > 0:
        print("\n🧬 Verifica dei player video in corso...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(ispeziona_sito_per_video, sito): sito for sito in domini_potenziali}
            for future in as_completed(futures):
                risultato = future.result()
                if risultato:
                    siti_certificati.add(risultato)
                    
        print(f"\n🏆 FINE! Canali validati e pronti: {len(siti_certificati)}")
        
        with open("lista_del_lupo.txt", "w", encoding="utf-8") as f:
            for s in sorted(siti_certificati):
                f.write(s + "\n")
        print("💾 File lista_del_lupo.txt aggiornato con successo!")
    else:
        print("❌ Nessun dominio estratto. Controlla la connessione dei server.")
        
