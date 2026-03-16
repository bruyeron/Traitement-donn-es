# downloader/vocalcom_downloader_playwright.py

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from config import INPUT_DIR

load_dotenv()

def download_reports():
    logging.info("Démarrage du téléchargement Vocalcom")

    download_path = os.path.abspath(INPUT_DIR)
    Path(download_path).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Lancer le navigateur Chromium (non-headless pour visualiser)
        browser = p.chromium.launch(headless=False)
        # Créer un contexte autorisant les téléchargements
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # -------------------------------------------------
            # Page login
            # -------------------------------------------------
            page.goto("https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/login")
            logging.info("Page Vocalcom ouverte")

            # -------------------------------------------------
            # Saisir username
            # -------------------------------------------------
            username = os.getenv("USER_NAME_VOCALCOM", "WFM")
            password = os.getenv("PASSWORD", "azer")

            page.fill("#usrID", username)
            page.press("#usrID", "Enter")
            logging.info("Login envoyé")

            # -------------------------------------------------
            # Saisir password
            # -------------------------------------------------
            page.wait_for_selector("#usrPWD", timeout=15000)
            page.fill("#usrPWD", password)
            page.press("#usrPWD", "Enter")
            logging.info("Mot de passe envoyé")

            # -------------------------------------------------
            # Attendre que le workspace soit visible et cliquer
            # -------------------------------------------------
            workspace_selector = "li.workspace[data-screen='workspace'][title='Gestion des Workspaces']"
            page.wait_for_selector(workspace_selector, timeout=20000)
            page.click(workspace_selector)
            logging.info("Workspace ouvert")

            # -------------------------------------------------
            # Attendre que le bouton Reporting apparaisse et cliquer dessus
            # -------------------------------------------------
            reporting_selector = "span.button-name[data-application-oid='f9LC8CUK']"
            page.wait_for_selector(reporting_selector, timeout=20000)
            page.click(reporting_selector)
            logging.info("Reporting ouvert")

            # -------------------------------------------------
            # Menu Report Agent
            # -------------------------------------------------
            page.wait_for_selector("#Mnuu_RepotAgent", timeout=15000)
            page.click("#Mnuu_RepotAgent")
            logging.info("Menu Agent Report ouvert")

            # -------------------------------------------------
            # Agent Distribution Report
            # -------------------------------------------------
            distribution_selector = "//td[@class='menutd2' and contains(@onclick,'AgentDistributionReport')]"
            page.wait_for_selector(distribution_selector, timeout=15000)
            page.click(distribution_selector)
            logging.info("Agent Distribution Report sélectionné")

            # -------------------------------------------------
            # Choisir format XLS
            # -------------------------------------------------
            page.wait_for_selector("#typeButton.XLS", timeout=15000)
            page.click("#typeButton.XLS")
            logging.info("Format XLS sélectionné")

            # -------------------------------------------------
            # Générer le rapport et télécharger
            # -------------------------------------------------
            page.wait_for_selector("#generateButton", timeout=15000)
            with page.expect_download() as download_info:
                page.click("#generateButton")
            download = download_info.value

            # Sauvegarder le fichier dans INPUT_DIR
            filepath = os.path.join(download_path, download.suggested_filename)
            download.save_as(filepath)
            logging.info(f"Téléchargement terminé : {filepath}")

            time.sleep(2)  # petite pause

        except Exception as e:
            logging.error(f"Erreur téléchargement Vocalcom : {e}")

        finally:
            browser.close()
            logging.info("Navigateur fermé")