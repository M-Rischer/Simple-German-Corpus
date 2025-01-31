import pandas as pd
import urllib.robotparser
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time

headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }

def is_valid_url(url: str) -> bool:
    """Prüft, ob ein String eine gültige URL ist."""
    try:
        url = url.strip()
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_meta_tag_forbidden(url: str) -> bool:
    """Prüft, ob das Meta-Tag <meta name="robots" content="noindex, nofollow"> vorhanden ist."""
    for _ in range(3):  # Bis zu 3 Versuche
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'robots', 'content': 'noindex, nofollow'})
            return meta_tag is not None
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen der URL {url}: {e}")
            time.sleep(2)  # Warten vor erneutem Versuch
    return False


def is_x_robots_tag_forbidden(url: str) -> bool:
    """Prüft, ob der X-Robots-Tag im HTTP-Header den Wert 'noindex, nofollow' hat."""
    for _ in range(3):  # Bis zu 3 Versuche
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            x_robots_tag = response.headers.get('X-Robots-Tag', '')
            return 'noindex' in x_robots_tag and 'nofollow' in x_robots_tag
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen des X-Robots-Tags für {url}: {e}")
            time.sleep(2)  # Warten vor erneutem Versuch
    return False


def is_crawling_allowed(url: str, user_agent: str = "*") -> str:
    """
    Prüft, ob Crawling erlaubt ist, und versucht, auf eine höhere Domain zu gehen, falls nötig.
    """
    if not is_valid_url(url):
        return ""

    parsed_url = urlparse(url)
    domains_to_check = []
    # Subdomains schrittweise entfernen, bis zur Root-Domain
    domain_parts = parsed_url.netloc.split('.')
    for i in range(len(domain_parts) - 1):
        higher_domain = ".".join(domain_parts[i:])
        domains_to_check.append(f"{parsed_url.scheme}://{higher_domain}")

    for domain in domains_to_check:
        robots_url = f"{domain}/robots.txt"
        for _ in range(3):  # Bis zu 3 Versuche pro Domain
            try:
                response = requests.get(robots_url, headers=headers, timeout=10)
                if response.status_code == 404:
                    # Prüfen, ob ein Meta-Tag oder X-Robots-Tag das Crawling verbietet
                    if is_meta_tag_forbidden(url) or is_x_robots_tag_forbidden(url):
                        return "Nein"
                    return "Ja"
                elif response.status_code == 200:
                    rp = urllib.robotparser.RobotFileParser()
                    rp.set_url(robots_url)
                    rp.read()
                    if rp.can_fetch(user_agent, url):
                        return "Ja"
                    return "Nein"
            except requests.RequestException as e:
                print(f"Fehler beim Abrufen von {robots_url}: {e}")
                time.sleep(2)  # Warten vor erneutem Versuch
    return "Nein"  # Wenn alle Domains nicht zugänglich sind, Crawling verbieten


def process_excel(input_file: str, output_file: str, txt_file: str, user_agent: str = "*"):
    """
    Liest URLs aus einer Excel-Datei, prüft die Crawling-Erlaubnis und speichert die Ergebnisse.
    """
    df = pd.read_excel(input_file)
    urls_col1 = df.iloc[:, 0]  # Erste Spalte
    robots_urls = set()
    results_col1 = []

    for url in urls_col1:
        if pd.notna(url):
            url = url.strip()
            result = is_crawling_allowed(url, user_agent)
            results_col1.append(result)

            if result == "Ja":
                parsed_url = urlparse(url)
                robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
                try:
                    response = requests.get(robots_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        robots_urls.add(robots_url)
                except requests.RequestException:
                    pass
        else:
            results_col1.append("")

    while len(results_col1) < len(df):
        results_col1.append("")
    df["Crawling erlaubt (Spalte 1)"] = results_col1

    df.to_excel(output_file, index=False)
    print(f"Ergebnisse gespeichert in {output_file}")

    with open(txt_file, "w") as f:
        for robots_url in sorted(robots_urls):
            f.write(f"{robots_url}\n")
    print(f"robots.txt Links gespeichert in {txt_file}")


if __name__ == "__main__":
    input_excel = "URLs.xlsx"
    output_excel = "URLs_crawling_results.xlsx"
    output_txt = "robots_links.txt"
    process_excel(input_excel, output_excel, output_txt)
