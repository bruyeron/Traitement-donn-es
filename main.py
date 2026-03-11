import sys
import os

from processors.distribution_etat_agent import DistributionEtatAgent
from processors.distribution_appel import DistributionAppel

from exporters.csv_exporter import export_csv
from exporters.excel_exporter import export_excel

from utils.file_utils import generate_filename, ensure_directory
from utils.converter import convert_xls_to_csv


INPUT_DIR = "input"
OUTPUT_DIR = "output"
TEMP_DIR = "temp"


def choose_processor():
    """
    Demande à l'utilisateur quel traitement effectuer
    """

    print("\nChoisissez le type de traitement :")
    print("1 - Distribution Etat Agent")
    print("2 - Distribution Appel")

    choice = input("Votre choix : ").strip()

    if choice == "1":
        return DistributionEtatAgent(), "distribution_etat_agent"

    elif choice == "2":
        return DistributionAppel(), "distribution_appel"

    else:
        print("❌ Choix invalide")
        sys.exit(1)


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

    # Choix du processor
    processor, processor_name = choose_processor()

    print("\n🔄 Conversion XLS → CSV...")
    csv_path = convert_xls_to_csv(xls_path, TEMP_DIR)

    print("🚀 Traitement du CSV converti...")
    df_processed = processor.process(csv_path)

    if df_processed.empty:
        print("⚠️ Aucune donnée extraite.")
        sys.exit(0)

    ensure_directory(OUTPUT_DIR)

    # Nom du fichier basé sur le traitement
    filename = generate_filename(processor_name, processor.extracted_date)

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