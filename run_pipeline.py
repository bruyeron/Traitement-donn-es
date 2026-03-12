import logging

from downloader.vocalcom_downloader import download_reports
from main import main as process_pipeline


def run():

    logging.info("===== PIPELINE COMPLET =====")

    # 1️⃣ Télécharger les rapports
    download_reports()

    # 2️⃣ Lancer ton pipeline existant
    process_pipeline()

    logging.info("===== FIN DU PIPELINE =====")


if __name__ == "__main__":
    run()