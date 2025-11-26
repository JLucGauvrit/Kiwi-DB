#!/usr/bin/env python3
"""
Télécharge un dataset 'entreprise' depuis Hugging Face ou GitHub
et génère un fichier SQL d'insertion pour Postgres.
"""

import pandas as pd
import os

OUTPUT_DIR = "/output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "02_data.sql")

# Dataset exemple : clients e-commerce Olist (Brésil)
DATASET_URL = "https://huggingface.co/datasets/olistbr/olist_customers_dataset/resolve/main/olist_customers_dataset.csv"

def download_and_convert():
    print("📥 Téléchargement du dataset...")
    try:
        df = pd.read_csv(DATASET_URL)
        print(f"✅ {len(df)} lignes téléchargées")
    except Exception as e:
        print(f"❌ Erreur de téléchargement : {e}")
        return

    print("🔄 Génération du fichier SQL...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("-- Données générées automatiquement\n")
        f.write("-- Dataset: Olist Customers\n\n")
        
        for idx, row in df.iterrows():
            # Échappement des apostrophes pour SQL
            city = str(row['customer_city']).replace("'", "''")
            
            sql = (
                f"INSERT INTO customers "
                f"(customer_id, customer_unique_id, customer_zip_code_prefix, "
                f"customer_city, customer_state) VALUES "
                f"('{row['customer_id']}', '{row['customer_unique_id']}', "
                f"'{row['customer_zip_code_prefix']}', '{city}', '{row['customer_state']}');\n"
            )
            f.write(sql)
            
            if (idx + 1) % 1000 == 0:
                print(f"  ... {idx + 1} lignes générées")
    
    print(f"✅ Fichier SQL créé : {OUTPUT_FILE}")
    print(f"📊 Total : {len(df)} insertions")

if __name__ == "__main__":
    download_and_convert()
