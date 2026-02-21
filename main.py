import sys
import os
from processors.incoming_processor import IncomingProcessor
from exporters.csv_exporter import export_csv
from exporters.excel_exporter import export_excel
from utils.file_utils import generate_filename, ensure_directory
import pandas as pd

OUTPUT_DIR = "output"

def main():

    # Vérification des arguments
    if len(sys.argv) < 2:
        print("Usage : python main.py <fichier_csv>")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Erreur : le fichier {file_path} n'existe pas.")
        return

    print(f"Traitement du fichier : {file_path}")

    ensure_directory(OUTPUT_DIR)

    # 1️⃣ Traitement incoming
    processor = IncomingProcessor()
    df_processed = processor.process(file_path)

    if df_processed.empty:
        print("Aucune donnée extraite.")
        return

    # 2️⃣ Génération nom dynamique
    extracted_date = getattr(processor, "extracted_date", None)
    filename = generate_filename("incoming", extracted_date)

    # 3️⃣ Chemins de sortie
    csv_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    excel_path = os.path.join(OUTPUT_DIR, f"{filename}.xlsx")

    # 4️⃣ Export
    export_csv(df_processed, csv_path)
    export_excel(df_processed, excel_path)

    print("✅ Traitement terminé")
    print(f"📁 Fichier CSV : {csv_path}")
    print(f"📁 Fichier XLSX : {excel_path}")
    print(f"📊 Nombre de lignes : {len(df_processed)}")


if __name__ == "__main__":
    main()