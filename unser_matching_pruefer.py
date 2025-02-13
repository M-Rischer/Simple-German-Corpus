import json
from collections import defaultdict
import defaultvalues as dfv

# JSON-Datei laden
def check_duplicate_matching_files(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matching_files_count = defaultdict(list)
    
    # Alle matching_files sammeln
    for key, value in data.items():
        matching_files = value.get("matching_files", [])
        for file in matching_files:
            matching_files_count[file].append(key)
    
    # Doppelte matching_files ausgeben
    duplicates_found = False
    for file, entries in matching_files_count.items():
        if len(entries) > 1:
            duplicates_found = True
            print(f"Das matching_file '{file}' kommt mehrfach vor")
    
    if not duplicates_found:
        print("Keine doppelten matching_files gefunden.")

# Beispielaufruf
check_duplicate_matching_files(f"{dfv.dataset_location}/www.mdr.de/parsed_header2025.json")
