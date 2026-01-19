"""
Database connection test and PDF extraction from PostgreSQL.

Ce script teste la connexion à la base de données PostgreSQL et
démontre l'extraction de documents PDF stockés dans la base de données.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
import psycopg2

def extract_pdf_from_database():
    """
    Extraire un document PDF de la base de données et l'enregistrer localement.
    
    Se connecte à la base de données PostgreSQL 'entreprise' et récupère
    le premier document PDF non-null de la table 'company_documents'.
    Le document est ensuite enregistré dans un fichier local.
    
    @return: Chemin du fichier créé
    @rtype: str
    @raise psycopg2.Error: En cas d'erreur de connexion ou de requête
    """
    # Établir la connexion à PostgreSQL
    conn = psycopg2.connect(
        host="localhost", port=5432,
        user="user", password="password", dbname="entreprise"
    )

    try:
        # Exécuter la requête pour récupérer un document PDF
        with conn.cursor() as cur:
            cur.execute("""
                SELECT doc_id, pdf_data
                FROM company_documents
                WHERE pdf_data IS NOT NULL
                LIMIT 1;
            """)
            doc_id, pdf_data = cur.fetchone()

        # Créer un nom de fichier basé sur l'ID du document
        filename = f"check_{doc_id or 'document'}.pdf"
        
        # Écrire les données PDF dans un fichier
        with open(filename, "wb") as f:
            f.write(pdf_data)

        print("PDF écrit dans", filename)
        return filename
        
    finally:
        # Fermer la connexion à la base de données
        conn.close()

if __name__ == "__main__":
    extract_pdf_from_database()
