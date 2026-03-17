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

from downloader.actions import etat_agent

from utils.browser_utils import create_chrome_driver

ACTIONS = {
    "1": ("Télécharger la distribution des états des agents", etat_agent.run)
}

def download_reports():

    print("=== Choisissez une action ===")
    for key, (desc, _) in ACTIONS.items():
        print(f"{key}. {desc}")

    choice = input("Entrez le numéro de l'action : ").strip()

    # download_dir = r"D:\Utilisateurs\soava.rakotomanana\Data\Rapport detaille\Brute" 
    # download_dir = r"D:\Utilisateurs\soava.rakotomanana\Workspace\Automatisation\Traitement-donn-es\input" 
    

    if choice not in ACTIONS:
        print("❌ Choix invalide")
    else:
        description, action_func = ACTIONS[choice]
        print(f"▶️  Exécution de : {description}")

        # driver = webdriver.Chrome()
        driver = create_chrome_driver(INPUT_DIR)
        try:
            action_func(driver)
        finally:
            driver.quit()
