import pandas as pd
import re
from .base_processor import BaseProcessor

class IncomingProcessor(BaseProcessor):

    def process(self, file_path):
        all_data = []
        current_agent_id = None
        current_agent_name = None
        current_date = None

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        for line in lines:
            # On nettoie la ligne des espaces et guillemets globaux avant le split
            clean_line = line.strip()
            parts = clean_line.split(',')

            # Détection Agent
            agent_match = re.search(r"Agent\s+([\d\s\xa0]+):\s*(.*)", clean_line)
            if agent_match:
                # ID : on supprime tous les types d'espaces
                raw_id = agent_match.group(1)
                current_agent_id = re.sub(r"[\s\xa0]+", "", raw_id)
                
                # Nom : 
                # On récupère la partie après les ":"
                raw_name = agent_match.group(2)
                
                # Nettoyage profond :
                # 1. On remplace la virgule par un espace
                name_step1 = raw_name.replace(',', ' ')
                # 2. On retire les guillemets (doubles et simples) et les virgules traînantes aux extrémités
                name_step2 = name_step1.strip(' ",\'') 
                # 3. On réduit les espaces multiples en un seul
                current_agent_name = re.sub(r"\s+", " ", name_step2).strip()
                
                continue

            # Détection Date
            date_match = re.search(r"Le\s+(\d{2}/\d{2}/\d{4})", clean_line)
            if date_match:
                current_date = date_match.group(1)
                continue

            # Extraction des lignes horaires (Heure : 00:00, 00:30, etc.)
            if len(parts) > 1 and re.match(r"^\d{2}:\d{2}$", parts[1]):
                row_dict = {
                    'Date_Fichier': current_date,
                    'Agent_ID': current_agent_id,
                    'Agent_Name': current_agent_name,
                    'Heure': parts[1],
                    'Attente_Num': parts[3] if len(parts) > 3 else '',
                    'Attente_Temps': parts[4] if len(parts) > 4 else '',
                    'Supervision_Num': parts[8] if len(parts) > 8 else '',
                    'Supervision_Temps': parts[10] if len(parts) > 10 else '',
                    'Traitement_Num': parts[14] if len(parts) > 14 else '',
                    'Traitement_Temps': parts[15] if len(parts) > 15 else '',
                    'Post_Travail_Num': parts[19] if len(parts) > 19 else '',
                    'Post_Travail_Temps': parts[20] if len(parts) > 20 else '',
                    'Pause_Num': parts[24] if len(parts) > 24 else '',
                    'Pause_Temps': parts[25] if len(parts) > 25 else '',
                }
                all_data.append(row_dict)

        return pd.DataFrame(all_data)