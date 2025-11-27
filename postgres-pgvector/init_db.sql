-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the postgres role if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
      CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'password';
   END IF;
END $$;

-- Create the database if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dbname') THEN
      CREATE DATABASE dbname;
   END IF;
END $$;

-- Create the droit_travail table
CREATE TABLE IF NOT EXISTS droit_travail (
    id SERIAL PRIMARY KEY,
    article TEXT NOT NULL,
    embedding vector(1536)
);