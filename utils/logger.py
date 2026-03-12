import logging
import os


def setup_logger():

    # créer dossier logs si inexistant
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("pipeline_logger")
    logger.setLevel(logging.INFO)

    # éviter les doublons
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # log fichier
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    # log console
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger