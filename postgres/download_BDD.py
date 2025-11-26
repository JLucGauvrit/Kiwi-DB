from huggingface_hub import snapshot_download
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Crée le chemin du répertoire de données dans le même dossier que le script
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)


snapshot_download(
    repo_id="AyoubChLin/CompanyDocuments",
    local_dir=data_dir,
    local_dir_use_symlinks=False,
    token=HUGGINGFACE_API_TOKEN,
    repo_type="dataset",
)

# Construit le chemin complet du fichier parquet
file_path = os.path.join(data_dir, "data", "train-00000-of-00001.parquet")

df = pd.read_parquet(file_path)

engine = create_engine("postgresql://myuser:mypass@db:5432/mydb")

df.to_sql("documents", engine, if_exists="replace", index=False)
