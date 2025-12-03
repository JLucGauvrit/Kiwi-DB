import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432,
    user="user", password="password", dbname="entreprise"
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT doc_id, pdf_data
        FROM company_documents
        WHERE pdf_data IS NOT NULL
        LIMIT 1;
    """)
    doc_id, pdf_data = cur.fetchone()

filename = f"check_{doc_id or 'document'}.pdf"
with open(filename, "wb") as f:
    f.write(pdf_data)

print("PDF écrit dans", filename)
