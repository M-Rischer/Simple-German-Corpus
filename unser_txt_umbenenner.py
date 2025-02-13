import os
import pandas as pd
import re
import defaultvalues as dfv

# Pfade anpassen
ORDNER_PFAD = dfv.mdr_txt
EXCEL_DATEI = "Übersicht Texte.xlsx"

# Excel-Tabelle einlesen
df = pd.read_excel(EXCEL_DATEI)

# Funktion zum Normalisieren des URL-Stubs
def normalisiere_url_stub(dateiname):
    return dateiname.replace("__", "/").rsplit(".", 1)[0]

# Dateien im Ordner durchgehen
for dateiname in os.listdir(ORDNER_PFAD):
    alter_pfad = os.path.join(ORDNER_PFAD, dateiname)
    
    # Nur Dateien betrachten
    if not os.path.isfile(alter_pfad):
        continue
    
    # Falls die Datei bereits umbenannt wurde, überspringen
    if re.match(r"\d{4}_(Leichte_Sprache|Standardsprache)\.txt", dateiname):
        continue
    
    url_stub = normalisiere_url_stub(dateiname)
    if not url_stub:
        continue
    
    # Prüfen, ob URL in der Excel-Tabelle vorkommt
    for index, row in df.iterrows():
        if isinstance(row['Leichte Sprache'], str) and url_stub in row['Leichte Sprache']:
            neuer_name = f"{int(row['lfdNr']):04d}_Leichte_Sprache.txt"
        elif isinstance(row['Standardsprache'], str) and url_stub in row['Standardsprache']:
            neuer_name = f"{int(row['lfdNr']):04d}_Standardsprache.txt"
        else:
            continue
        
        neuer_pfad = os.path.join(ORDNER_PFAD, neuer_name)
        
        # Umbenennen, falls der neue Name noch nicht existiert
        if not os.path.exists(neuer_pfad):
            os.rename(alter_pfad, neuer_pfad)
            print(f"Umbenannt: {dateiname} -> {neuer_name}")
        break