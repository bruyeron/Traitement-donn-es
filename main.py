import sys
import os
from processors.distribution_etat_agent import DistributionEtatAgent
from exporters.csv_exporter import export_csv
from exporters.excel_exporter import export_excel
from utils.file_utils import generate_filename, ensure_directory
from utils.converter import convert_xls_to_csv

INPUT_DIR = "input"
OUTPUT_DIR = "output"
TEMP_DIR = "temp"

def main():

    if len(sys.argv) < 2:
        print("Usage : python main.py <nom_fichier.xls>")
        sys.exit(1)

    file_name = sys.argv[1]
    xls_path = os.path.join(INPUT_DIR, file_name)

    if not os.path.isfile(xls_path):
        print("❌ Fichier introuvable dans input/")
        sys.exit(1)

    if not file_name.lower().endswith(".xls"):
        print("❌ Le fichier doit être en .xls")
        sys.exit(1)

    print("🔄 Conversion XLS → CSV...")
    csv_path = convert_xls_to_csv(xls_path, TEMP_DIR)

    print("🚀 Traitement du CSV converti...")

    processor = DistributionEtatAgent()
    df_processed = processor.process(csv_path)

    if df_processed.empty:
        print("⚠️ Aucune donnée extraite.")
        sys.exit(0)

    ensure_directory(OUTPUT_DIR)

    filename = generate_filename("distribution_etat_agent")

    csv_output = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    excel_output = os.path.join(OUTPUT_DIR, f"{filename}.xlsx")

    export_csv(df_processed, csv_output)
    export_excel(df_processed, excel_output)

    print("\n✅ Traitement terminé")
    print(f"📁 CSV : {csv_output}")
    print(f"📁 XLSX : {excel_output}")
    print(f"📊 Lignes : {len(df_processed)}")


if __name__ == "__main__":
    main()