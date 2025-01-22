import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

# Funktion zur Überprüfung, ob eine Seite relevante Inhalte enthält
def validate_target_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False  # Seite nicht erreichbar

        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ["Urheber", "Urheberrecht", "Leistungsschutzrecht", "Copyright", "Nutzungsbedingungen", "Lizenzbedingungen"]

        # Suche in Überschriften (<h1> bis <h4>, <strong>, <em>)
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'em']):
            if any(keyword.lower() in tag.get_text(separator=" ").lower() for keyword in keywords):
                return True  # Relevante Inhalte gefunden

        # Suche in regulärem Text mit <br> als Trenner
        for tag in soup.find_all(['p', 'div']):
            if any(keyword.lower() in tag.get_text(separator=" ").lower() for keyword in keywords):
                return True  # Relevante Inhalte gefunden

        # Suche in Attributen wie `class` oder `id`
        for tag in soup.find_all():
            attributes = tag.attrs
            for attr, value in attributes.items():
                if isinstance(value, str) and any(keyword.lower() in value.lower() for keyword in keywords):
                    return True  # Relevante Inhalte gefunden in Attributen

        return False  # Keine relevanten Inhalte gefunden
    except:
        return False  # Fehler beim Abrufen der Seite

# Funktion zum Suchen nach Links zu relevanten Seiten
def find_relevant_links(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return f"Fehler: 403 - Zugriff verweigert bei {url}"
        elif response.status_code == 404:
            # Fallback: Prüfe alternative Seiten wie /impressum, /agb, /datenschutz
            fallback_paths = ["/impressum", "/agb", "/datenschutz", "/recht"]
            for path in fallback_paths:
                fallback_url = urljoin(url, path)
                if validate_target_page(fallback_url):
                    return fallback_url
            return f"Fehler: 404 - Keine relevanten Inhalte gefunden bei {url}"
        elif response.status_code != 200:
            return f"Fehler: {response.status_code} bei {url}"

        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ["impressum", "agb", "datenschutz", "recht", "copyright", "nutzungsbedingungen", "lizenzbedingungen"]

        # Suche nach Links mit relevanten Schlüsselwörtern
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(keyword in href for keyword in keywords):
                full_url = urljoin(url, href)  # Absoluten Link erzeugen

                # Validierung der Zielseite
                if validate_target_page(full_url):
                    return full_url

        # Fallback, wenn keine relevanten Links gefunden wurden
        return "Kein relevanter Link gefunden"
    
    except Exception as e:
        return f"Fehler bei der Verarbeitung der URL: {e}"

# Erweiterte Funktion für Subdomains
def process_url_with_subdomain_handling(url):
    # Zuerst die ursprüngliche URL prüfen
    result = find_relevant_links(url)
    if "Fehler" not in result and "Kein relevanter Link gefunden" not in result:
        return result  # Relevanter Link gefunden

    # Hauptdomain extrahieren und prüfen
    main_domain = get_main_domain(url)
    main_domain_url = f"https://{main_domain}"
    result = find_relevant_links(main_domain_url)
    if "Fehler" not in result and "Kein relevanter Link gefunden" not in result:
        return result  # Relevanter Link gefunden auf Hauptdomain

    return result  # Kein relevanter Link gefunden, Rückgabe des ursprünglichen Ergebnisses

# Funktion zum Extrahieren der Hauptdomain aus einer URL
def get_main_domain(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 2:
        return '.'.join(domain_parts[-2:])  # Hauptdomain extrahieren
    return parsed_url.netloc

# Laden der Excel-Datei
file_path = 'URLs.xlsx'  # Pfad zur Excel-Datei
df = pd.read_excel(file_path, engine='openpyxl')

# Filtern der Zeilen mit gültigen URLs
valid_urls = df.iloc[:, [0, 1]].stack().dropna().unique()  # Extrahiert alle gültigen URLs

# Set, um redundante Domains zu vermeiden
unique_domains = set()
relevant_links = []

# Durchlaufe jede URL und extrahiere nur eine pro Domain
for url in valid_urls:
    domain = get_main_domain(url)
    if domain not in unique_domains:
        unique_domains.add(domain)
        relevant_links.append({
            'Domain': domain,
            'Relevanter Link oder Fehler': process_url_with_subdomain_handling(url)
        })

# Speichern der Ergebnisse in einer Excel-Datei
output_file = 'urheberrechtshinweise.xlsx'
df_output = pd.DataFrame(relevant_links)

# Schreiben der DataFrame in eine Excel-Datei
df_output.to_excel(output_file, index=False, engine='openpyxl')

print(f"Relevante Links und Fehler wurden in '{output_file}' gespeichert.")
