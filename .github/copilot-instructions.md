# Guide pour les agents IA Copilot

Ce document fournit des instructions pour les agents IA qui travaillent sur ce projet.

## Vue d'ensemble du projet

Ce projet est un orchestrateur multi-agents pour l'IA générative avec RAG (Retrieval-Augmented Generation). Il utilise le protocole MCP (Model Context Protocol) pour la communication entre les agents.

L'objectif est de distribuer les requêtes des utilisateurs à différents agents spécialisés (connaissances générales, actualités, analyse) et de synthétiser leurs réponses.

## Architecture

L'architecture est basée sur des microservices conteneurisés avec Docker.

```
Interface utilisateur (Web UI)
         ↓
Orchestrateur (FastAPI)
         ↓
    Serveur MCP
    ↙   ↓    ↘
Client MCP A   Client MCP B   Client MCP C
    ↓              ↓              ↓
Agent RAG 1    Agent RAG 2    Agent RAG 3
(Gemini)      (Perplexity)   (Gemini)
Général       Actuel        Analyse
    ↓              ↓              ↓
PostgreSQL + pgvector (Base de données vectorielle partagée)
```

Consultez le fichier `docker-compose.yml` pour voir comment les services sont connectés.

## Services

-   `web` : L'interface utilisateur front-end (le contenu n'est pas encore défini).
-   `orchestrateur` : Le service principal qui reçoit les requêtes, les distribue aux agents via MCP et synthétise les réponses. Il est construit avec FastAPI.
-   `query-management` : Un exemple d'agent qui traite les requêtes. Il est construit avec Flask et utilise l'API Google Gemini.

## Flux de travail du développeur

### Construction et exécution du projet

Pour construire et exécuter le projet, utilisez Docker Compose :

```bash
docker-compose up --build
```

### Dépendances

Les dépendances Python pour chaque service sont gérées dans les fichiers `requirements.txt`.

-   Le service `query-management` utilise Flask, python-dotenv, google-generativeai et gunicorn.

### Points de terminaison de l'API

-   Le service `query-management` a un point de terminaison `/query` qui accepte les requêtes POST avec un `prompt` JSON.

    Exemple :
    ```json
    {
      "prompt": "Quelle est la capitale de la France ?"
    }
    ```

## Technologies clés

-   **Docker et Docker Compose** : Pour la conteneurisation et l'orchestration.
-   **Python** : Le langage principal pour les services back-end.
-   **FastAPI** : Pour le service `orchestrateur`.
-   **Flask** : Pour le service `query-management`.
-   **Google Gemini** : Utilisé par l'agent `query-management` pour générer du contenu.
-   **PostgreSQL avec pgvector** : Pour le stockage vectoriel et la recherche.
