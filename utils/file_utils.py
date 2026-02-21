from datetime import datetime
import os

def generate_filename(base_name, extracted_date=None):
    today = datetime.now().strftime("%d-%m-%Y")

    if extracted_date:
        extracted_date = extracted_date.replace("/", "-")
        return f"{base_name}_{extracted_date}_{today}"

    return f"{base_name}_{today}"

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)