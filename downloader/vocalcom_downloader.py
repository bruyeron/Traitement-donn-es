import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from config import INPUT_DIR


def download_reports():

    logging.info("Démarrage du téléchargement Vocalcom")

    # 📁 Configuration du dossier de téléchargement
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

    wait = WebDriverWait(driver, 20)

    try:

        driver.get("https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/login")

        logging.info("Page Vocalcom ouverte")

        # -------------------------------------------------
        # Entrer le LOGIN
        # -------------------------------------------------

        username = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        username.send_keys("WFM")
        username.send_keys(Keys.RETURN)

        logging.info("Login envoyé")

        # -------------------------------------------------
        # Entrer le PASSWORD
        # -------------------------------------------------

        password = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        password.send_keys("azer")
        password.send_keys(Keys.RETURN)

        logging.info("Mot de passe envoyé")

        # -------------------------------------------------
        # Attendre chargement du dashboard
        # -------------------------------------------------

        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        logging.info("Connexion réussie")

        # Eto ny asina anle chemin maka anle rapport amzay zany

        time.sleep(20)

        logging.info("Téléchargement terminé")

    except Exception as e:

        logging.error(f"Erreur téléchargement Vocalcom : {str(e)}")

    finally:

        driver.quit()

        logging.info("Navigateur fermé")