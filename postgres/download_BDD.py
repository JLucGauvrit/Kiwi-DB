import os
import json
import psycopg2
import time
from psycopg2.extras import execute_values, Json
from datasets import load_dataset

HF_DATASET = "AyoubChLin/CompanyDocuments"
LOCAL_DATA_DIR = "/data/CompanyDocuments"


def get_pg_conn():
    """Connexion Postgres avec retry"""
    max_retries = 10
    wait_seconds = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to PostgreSQL... (Attempt {attempt + 1}/{max_retries})")
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "postgres"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                user=os.getenv("POSTGRES_USER", "user"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                dbname=os.getenv("POSTGRES_DB", "entreprise"),
            )
            conn.autocommit = True
            print("✓ Successfully connected to PostgreSQL.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Connection failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                print("Max retries reached. Could not connect to the database.")
                exit(1)

def table_already_filled(conn, min_rows: int = 1000) -> bool:
    """Retourne True si la table contient déjà des données (seed déjà fait)."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM company_documents;")
        count = cur.fetchone()[0]
        print(f"company_documents row count: {count}")
        return count >= min_rows

def discover_folders():
    """Découvrir automatiquement les dossiers disponibles dans le clone"""
    folders = {}
    if os.path.exists(LOCAL_DATA_DIR):
        for item in os.listdir(LOCAL_DATA_DIR):
            item_path = os.path.join(LOCAL_DATA_DIR, item)
            if os.path.isdir(item_path):
                folders[item.lower()] = item
                print(f"  Found folder: {item}")
    return folders


def map_document_type_to_folder(document_type, discovered_folders):
    """
    Mapper le document_type (de la colonne) au vrai dossier découvert.
    document_type peut être: "Shipping Orders", "Purchase Orders", "Invoice", etc.
    """
    doc_type_lower = (document_type or "").lower()
    
    # Chercher un match dans les dossiers découverts
    for folder_key, folder_name in discovered_folders.items():
        if folder_key in doc_type_lower or doc_type_lower.split()[0] in folder_key:
            return folder_name
    
    # Fallback basé sur les patterns connus
    if "shipping" in doc_type_lower:
        return discovered_folders.get("shippingorders", "ShippingOrders")
    elif "purchase" in doc_type_lower:
        return discovered_folders.get("purchaseorders", "PurchaseOrders")
    elif "invoice" in doc_type_lower:
        return discovered_folders.get("invoices", "Invoices")
    
    # Si rien ne match, pas de dossier
    return None


def fetch_pdf_local(rel_path):
    """Lire le PDF depuis le clone local"""
    full_path = os.path.join(LOCAL_DATA_DIR, rel_path)
    try:
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                data = f.read()
                return data
        else:
            return None
    except Exception as e:
        print(f"✗ Error reading PDF {full_path}: {e}")
        return None


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS company_documents (
                id SERIAL PRIMARY KEY,
                split TEXT,
                doc_id TEXT,
                file_name TEXT,
                document_type TEXT,
                file_content TEXT,
                extracted_data JSONB,
                chat_format JSONB,
                pdf_data BYTEA,
                metadata JSONB
            );
            """
        )
        print("✓ Table 'company_documents' created or already exists.")


def main():
    print(f"🔍 Discovering folders in {LOCAL_DATA_DIR}...")
    discovered_folders = discover_folders()
    if not discovered_folders:
        print(f"⚠ Warning: No folders found in {LOCAL_DATA_DIR}")
        print("  Make sure Git LFS clone completed successfully.")

    conn = get_pg_conn()
    create_table(conn)

    # NE RIEN FAIRE si la table est déjà remplie
    if table_already_filled(conn, min_rows=2000):
        print("✅ Table company_documents already filled, skipping import.")
        conn.close()
        return

    print(f"\n📚 Loading dataset from Hugging Face: {HF_DATASET}")
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    load_kwargs = {}
    if hf_token:
        load_kwargs["token"] = hf_token

    # Load from HF (parquet only)
    ds_dict = load_dataset(HF_DATASET, **load_kwargs)

    with conn.cursor() as cur:
        for split_name, ds in ds_dict.items():
            print(f"\n📦 Processing split: {split_name}")
            rows = []
            pdf_found_count = 0
            pdf_missing_count = 0

            for idx, row in enumerate(ds):
                if (idx + 1) % 100 == 0:
                    print(f"  Processing row {idx + 1}/{len(ds)}")

                doc_id = str(row.get("id") or "")
                file_name = row.get("file_name") or ""
                document_type = row.get("document_type") or ""
                file_content = row.get("file_content") or ""

                extracted_data_raw = row.get("extracted_data") or {}
                try:
                    if isinstance(extracted_data_raw, str):
                        extracted_data = json.loads(extracted_data_raw)
                    else:
                        extracted_data = extracted_data_raw
                except Exception:
                    extracted_data = {}

                chat_format = row.get("chat_format") or []
                if not isinstance(chat_format, (list, dict)):
                    try:
                        chat_format = json.loads(str(chat_format))
                    except Exception:
                        chat_format = []

                folder = map_document_type_to_folder(document_type, discovered_folders)

                pdf_data = None
                if folder and file_name:
                    rel_path = f"{folder}/{file_name}"
                    pdf_data = fetch_pdf_local(rel_path)
                    if pdf_data:
                        pdf_found_count += 1
                    else:
                        pdf_missing_count += 1

                metadata = {
                    k: str(v)
                    for k, v in row.items()
                    if k not in (
                        "id",
                        "file_name",
                        "document_type",
                        "file_content",
                        "extracted_data",
                        "chat_format",
                    )
                }

                rows.append(
                    (
                        split_name,
                        doc_id,
                        file_name,
                        document_type,
                        file_content,
                        Json(extracted_data),
                        Json(chat_format),
                        pdf_data,
                        Json(metadata),
                    )
                )

            if rows:
                print(f"Inserting {len(rows)} rows into 'company_documents'...")
                print(f"  ✓ PDFs found: {pdf_found_count}")
                print(f"  ⚠ PDFs missing: {pdf_missing_count}")

                execute_values(
                    cur,
                    """
                    INSERT INTO company_documents
                    (split, doc_id, file_name, document_type, file_content, extracted_data, chat_format, pdf_data, metadata)
                    VALUES %s
                    """,
                    rows,
                )
                print(f"✓ Successfully inserted {len(rows)} rows from split '{split_name}'")

    conn.close()
    print("\n✓ Import completed successfully!")


if __name__ == "__main__":
    main()
