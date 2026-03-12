import pandas as pd
from processors.distribution_appel import DistributionAppel
from processors.distribution_etat_agent import DistributionEtatAgent

def detect_processor(csv_path):
    # Lire seulement les 20Pas premières lignes pour détecter le type
    df = pd.read_csv(csv_path, nrows=20, header=None, dtype=str).fillna('')
    sample_text = " ".join(df.astype(str).values.flatten())

    if "Calls distribution report" in sample_text or "Reroutes" in sample_text:
        return DistributionAppel(), "distribution_appel"

    if "Agent" in sample_text or "Attente_Num" in sample_text:
        return DistributionEtatAgent(), "distribution_etat_agent"

    raise Exception("Type de fichier inconnu")