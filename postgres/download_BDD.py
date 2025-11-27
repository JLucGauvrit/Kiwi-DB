import os
import psycopg2
import requests
from psycopg2.extras import execute_values, Json
from datasets import load_dataset

HF_DATASET = "AyoubChLin/CompanyDocuments"

def get_pg_conn():
    # Tu peux aussi utiliser une URL unique POSTGRES_URL si tu préfères
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        dbname=os.getenv("POSTGRES_DB", "entreprise"),
    )
    conn.autocommit = True
    return conn

def fetch_pdf(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print("DL PDF failed:", url, e)
        return None
    
def create_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS company_documents (
                id SERIAL PRIMARY KEY,
                split TEXT,
                doc_id TEXT,
                content TEXT,
                metadata JSONB,
                pdf_data BYTEA,            -- ajout colonne pour le PDF
                pdf_url TEXT               -- éventuellement garder l’URL
            );
            """
        )


def main():
    # Auth HF optionnelle si le dataset est privé
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    load_kwargs = {}
    if hf_token:
        load_kwargs["token"] = hf_token

    # Charge toutes les splits du dataset
    ds_dict = load_dataset(HF_DATASET, **load_kwargs)

    conn = get_pg_conn()
    create_table(conn)

    with conn.cursor() as cur:
        for split_name, ds in ds_dict.items():
            rows = []
            for row in ds:
                doc_id = str(row.get("id") or row.get("doc_id") or "")
                content = str(row.get("content") or row.get("text") or "")
                metadata = {k: v for k, v in row.items()
                            if k not in ("id", "doc_id", "content", "text", "pdf_url")}
                # Adapte le champ : ex pdf_url = row.get("pdf_url")
                pdf_url = row.get("pdf_url") or f"L'URL exacte à reconstruire selon doc_id/chemin HuggingFace"
                pdf_data = fetch_pdf(pdf_url) if pdf_url else None
                rows.append((split_name, doc_id, content, Json(metadata), pdf_data, pdf_url))

            # Insert en masse
            execute_values(
                cur,
                """
                INSERT INTO company_documents (split, doc_id, content, metadata, pdf_data, pdf_url)
                VALUES %s
                """,
                rows,
            )
    conn.close()

if __name__ == "__main__":
    main()
