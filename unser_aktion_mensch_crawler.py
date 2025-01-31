import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse, unquote
import re

def parse_website(url, output_file):
    # Bereinige die URL, um potenzielle Probleme mit Leerzeichen oder falscher Kodierung zu beheben
    url = unquote(url).strip()

    # HTTP-Anfrage
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # HTML parsen
    soup = BeautifulSoup(response.text, "html.parser")

    # Extrahiere die H1-Überschrift aus dem spezifischen <div> (nicht aus dem <header>)
    header_h1 = soup.find('div', class_='nav-simple-language-tile-children-overview__headline')
    formatted_text = []

    # Prüfe, ob die H1-Überschrift vorhanden ist
    if header_h1:
        h1_tag = header_h1.find('h1')
        if h1_tag:
            formatted_text.append(f"\n{h1_tag.get_text(strip=True)}\n")
        else:
            formatted_text.append("Keine H1 gefunden")  # Falls keine H1 gefunden wird
    else:
        formatted_text.append("Kein Header gefunden")  # Falls das <div> nicht gefunden wird

    # Hauptinhalt identifizieren
    main_content = soup.find('main')  
    if not main_content:
        print(f"Hauptinhalt nicht gefunden: {url}")
        return

    # Text mit Zeilenumbrüchen und Einrückungen formatieren
    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'br', 'strong']):
        if element.name in ['h1', 'h2', 'h3']:
            formatted_text.append(f"\n{element.get_text(strip=True)}\n")
        elif element.name == 'p':
            p_text = []
            for sub_element in element.children:
                if sub_element.name == 'strong':
                    # Text im <strong> mit Leerzeichen davor
                    p_text.append(f" {sub_element.get_text(strip=True)} ")
                elif isinstance(sub_element, str):
                    p_text.append(sub_element.strip())
                elif sub_element.name == 'br':
                    p_text.append("\n")  # Zeilenumbruch bei <br>
            formatted_text.append("".join(p_text))
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                li_text = []
                for sub_element in li.children:
                    if sub_element.name == 'strong':
                        # Text im <strong> mit Leerzeichen davor
                        li_text.append(f" {sub_element.get_text(strip=True)} ")
                    elif sub_element.name == 'br':
                        li_text.append("\n")  # Zeilenumbruch für <br> innerhalb des <li>
                    elif isinstance(sub_element, str):
                        li_text.append(f"{sub_element.strip()}")
                formatted_text.append(f"- {' '.join(li_text)}")
           # formatted_text.append("")  # Leerzeile nach einer Liste
        elif element.name == 'br':
            # Füge einen Zeilenumbruch für <br> ein
            formatted_text.append("\n")

    # Ordner für die Speicherung erstellen, falls er nicht existiert
    folder_name = "aktion-mensch"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Speichere die Datei im Ordner 'aktion-mensch'
    with open(os.path.join(folder_name, output_file), 'w', encoding='utf-8') as file:
        file.write("\n".join(formatted_text))
    print(f"Text erfolgreich gespeichert: {os.path.join(folder_name, output_file)}")

def parse_all_websites(json_file):
    # Lade URLs aus der JSON-Datei
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Setze eine Menge von URLs, um doppelte Einträge zu vermeiden
    seen_urls = set()

    # Definiere die gültige Domain
    valid_domain = "aktion-mensch.de"

    # Iteriere über alle Einträge und verarbeite nur die "original_url"
    for key, value in data.items():
        original_url = value.get('original_url')
        
        # Überprüfe, ob die URL zur richtigen Domain gehört
        if original_url and valid_domain in urlparse(original_url).netloc and original_url not in seen_urls:
            seen_urls.add(original_url)
            filename = re.sub(r'[\/\\:]', '_', original_url)
            output_file = f"{filename[12:]}.txt"  # Verwende den URL-Pfad als Dateinamen
            parse_website(original_url, output_file)

# Beispielaufruf
json_file = "archive_header.json"  # JSON-Datei mit den URLs
parse_all_websites(json_file)
