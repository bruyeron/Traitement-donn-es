import pandas as pd
import os

def convert_xls_to_csv(input_path, temp_dir="temp"):
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Nom du fichier sans extension
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    csv_path = os.path.join(temp_dir, f"{base_name}.csv")

    # Lecture du .xls
    df = pd.read_excel(input_path, engine="xlrd")

    # Export en CSV
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return csv_path