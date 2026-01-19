-- Se connecter à la base de données dbname
\connect dbname

-- Créer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Créer la table droit_travail
CREATE TABLE IF NOT EXISTS droit_travail (
    id SERIAL PRIMARY KEY,
    article TEXT NOT NULL,
    embedding vector(1536)
);
