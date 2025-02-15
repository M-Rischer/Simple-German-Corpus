import requests
from bs4 import BeautifulSoup
import json
import os
import time
import urllib.request
import urllib.error

# Funktion zum Abrufen und Parsen der Worterklärungsseite
def get_word_explanation(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrahiere die Erklärung aus dem <p> Tag mit der Klasse 'text'
        explanation_tag = soup.find('p', class_='text')
        if explanation_tag:
            explanation = explanation_tag.get_text(separator='\n').strip()
        else:
            explanation = "Keine Erklärung gefunden"
        
        return explanation
    except Exception as e:
        print(f"Fehler beim Abrufen der Erklärung von {url}: {e}")
        return "Fehler beim Abrufen der Erklärung"

# Funktion zum Abrufen der Links zu den Buchstaben
def get_letter_urls(glossary_url):
    try:
        response = requests.get(glossary_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrahiere alle Links zu den Buchstaben
        letter_links = soup.find_all('a', class_='pageItem')
        letter_urls = {}
        
        for link in letter_links:
            letter = link.get_text().strip()
            if letter:  # Stelle sicher, dass der Buchstabe nicht leer ist
                full_url = 'https://www.mdr.de' + link['href']
                letter_urls[letter] = full_url
        
        return letter_urls
    except Exception as e:
        print(f"Fehler beim Abrufen der Buchstaben-Links: {e}")
        return {}

# Funktion zum Abrufen der Wörter und Links aus der Glossar-Seite eines bestimmten Buchstabens
def get_words_from_glossary_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrahiere alle Links, die zu den Wortgruppen führen
        word_links = soup.find_all('a', class_='headline')
        words = []
        for link in word_links:
            word_text = link.get_text().strip()  # Extrahiere das Wort
            word_url = 'https://www.mdr.de' + link['href']  # Erstelle den vollen Link
            words.append((word_text, word_url))
        
        return words
    except Exception as e:
        print(f"Fehler beim Abrufen der Wörter von {url}: {e}")
        return []

# Funktion zum Speichern des aktuellen Fortschritts in zwei JSON-Dateien
def save_progress(all_words, all_urls):
    # Speichern der Worterklärungen
    with open('unser_glossary_explanations.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_words, json_file, ensure_ascii=False, indent=4)
    
    # Speichern der URLs
    with open('unser_glossary_urls.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_urls, json_file, ensure_ascii=False, indent=4)

# Funktion zum Laden des Fortschritts (falls vorhanden)
def load_progress():
    all_words = {}
    all_urls = {}

    # Wenn die Erklärung-JSON-Datei existiert, lade den Fortschritt
    if os.path.exists('unser_glossary_explanations.json'):
        with open('unser_glossary_explanations.json', 'r', encoding='utf-8') as json_file:
            all_words = json.load(json_file)
    
    # Wenn die URL-JSON-Datei existiert, lade die URLs
    if os.path.exists('unser_glossary_urls.json'):
        with open('unser_glossary_urls.json', 'r', encoding='utf-8') as json_file:
            all_urls = json.load(json_file)
    
    return all_words, all_urls

# Funktion zum Archivieren der URL mit Zeitstempel
def archive_url_with_retries(url, max_retries=5, delay=3):
    """Archiviert eine URL und gibt die archivierte URL mit Zeitstempel zurück."""
    for attempt in range(1, max_retries + 1):
        try:
            # Baue die URL zur archivierten Version auf Archive.org
            archive_url = f"http://web.archive.org/save/{url}"
            # Versuche die URL zu archivieren
            with urllib.request.urlopen(archive_url) as f:
                # Die archivierte URL enthält den Zeitstempel und wird als f.url zurückgegeben
                timestamp = f.url.split('/web/')[1].split('/')[0]
                archived_url = f"http://web.archive.org/web/{timestamp}/{url}"
                print(f"Neu archiviert: {archived_url}")
                return archived_url
        except urllib.error.HTTPError as err:
            print(f"Fehler beim Archivieren der URL {url}: {err}, Versuch {attempt} von {max_retries}")
        except urllib.error.URLError as err:
            print(f"Netzwerkfehler bei {url}: {err}, Versuch {attempt} von {max_retries}")
        
        # Warten, bevor der nächste Versuch gestartet wird
        time.sleep(delay)
    
    print(f"Archivierung für {url} nach {max_retries} Versuchen fehlgeschlagen.")
    return None

# Hauptfunktion, die das Glossar von A bis Z durchgeht
def create_glossary_json():
    glossary_url = 'https://www.mdr.de/nachrichten-leicht/woerterbuch/glossar-leichte-sprache-100_inheritancecontext-header_letter-1_numberofelements-1_zc-a093b89c.html#letternavi'
    
    # Lade den bisherigen Fortschritt
    all_words, all_urls = load_progress()

    # Abrufen der Links zu den Buchstaben (A bis Z)
    letter_urls = get_letter_urls(glossary_url)

    # Durchlaufe alle Buchstaben und ihre Seiten
    for letter, letter_url in letter_urls.items():
        print(f"Verarbeite Seite für den Buchstaben: {letter} - URL: {letter_url}")
        
        # Abrufe alle Wörter von der Seite des jeweiligen Buchstabens
        words = get_words_from_glossary_page(letter_url)
        
        for word, word_url in words:
            if word not in all_words:  # Nur Wörter verarbeiten, die noch nicht gespeichert wurden
                print(f"Verarbeite Wort: {word}, URL: {word_url}")
                
                # Abrufen der Erklärung
                explanation = get_word_explanation(word_url)
                
                # Hinzufügen der Erklärung zum all_words
                all_words[word] = {
                    "leichte Sprache": word,
                    "Standardsprache": explanation
                }
                
                # Archivierte URL abrufen
                archived_url = archive_url_with_retries(word_url)
                if archived_url:
                    all_urls[word] = {
                        "url": word_url,
                        "archivierte url": archived_url
                    }
                
                # Fortschritt speichern
                save_progress(all_words, all_urls)

    print("Glossar-Daten gespeichert.")

# Funktion ausführen
create_glossary_json()
