import pandas as pd
import urllib.robotparser
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def is_valid_url(url: str) -> bool:
    """
    Prüft, ob ein String eine gültige URL ist.

    Args:
        url (str): Der zu überprüfende String.

    Returns:
        bool: True, wenn es eine gültige URL ist, sonst False.
    """
    try:
        # Entfernen von möglichen Leerzeichen oder unsichtbaren Zeichen
        url = url.strip()
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def is_meta_tag_forbidden(url: str) -> bool:
    """
    Prüft, ob das Meta-Tag <meta name="robots" content="noindex, nofollow">
    auf der Seite vorhanden ist, wenn keine robots.txt existiert.

    Args:
        url (str): Die URL der Seite, die geprüft werden soll.

    Returns:
        bool: True, wenn das Meta-Tag gefunden wird, ansonsten False.
    """
    try:
        # HTML-Inhalt der Seite holen
        response = requests.get(url)
        response.raise_for_status()  # Überprüft, ob die Seite erfolgreich geladen wurde

        # BeautifulSoup verwenden, um den HTML-Code zu durchsuchen
        soup = BeautifulSoup(response.text, 'html.parser')

        # Suchen nach dem Meta-Tag
        meta_tag = soup.find('meta', attrs={'name': 'robots', 'content': 'noindex, nofollow'})
        
        if meta_tag:
            return True  # Meta-Tag gefunden, Crawling verboten
        return False  # Meta-Tag nicht gefunden
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der URL {url}: {e}")
        return False

def is_crawling_allowed(url: str, user_agent: str = "*") -> str:
    """
    Prüft, ob Crawling der URL laut robots.txt erlaubt ist und gibt den Link zum robots.txt-File aus.
    Wenn keine robots.txt existiert, wird das Meta-Tag geprüft.

    Args:
        url (str): Die URL der Webseite, die geprüft werden soll.
        user_agent (str): Der User-Agent, für den die Regel geprüft wird. Standard ist "*".
    
    Returns:
        str: "Ja", wenn Crawling erlaubt ist, "Nein", wenn es nicht erlaubt ist.
             Leerstring, wenn die URL ungültig ist oder keine robots.txt vorhanden ist.
    """
    if not is_valid_url(url):
        return ""
    
    try:
        # Domain aus URL extrahieren
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

        # Versuchen, robots.txt zu lesen
        response = requests.get(robots_url)
        if response.status_code == 404:
            # Wenn 404 Fehler, robots.txt existiert nicht
            if is_meta_tag_forbidden(url):
                return "Nein"  # Meta-Tag gefunden, Crawling verboten
            return "Ja"  # Kein Meta-Tag gefunden, Crawling erlaubt
        elif response.status_code == 200:
            # Wenn robots.txt gefunden wurde, analysieren
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            if rp.can_fetch(user_agent, url):
                return "Ja"  # Crawling erlaubt laut robots.txt
            else:
                return "Nein"  # Crawling verboten laut robots.txt
        else:
            return "Nein"  # Für alle anderen HTTP-Fehler

    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der URL {url}: {e}")
        return ""

def process_excel(input_file: str, output_file: str, txt_file: str, user_agent: str = "*"):
    """
    Liest URLs aus einer Excel-Tabelle, prüft die Crawling-Erlaubnis und speichert die Ergebnisse.

    Args:
        input_file (str): Pfad zur Eingabe-Excel-Datei.
        output_file (str): Pfad zur Ausgabe-Excel-Datei.
        txt_file (str): Pfad zur Textdatei für die robots.txt Links.
        user_agent (str): Der User-Agent, für den die Regeln geprüft werden. Standard ist "*".
    """
    # Excel-Datei laden
    df = pd.read_excel(input_file)

    # Annahme: URLs sind in der ersten und zweiten Spalte
    if df.shape[1] < 2:
        print("Die Eingabetabelle benötigt mindestens zwei Spalten für URLs.")
        return

    urls_col1 = df.iloc[:, 0]  # Erste Spalte
    urls_col2 = df.iloc[:, 1]  # Zweite Spalte

    # Set zum Speichern von einzigartigen robots.txt Links
    robots_urls = set()

    # Ergebnisse prüfen und speichern
    results_col1 = []
    results_col2 = []
    for url in urls_col1:
        if pd.notna(url):
            url = url.strip()  # Entfernen von möglichen Leerzeichen
            result = is_crawling_allowed(url, user_agent)
            results_col1.append(result)
            if result == "Ja":  # Nur speichern, wenn Crawling erlaubt ist und robots.txt existiert
                parsed_url = urlparse(url)
                robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
                # Nur URLs mit bestehendem robots.txt in robots_links.txt speichern
                try:
                    response = requests.get(robots_url)
                    if response.status_code == 200:
                        robots_urls.add(robots_url)
                except requests.RequestException:
                    pass
        else:
            results_col1.append("")  # Leerer Eintrag, wenn URL fehlt

    for url in urls_col2:
        if pd.notna(url):
            url = url.strip()  # Entfernen von möglichen Leerzeichen
            result = is_crawling_allowed(url, user_agent)
            results_col2.append(result)
            if result == "Ja":  # Nur speichern, wenn Crawling erlaubt ist und robots.txt existiert
                parsed_url = urlparse(url)
                robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
                # Nur URLs mit bestehendem robots.txt in robots_links.txt speichern
                try:
                    response = requests.get(robots_url)
                    if response.status_code == 200:
                        robots_urls.add(robots_url)
                except requests.RequestException:
                    pass
        else:
            results_col2.append("")  # Leerer Eintrag, wenn URL fehlt

    # Sicherstellen, dass die Listen die gleiche Länge wie der DataFrame haben
    while len(results_col1) < len(df):
        results_col1.append("")  # Füge leere Werte hinzu, wenn zu wenig Werte in Spalte 1 sind
    while len(results_col2) < len(df):
        results_col2.append("")  # Füge leere Werte hinzu, wenn zu wenig Werte in Spalte 2 sind

    # Ergebnisse zum DataFrame hinzufügen
    df["Crawling erlaubt (Spalte 1)"] = results_col1
    df["Crawling erlaubt (Spalte 2)"] = results_col2

    # Ausgabe in neue Excel-Datei speichern
    df.to_excel(output_file, index=False)
    print(f"Ergebnisse gespeichert in {output_file}")

    # Speichern der einzigartigen robots.txt Links in eine .txt-Datei
    with open(txt_file, "w") as f:
        for robots_url in sorted(robots_urls):
            f.write(f"{robots_url}\n")
    print(f"robots.txt Links gespeichert in {txt_file}")


if __name__ == "__main__":
    input_excel = "URLs.xlsx"  # Eingabe-Excel-Datei mit URLs
    output_excel = "URLs_results.xlsx"  # Ausgabe-Excel-Datei mit Ergebnissen
    output_txt = "robots_links.txt"  # Datei für die gespeicherten robots.txt Links
    process_excel(input_excel, output_excel, output_txt)
