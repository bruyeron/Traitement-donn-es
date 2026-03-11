import pandas as pd
import re
from .base_processor import BaseProcessor


class DistributionEtatAgent(BaseProcessor):

    def __init__(self):
        self.extracted_date = None

    def process(self, csv_file_path):
        # Lecture du CSV en forçant tout en texte
        df_raw = pd.read_csv(csv_file_path, encoding="utf-8-sig", dtype=str).fillna('')

        # Regex pour extraire agent, date et heure
        agent_re = re.compile(r"Agent\s+([\d\s\xa0]+):\s*(.*)")
        date_re = re.compile(r"Le\s+(\d{2}/\d{2}/\d{4})")
        time_re = re.compile(r"\b\d{2}:\d{2}\b")

        all_rows = []

        current_agent_id = None
        current_agent_name = None
        current_date = None

        ignored_lines = 0

        for _, row in df_raw.iterrows():
            # Nettoyage de chaque cellule
            row_list = [str(c).strip() for c in row.tolist()]
            line = ",".join(row_list)

            # 🔹 Détection agent
            agent_match = agent_re.search(line)
            if agent_match:
                raw_id = agent_match.group(1)
                current_agent_id = re.sub(r"[\s\xa0]+", "", raw_id)

                raw_name = agent_match.group(2)
                current_agent_name = re.sub(r"\s+", " ", raw_name.replace(",", " ").strip())
                continue

            # 🔹 Détection date
            date_match = date_re.search(line)
            if date_match:
                current_date = date_match.group(1)
                self.extracted_date = current_date
                continue

            # 🔹 Détection heure
            heure = None
            for cell in row_list:
                if time_re.match(cell):
                    heure = cell
                    break

            if not heure:
                ignored_lines += 1
                continue

            # Nettoyage de la ligne
            cleaned = [x for x in row_list if x != ""]

            # Si moins de 5 colonnes après nettoyage, ignorer
            if len(cleaned) < 5:
                ignored_lines += 1
                continue

            # Créer un dictionnaire avec valeurs par défaut si certaines colonnes manquent
            row_dict = {
                "Date_Fichier": current_date,
                "Agent_ID": current_agent_id,
                "Agent_Name": current_agent_name,
                "Heure": cleaned[0],
                "Attente_Num": cleaned[1] if len(cleaned) > 1 else "",
                "Attente_Temps": cleaned[2] if len(cleaned) > 2 else "",
                "Attente_Pct": cleaned[3] if len(cleaned) > 3 else "",
                "Supervision_Temps": cleaned[4] if len(cleaned) > 4 else "",
                "Supervision_Pct": cleaned[5] if len(cleaned) > 5 else "",
                "Traitement_Num": cleaned[6] if len(cleaned) > 6 else "",
                "Traitement_Temps": cleaned[7] if len(cleaned) > 7 else "",
                "Traitement_Pct": cleaned[8] if len(cleaned) > 8 else "",
                "Post_Travail_Num": cleaned[9] if len(cleaned) > 9 else "",
                "Post_Travail_Temps": cleaned[10] if len(cleaned) > 10 else "",
                "Post_Travail_Pct": cleaned[11] if len(cleaned) > 11 else "",
                "Pause_Num": cleaned[12] if len(cleaned) > 12 else "",
                "Pause_Temps": cleaned[13] if len(cleaned) > 13 else "",
                "Pause_Pct": cleaned[14] if len(cleaned) > 14 else "",
            }

            all_rows.append(row_dict)

        # Transformation finale en DataFrame
        df = pd.DataFrame(all_rows)

        return df