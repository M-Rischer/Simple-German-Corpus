import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse, unquote
import re

def parse_website(url, output_file):
    # Bereinige die URL
    url = unquote(url).strip()

    # HTTP-Anfrage senden
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
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

    # **Textbereiche analysieren**
    text_sections = soup.find_all('div', class_='running_text')

    for section in text_sections:
        for element in section.find_all(['p', 'h3', 'h4', 'ul', 'strong', 'br']):
            if element.name == 'p':
                # Prüfe auf fett formatierten Text
                strong_text = element.find('strong')
                if strong_text:
                    text = f"**{strong_text.get_text(strip=True)}**\n"
                    formatted_text.append(text)
                else:
                    text = element.get_text(separator="\n", strip=True)
                    formatted_text.append(text + "\n")

            elif element.name == 'h3':
                formatted_text.append(f"## {element.get_text(strip=True)}\n")

            elif element.name == 'h4':
                formatted_text.append(f"### {element.get_text(strip=True)}\n")

            elif element.name == 'ul':
                for li in element.find_all('li'):
                    formatted_text.append(f"- {li.get_text(strip=True)}")

            elif element.name == 'br':
                formatted_text.append("\n")

    # **Ordner für die Speicherung erstellen**
    folder_name = "lvr"
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
    valid_domain = "lvr.de"

    for key, value in data.items():
        original_url = value.get('original_url')
        
        # Überprüfen, ob die URL zur richtigen Domain gehört
        if original_url and valid_domain in urlparse(original_url).netloc and original_url not in seen_urls:
            seen_urls.add(original_url)
            filename = re.sub(r'[\/\\:]', '_', original_url)
            output_file = f"{filename[8:]}.txt"  # URL als Dateiname anpassen
            parse_website(original_url, output_file)

# Beispielaufruf
json_file = "archive_header.json"
parse_all_websites(json_file)
