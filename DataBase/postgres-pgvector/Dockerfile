FROM pgvector/pgvector:pg16

# Image pré-construite qui contient PostgreSQL + pgvector.
# On copie les scripts d'initialisation pour créer la base et la table/extension
COPY 00-create-db.sql /docker-entrypoint-initdb.d/00-create-db.sql
COPY 01-init-schema.sql /docker-entrypoint-initdb.d/01-init-schema.sql
COPY dataset_droit_travail.sql /docker-entrypoint-initdb.d/03-droit-travail-data.sql

EXPOSE 5432

CMD ["postgres"]
