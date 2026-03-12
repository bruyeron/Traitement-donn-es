import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from config import INPUT_DIR


def download_reports():

    logging.info("Démarrage du téléchargement Vocalcom")

    # Configuration du dossier de téléchargement
    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": os.path.abspath(INPUT_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:

        # 1️⃣ Aller sur Vocalcom
        driver.get("URL_VOCALCOM")

        time.sleep(5)

        # 2️⃣ Connexion
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")

        username.send_keys("TON_LOGIN")
        password.send_keys("TON_PASSWORD")
        password.send_keys(Keys.RETURN)

        logging.info("Connexion Vocalcom envoyée")

        time.sleep(10)

        # 3️⃣ Aller vers la page des rapports
        driver.get("URL_PAGE_RAPPORT")

        time.sleep(5)

        # 4️⃣ Télécharger le rapport
        download_button = driver.find_element(By.ID, "downloadButton")
        download_button.click()

        logging.info("Téléchargement du rapport lancé")

        # 5️⃣ Attendre la fin du téléchargement
        time.sleep(20)

    except Exception as e:

        logging.error(f"Erreur téléchargement Vocalcom : {str(e)}")

    finally:

        driver.quit()

        logging.info("Navigateur fermé")