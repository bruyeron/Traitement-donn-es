import os
from dotenv import load_dotenv

# Charger les variables .env une seule fois
load_dotenv()

USER_NAME_VOCALCOM = os.getenv("USER_NAME_VOCALCOM")
PASSWORD = os.getenv("PASSWORD")

if not USER_NAME_VOCALCOM or not PASSWORD:
    raise Exception("Les identifiants doivent être définis dans le fichier .env")
