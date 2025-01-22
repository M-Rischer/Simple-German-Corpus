import os
import time
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

# URLs aus einer Textdatei einlesen
def read_urls_from_txt(file_path):
    """Liest URLs aus einer .txt-Datei und gibt sie als Liste zurück."""
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file.readlines() if is_valid_url(line.strip())]
    return urls

# Archivierungslogik bei Archive.org
def archive_url(url):
    """Archiviert eine URL auf archive.org und gibt die archivierte URL zurück."""
    try:
        # Versucht, die URL zu archivieren
        with urllib.request.urlopen(f"http://web.archive.org/save/{url}") as f:
            print(f"Neu archiviert: {f.url}")
            return f.url
    except urllib.error.HTTPError as err:
        print(f"Fehler beim Archivieren der URL {url}: {err}")
        return None
    except urllib.error.URLError as err:
        print(f"Netzwerkfehler bei {url}: {err}")
        return None

def main(txt_file_path, output_file_path):
    # URLs aus der Textdatei lesen
    urls = read_urls_from_txt(txt_file_path)

    # Liste für archivierte URLs
    archived_urls = []

    # URLs archivieren
    for url in urls:
        print(f"Archiviere: {url}")
        archived_url = None
        retries = 0
        while archived_url is None and retries < 5:
            archived_url = archive_url(url)
            if archived_url is None:
                retries += 1
                print(f"Versuche erneut ({retries}/5): {url}")
                time.sleep(60)  # Wartezeit vor erneutem Versuch

        if archived_url:
            archived_urls.append(f"{url} -> {archived_url}")

    # Archivierte URLs in eine Textdatei schreiben
    if archived_urls:
        with open(output_file_path, "w") as f:
            f.write("\n".join(archived_urls))
        print(f"Archivierte URLs wurden in {output_file_path} gespeichert.")
    else:
        print("Keine URLs archiviert.")

if __name__ == "__main__":
    # Beispiel für den Aufruf der Funktion
    txt_file_path = "robots_links.txt"  # Pfad zur .txt-Datei mit den URLs
    output_file_path = "archivierte_robots_links.txt"  # Pfad zur neuen Textdatei, in der die archivierten URLs gespeichert werden
    main(txt_file_path, output_file_path)
