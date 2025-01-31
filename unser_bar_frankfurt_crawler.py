import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse, unquote
import re

def parse_website(url, output_file):
    # Bereinige die URL, um potenzielle Probleme zu vermeiden
    url = unquote(url).strip()

    # HTTP-Anfrage senden
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

    # Liste für den extrahierten Text
    formatted_text = []

    # **Hauptüberschrift (h1) extrahieren**
    h1_header = soup.find('h1')
    if h1_header:
        formatted_text.append(f"# {h1_header.get_text(strip=True)}\n")

    # **Alle relevanten Inhalte durchsuchen**
    content_divs = soup.find_all('div', class_='ce-bodytext')

    for content_div in content_divs:
        # **Absätze (<p>) mit Zeilenumbrüchen**
        paragraphs = content_div.find_all('p')
        for paragraph in paragraphs:
            text = paragraph.get_text(separator="\n", strip=True)  # Zeilenumbrüche beibehalten
            if text:
                formatted_text.append(text + "\n")

        # **Listen (<ul> und <ol>)**
        lists = content_div.find_all(['ul', 'ol'])
        for list_tag in lists:
            for li in list_tag.find_all('li'):
                list_item = li.get_text(strip=True)
                formatted_text.append(f"- {list_item}")

        # **Bilder mit Alt-Text extrahieren**
        figures = content_div.find_all('figure', class_='image')
        for figure in figures:
            img = figure.find('img')
            if img and 'alt' in img.attrs:
                img_alt = img['alt']
                img_title = img.get('title', 'Kein Titel verfügbar')
                formatted_text.append(f"\n📷 Bild: {img_alt} - {img_title}\n")

    # **Ordner für die Speicherung erstellen**
    folder_name = "bar-frankfurt"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # **Speicherung der Datei**
    with open(os.path.join(folder_name, output_file), 'w', encoding='utf-8') as file:
        file.write("\n".join(formatted_text))
    
    print(f"Text erfolgreich gespeichert: {os.path.join(folder_name, output_file)}")

def parse_all_websites(json_file):
    # Lade URLs aus JSON-Datei
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Setze eine Menge von URLs, um doppelte Einträge zu vermeiden
    seen_urls = set()
    valid_domain = "bar-frankfurt.de"

    for key, value in data.items():
        original_url = value.get('original_url')
        
        # Überprüfen, ob die URL zur richtigen Domain gehört
        if original_url and valid_domain in urlparse(original_url).netloc and original_url not in seen_urls:
            seen_urls.add(original_url)
            filename = re.sub(r'[\/\\:]', '_', original_url)
            output_file = f"{filename[12:]}.txt"  # URL als Dateiname anpassen
            parse_website(original_url, output_file)

# Beispielaufruf
json_file = "archive_header.json"
parse_all_websites(json_file)
