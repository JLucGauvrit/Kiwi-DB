FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
RUN pip install --no-cache-dir pandas requests

# Copie du script de génération
COPY seed_generator.py .

# Exécution du script au démarrage
CMD ["python", "seed_generator.py"]
