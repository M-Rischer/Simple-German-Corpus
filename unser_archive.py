import os
import time
import json
import pandas as pd
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

# Funktion zur Validierung von URLs
def is_valid_url(url):
    """Prüft, ob ein String eine gültige URL ist."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Beispiel-Excel-Datei einlesen
def read_urls_from_excel(file_path):
    """Liest URLs aus den Spalten 'Leichte Sprache' und 'Standardsprache' und gibt sie als Liste zurück."""
    df = pd.read_excel(file_path)
    print("Spalten in der Excel-Datei:", df.columns)  # Zeigt die Spaltennamen an
    urls = []

    if 'Leichte Sprache' in df.columns:
        urls.extend([url for url in df['Leichte Sprache'].dropna() if is_valid_url(url)])

    if 'Standardsprache' in df.columns:
        urls.extend([url for url in df['Standardsprache'].dropna() if is_valid_url(url)])

    return urls

# Archivierungslogik bei Archive.org
def archive_url(url, archive_header):
    """Archiviert eine URL auf archive.org und fügt die Daten in archive_header ein."""
    try:
        # Versucht, die URL zu archivieren
        with urllib.request.urlopen(f"http://web.archive.org/save/{url}") as f:
            print(f"Neu archiviert: {f.url}")
            # Archivierte URL und Metadaten speichern
            archive_header[url] = {
                "archivierte_url": f.url,
                "original_url": url
            }
        return True
    except urllib.error.HTTPError as err:
        print(f"Fehler beim Archivieren der URL {url}: {err}")
        return False
    except urllib.error.URLError as err:
        print(f"Netzwerkfehler bei {url}: {err}")
        return False

def main(excel_file_path, archive_header_file):
    # Archive Header laden oder initialisieren
    if os.path.exists(archive_header_file):
        with open(archive_header_file, "r") as f:
            archive_header = json.load(f)
    else:
        archive_header = {}

    # URLs aus Excel-Datei lesen
    urls = read_urls_from_excel(excel_file_path)

    # URLs archivieren
    for url in urls:
        if url not in archive_header:
            print(f"Archiviere: {url}")
            archived = False
            retries = 0
            while not archived and retries < 5:
                archived = archive_url(url, archive_header)
                if not archived:
                    retries += 1
                    print(f"Versuche erneut ({retries}/5): {url}")
                    time.sleep(60)  # Wartezeit vor erneutem Versuch

            # Archive Header speichern, wenn URL archiviert wurde
            if archived:
                with open(archive_header_file, "w") as f:
                    json.dump(archive_header, f, indent=4)
        else:
            print(f"URL bereits archiviert: {url}")

if __name__ == "__main__":
    # Beispiel für den Aufruf der Funktion
    excel_file_path = "C:/Users/Rischer/OneDrive - Helmut-Schmidt-Universität/Dokumente/Lebenshilfe Projekt/Übersicht Texte.xlsx"  # Pfad zur Excel-Datei mit den URLs
    archive_header_file = "archive_header.json"  # Pfad zur JSON-Datei, in der die archivierten URLs gespeichert werden
    main(excel_file_path, archive_header_file)
