import pandas as pd
import re
from .base_processor import BaseProcessor

class DistributionAppel(BaseProcessor):

    def __init__(self):
        self.extracted_date = None

    def process(self, csv_file_path):
        # Lecture du CSV en forçant tout en texte
        df_raw = pd.read_csv(csv_file_path, encoding="utf-8-sig", dtype=str, header=None).fillna('')

        # Tes Regex originales (conservées)
        date_re = re.compile(r"Le\s+(\d{2}/\d{2}/\d{4})")
        time_re = re.compile(r"\b\d{2}:\d{2}\b")

        all_rows = []

        current_date = None
        current_sous_campagne = None
        last_potential_subject = None # Pour mémoriser le texte au-dessus de la date

        for _, row in df_raw.iterrows():
            # Nettoyage de chaque cellule (ton code original)
            row_list = [str(c).strip() for c in row.tolist()]
            line = ",".join(row_list)
            first_cell = row_list[0] if row_list else ""

            # 🔹 Logique pour capturer la sous-campagne (le texte avant la date)
            # Si la ligne n'est pas vide et n'est pas une date/heure/titre, c'est une potentielle sous-campagne
            if first_cell and not date_re.search(line) and not time_re.match(first_cell):
                if "Calls distribution report" not in first_cell and "Durée" not in first_cell:
                    last_potential_subject = first_cell

            # 🔹 Détection date (ton code original conservé)
            date_match = date_re.search(line)
            if date_match:
                current_date = date_match.group(1)
                self.extracted_date = current_date
                # Quand on trouve la date, on valide que le texte précédent était la sous-campagne
                current_sous_campagne = last_potential_subject
                continue

            # 🔹 Détection heure (ton code original conservé)
            heure = None
            for cell in row_list:
                if time_re.match(cell):
                    heure = cell
                    break

            if not heure:
                continue

            # Nettoyage de la ligne (ton code original)
            cleaned = [x for x in row_list if x != ""]
            cleaned = [x.replace("h", ":").replace("'", ":") for x in cleaned]

            if len(cleaned) < 5:
                continue

            # Créer un dictionnaire (en utilisant current_sous_campagne au lieu de current_agent_id)
            row_dict = {
                "Date": current_date,
                "Sous_campagne": current_sous_campagne,
                "Heure": cleaned[0],
                "Appels": cleaned[1] if len(cleaned) > 1 else "",
                "Clotures": cleaned[2] if len(cleaned) > 2 else "",
                "Debordements": cleaned[3] if len(cleaned) > 3 else "",
                "Reroutes": cleaned[4] if len(cleaned) > 4 else "",
                "Ignores": cleaned[5] if len(cleaned) > 5 else "",
                "SVI": cleaned[6] if len(cleaned) > 6 else "",
                "Abandon": cleaned[7] if len(cleaned) > 7 else "",
                "Traites": cleaned[8] if len(cleaned) > 8 else "",
                "Transf": cleaned[9] if len(cleaned) > 9 else "",
                "NS": cleaned[10] if len(cleaned) > 10 else "",
                "Traite<SL": cleaned[11] if len(cleaned) > 11 else "",
                "Aband.<": cleaned[12] if len(cleaned) > 12 else "",
                "Comm_moy": cleaned[13] if len(cleaned) > 13 else "",
                "Att_moy": cleaned[14] if len(cleaned) > 14 else "",
                "Aband_moy": cleaned[13] if len(cleaned) > 13 else "",
                "Comm_tot": cleaned[14] if len(cleaned) > 14 else "",
            }

            all_rows.append(row_dict)

        return pd.DataFrame(all_rows)