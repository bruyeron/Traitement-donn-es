import os

from config import INPUT_DIR, OUTPUT_DIR, TEMP_DIR

from utils.file_utils import generate_filename, ensure_directory
from utils.converter import convert_xls_to_csv
from utils.logger import setup_logger

from exporters.csv_exporter import export_csv
from exporters.excel_exporter import export_excel

from detectors.processor_detector import detect_processor


# Initialisation du logger
logger = setup_logger()


def main():

    logger.info("Demarrage du pipeline de traitement")

    ensure_directory(OUTPUT_DIR)

    files = os.listdir(INPUT_DIR)

    for file in files:

        # On ignore les fichiers non xls
        if not file.lower().endswith(".xls"):
            continue

        try:

            xls_path = os.path.join(INPUT_DIR, file)

            print(f"\n📂 Traitement du fichier : {file}")
            logger.info(f"Traitement du fichier : {file}")

            print("🔄 Conversion XLS → CSV...")
            logger.info("Conversion XLS → CSV")

            csv_path = convert_xls_to_csv(xls_path, TEMP_DIR)

            # Détection automatique du processor
            processor, processor_name = detect_processor(csv_path)
            logger.info(f"Processor detecte : {processor_name}")

            print("🚀 Traitement du CSV converti...")
            df_processed = processor.process(csv_path)

            if df_processed.empty:
                print("⚠️ Aucune donnée extraite.")
                logger.warning(f"Aucune donnee extraite pour {file}")
                continue

            # Génération du nom du fichier
            filename = generate_filename(processor_name, processor.extracted_date)

            csv_output = os.path.join(OUTPUT_DIR, f"{filename}.csv")
            excel_output = os.path.join(OUTPUT_DIR, f"{filename}.xlsx")

            export_csv(df_processed, csv_output)
            export_excel(df_processed, excel_output)

            print("✅ Traitement terminé")
            print(f"📁 CSV : {csv_output}")
            print(f"📁 XLSX : {excel_output}")
            print(f"📊 Lignes : {len(df_processed)}")

            logger.info(f"Export CSV : {csv_output}")
            logger.info(f"Export XLSX : {excel_output}")
            logger.info(f"Lignes traitees : {len(df_processed)}")

        except Exception as e:

            print(f"❌ Erreur lors du traitement de {file}")
            logger.error(f"Erreur sur {file} : {str(e)}")


if __name__ == "__main__":
    main()