import pandas as pd

# Dateinamen der Excel-Dateien
file_1 = "URLs.xlsx"
file_2 = "Übersicht Texte.xlsx"

# Spaltennamen der archivierten URLs in den beiden Dateien
archived_column_file_1 = "Archivierte URL"  # Spalte in URL.xlsx
possible_columns_file_2 = ["Leichte Sprache", "Standardsprache"]  # Beide Spalten in Übersicht Texte.xlsx

# Excel-Dateien laden
data_1 = pd.read_excel(file_1)
data_2 = pd.read_excel(file_2)

# Archivierte URLs aus file_1 extrahieren
archived_urls_file_1 = set(data_1[archived_column_file_1].dropna())

# Archivierte URLs aus beiden möglichen Spalten von file_2 extrahieren
archived_urls_file_2 = set()
for col in possible_columns_file_2:
    if col in data_2.columns:  # Nur vorhandene Spalten berücksichtigen
        archived_urls_file_2.update(data_2[col].dropna())

# URLs finden, die nur in file_1 enthalten sind
unique_urls_in_file_1 = archived_urls_file_1 - archived_urls_file_2

# Ergebnis ausgeben
if unique_urls_in_file_1:
    print("Die folgenden URLs sind nur in URL.xlsx vorhanden:")
    for url in unique_urls_in_file_1:
        print(url)
else:
    print("Keine zusätzlichen URLs in URL.xlsx gefunden.")
