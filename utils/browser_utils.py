from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def create_chrome_driver(download_dir: str):
    """
    Crée et renvoie un driver Chrome configuré avec le dossier de téléchargement spécifié.
    """
    # Crée le dossier s'il n'existe pas
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    # chrome_options.add_argument("--headless")              # ✅ exécution sans fenêtre
    chrome_options.add_argument("--no-sandbox")            # utile pour Linux ou environnements isolés
    chrome_options.add_argument("--disable-dev-shm-usage") # améliore la stabilité
    chrome_options.add_argument("--disable-gpu")           # recommandé pour Windows
    chrome_options.add_argument("--window-size=1920,1080") # évite les erreurs de résolution
    chrome_options.add_argument("--log-level=3")           # moins de logs inutiles
    # chrome_options.add_argument("--incognito")

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
    })

    driver = webdriver.Chrome(options=chrome_options)
    return driver