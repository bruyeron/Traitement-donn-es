import pandas as pd
import os

def convert_xls_to_csv(input_path, temp_dir="temp"):
    """
    Convertit un XLS en CSV, en lisant tout en texte et en ignorant les en-têtes.
    """

    os.makedirs(temp_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    csv_path = os.path.join(temp_dir, f"{base_name}.csv")

    # Lire tout en texte, pas de header
    df = pd.read_excel(input_path, header=None, dtype=str).fillna('')

    # Exporter en CSV
    df.to_csv(csv_path, index=False, header=False, encoding="utf-8-sig")

    return csv_path