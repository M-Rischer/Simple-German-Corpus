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

# Prüft, ob die URL ein Link ist, der bereits archiviert wurde
def is_archived_url(url):
    """
    Überprüft, ob eine URL ein archivierter Link von web.archive.org ist.
    """
    return url.startswith("http://web.archive.org/web/")

# URLs aus einer Excel-Datei lesen
def read_urls_from_excel(file_path):
    """Liest URLs aus den Spalten 'Leichte Sprache' und 'Standardsprache' und gibt sie als Liste zurück."""
    try:
        df = pd.read_excel(file_path)
        print("Spalten in der Excel-Datei:", df.columns)  # Zeigt die Spaltennamen an
        urls = []

        if 'Leichte Sprache' in df.columns:
            urls.extend([url for url in df['Leichte Sprache'].dropna() if is_valid_url(url)])

        if 'Standardsprache' in df.columns:
            urls.extend([url for url in df['Standardsprache'].dropna() if is_valid_url(url)])

        return urls
    except Exception as e:
        print(f"Fehler beim Lesen der Excel-Datei: {e}")
        return []

# Archivierungslogik bei Archive.org
def archive_url(url, archive_header):
    """Archiviert eine URL auf archive.org und fügt die Daten in archive_header ein."""
    try:
        with urllib.request.urlopen(f"http://web.archive.org/save/{url}") as f:
            print(f"Neu archiviert: {f.url}")
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

def load_archive_header(file_path):
    """Lädt die archivierten URLs aus einer JSON-Datei oder gibt ein leeres Dictionary zurück."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warnung: Die Datei {file_path} ist keine gültige JSON-Datei. Sie wird überschrieben.")
            return {}
    return {}

def save_archive_header(file_path, archive_header):
    """Speichert das Archivierungsprotokoll in einer JSON-Datei."""
    try:
        with open(file_path, "w") as f:
            json.dump(archive_header, f, indent=4)
    except Exception as e:
        print(f"Fehler beim Speichern der JSON-Datei {file_path}: {e}")

def main(excel_file_path, archive_header_file):
    # Archivierungsprotokoll laden
    archive_header = load_archive_header(archive_header_file)

    # URLs aus der Excel-Datei lesen
    urls = read_urls_from_excel(excel_file_path)

    # URLs archivieren
    for url in urls:
        if is_archived_url(url):
            print(f"Überspringe bereits archivierte URL: {url}")
            continue

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

            # Archivierungsprotokoll speichern, wenn URL erfolgreich archiviert wurde
            if archived:
                save_archive_header(archive_header_file, archive_header)
        else:
            print(f"URL bereits archiviert: {url}")

if __name__ == "__main__":
    # Beispiel für den Aufruf der Funktion
    excel_file_path = "Übersicht Texte.xlsx"  # Pfad zur Excel-Datei mit den URLs
    archive_header_file = "unser_archive_header.json"  # Pfad zur JSON-Datei, in der die archivierten URLs gespeichert werden
    main(excel_file_path, archive_header_file)