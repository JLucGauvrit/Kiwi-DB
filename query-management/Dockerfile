# Étape 1: Utiliser une image Python de base, légère et officielle
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances dans le conteneur
COPY requirements.txt .
COPY main.py .

# Installer les dépendances Python
# --no-cache-dir pour ne pas stocker le cache, réduisant la taille de l'image
# --trusted-host pypi.python.org pour éviter des problèmes de SSL dans certains environnements
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Exposer le port sur lequel l'application Flask va tourner
EXPOSE 5000

# Commande pour lancer l'application lorsque le conteneur démarre
# Utilise "gunicorn" pour un serveur de production plus robuste que le serveur de développement de Flask
# CMD ["python", "main.py"] # Alternative pour le développement
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
