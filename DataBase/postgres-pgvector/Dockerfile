FROM pgvector/pgvector:pg16

# Image pré-construite qui contient PostgreSQL + pgvector.
# On copie seulement le script d'initialisation pour créer la table/extension
COPY dataset_droit_travail.sql /docker-entrypoint-initdb.d/03-droit-travail-data.sql

EXPOSE 5432

CMD ["postgres"]
