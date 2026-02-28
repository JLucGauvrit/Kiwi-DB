# Étape 1 : Build (compilation des dépendances)
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .

# Installation des dépendances de compilation et création des "wheels"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
       libffi-dev \
       libssl-dev \
       ca-certificates \
       rustc \
       cargo \
    && pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Étape 2 : Runtime (image finale allégée)
FROM python:3.11-slim

WORKDIR /app

# Récupération des paquets compilés à l'étape précédente
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copie du code avec les bons droits
COPY . .

EXPOSE 9000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
