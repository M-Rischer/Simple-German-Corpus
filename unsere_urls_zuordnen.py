import pandas as pd
import json

# Dateinamen
excel_file = "Arbeit.xlsx"
json_file = "unser_archive_header_2.json"

# Spaltennummern (basierend auf nullbasiertem Index)
url_columns = [0, 1]  # Spalte 1 und 2 im nullbasierten Index

# Excel-Datei laden
dataframe = pd.read_excel(excel_file)

# JSON-Datei laden
with open(json_file, "r", encoding="utf-8") as f:
    archive_data = json.load(f)

# Neue Spalten für archivierte URLs hinzufügen
for column in url_columns:
    archiv_column_name = f"Archivierte URL (Spalte {column + 1})"

    # Prüfen, ob die archivierte URL bereits vorhanden ist
    dataframe[archiv_column_name] = dataframe.iloc[:, column].map(
        lambda url: (
            archive_data.get(url, {}).get("archivierte_url", "Keine Archiv-URL gefunden")
            if pd.notna(url) else "Keine URL"
        )
    )

# Geänderte Tabelle in eine neue Excel-Datei speichern
output_file = "\u00dcbersicht_Texte_mit_Archiv.xlsx"
dataframe.to_excel(output_file, index=False)

print(f"Die erweiterte Tabelle wurde erfolgreich in {output_file} gespeichert.")
