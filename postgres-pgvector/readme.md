make build      # Construire l'image Docker
make start      # Démarrer le conteneur PostgreSQL
make convert    # Convertir les vecteurs en CSV
make import     # Importer les vecteurs dans PostgreSQL
make logs       # Suivre les logs

Connecte-toi au conteneur PostgreSQL :
docker exec -it postgres-pgvector psql -U user -d dbTravail
