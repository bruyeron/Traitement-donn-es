import logging
import sys
from downloader.vocalcom_downloader import download_reports
from main import main as process_pipeline

# Configuration du logging pour voir ce qui se passe dans la console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run():
    logging.info("===== DÉMARRAGE DU PIPELINE COMPLET =====")

    try:
        # 1. Télécharger les rapports
        logging.info("Étape 1 : Récupération des données sur Vocalcom...")
        download_reports()
        
        # 2. Lancer ton pipeline existant
        logging.info("Étape 2 : Lancement du traitement des données...")
        process_pipeline()

        logging.info("===== PIPELINE TERMINÉ AVEC SUCCÈS =====")

    except Exception as e:
        logging.error(f"===== ÉCHEC DU PIPELINE : {str(e)} =====")
        sys.exit(1) # Quitte avec une erreur si quelque chose lâche

if __name__ == "__main__":
    run()