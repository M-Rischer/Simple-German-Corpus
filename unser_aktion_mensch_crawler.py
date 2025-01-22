import requests
from bs4 import BeautifulSoup

def extract_cleaned_content(url: str) -> str:
    """
    Extrahiert und bereinigt Inhalte einer Website: Überschriften, Absätze, Leerzeichen und Links.
    
    Args:
        url (str): Die URL der Webseite.

    Returns:
        str: Bereinigter Textinhalt.
    """
    try:
        # Anfrage mit User-Agent
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Inhalte sammeln
        content = []
        seen_words = set()  # Für Dopplungen
        
        for element in soup.find_all(["h1", "h2", "h3", "p"]):
            text = element.get_text(" ", strip=True)
            
            # Links entfernen (ganze Wörter, die mit "http" beginnen)
            text = ' '.join(part for part in text.split() if not part.startswith("http"))
            
            # Dopplungen verhindern (z. B. Wörter wie "Inklusion", "Zukunft")
            if text.strip() in seen_words:
                continue
            seen_words.add(text.strip())

            # Überflüssige Leerzeichen bereinigen
            text = text.replace(" .", ".").replace(" ,", ",").strip()

            # Wenn Text vorhanden, hinzufügen
            if text:
                content.append(text)

        # Inhalte mit doppelten Leerzeilen verbinden
        result = "\n\n".join(content)
        
        # Zusätzliche Verarbeitung: Listenpunkte und Absätze formatieren
        result = result.replace("Zum Beispiel:", "\n    Zum Beispiel:")
        result = result.replace("Das bedeutet:", "\n    Das bedeutet:")
        result = result.replace("Denn die Aktion Mensch denkt:", "\n    Denn die Aktion Mensch denkt:")
        result = result.replace("Zum Beispiel:", "\n    Zum Beispiel:")
        
        return result
    
    except requests.exceptions.RequestException as e:
        return f"Fehler beim Abrufen der Seite: {e}"

def save_content_to_txt(content: str, file_name: str):
    """
    Speichert den bereinigten Textinhalt in einer .txt-Datei.

    Args:
        content (str): Der zu speichernde Textinhalt.
        file_name (str): Der Name der .txt-Datei.
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Inhalte wurden in '{file_name}' gespeichert.")

if __name__ == "__main__":
    # Beispiel-URL
    url = "https://www.aktion-mensch.de/leichte-sprache/ueber-uns/arbeiten-bei-der-aktion-mensch"
    
    # Inhalte extrahieren und bereinigen
    extracted_content = extract_cleaned_content(url)
    
    # Ergebnis speichern
    save_content_to_txt(extracted_content, "aktion_mensch_cleaned_content.txt")
