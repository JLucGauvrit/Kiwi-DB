BDD Fédérée par Agent - Documentation
=====================================

Bienvenue dans la documentation complète du projet **BDD Fédérée par Agent**, un orchestrateur multi-agents pour l'IA générative avec RAG (Retrieval-Augmented Generation).

.. toctree::
   :maxdepth: 2
   :caption: 📚 Contenu

   guide_demarrage
   architecture
   agents
   mcp_protocol
   api_reference
   modules
   deployment
   faq

Table des Matières
==================

- **Guide de Démarrage** : Installation, configuration et premiers pas
- **Architecture** : Vue d'ensemble du système et flux de données
- **Modules** : Documentation de tous les modules Python
- **Référence API** : Points d'entrée et endpoints
- **Agents** : Détails sur chaque agent spécialisé
- **Protocole MCP** : Communication avec les bases de données
- **Déploiement** : Mise en production avec Docker

Introduction
============

Ce projet implémente un système fédéré de Retrieval-Augmented Generation (RAG) utilisant une architecture multi-agents. Il permet de :

- **Analyser les requêtes** pour déterminer l'intention de l'utilisateur
- **Récupérer les schémas** des bases de données disponibles
- **Générer des requêtes SQL** optimisées et sécurisées
- **Valider les requêtes** avant exécution
- **Exécuter en fédéré** sur plusieurs bases de données
- **Composer les réponses** en langage naturel

Technologies Principales
========================

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
.. image:: https://img.shields.io/badge/FastAPI-0.104+-green.svg
.. image:: https://img.shields.io/badge/LangGraph-latest-purple.svg

- **Python 3.9+** : Langage principal
- **FastAPI** : Framework web asynchrone
- **LangGraph** : Orchestration de pipelines avec états
- **LangChain** : Intégration avec modèles de langage
- **Ollama** : Modèle de langage local
- **PostgreSQL + pgvector** : Stockage vectoriel
- **MCP (Model Context Protocol)** : Communication inter-services
- **Docker & Docker Compose** : Conteneurisation

Structure du Projet
===================

::

    BDD Fédérée par Agent/
    ├── orchestrateur/          # Service principal
    │   ├── main.py
    │   ├── src/
    │   │   ├── orchestrator/   # Pipeline LangGraph
    │   │   ├── agents/         # 6 agents spécialisés
    │   │   ├── executor/       # Exécution requêtes
    │   │   └── mcp_client.py
    │   └── requirements.txt
    ├── mcp/
    │   └── mcp-gateway/        # Passerelle MCP
    ├── query-management/       # Service Gemini
    ├── DataBase/               # Scripts BDD
    ├── pytest/                 # Tests
    ├── docs/                   # Documentation
    └── docker-compose.yml      # Orchestration

Démarrage Rapide
================

Installation et lancement avec Docker :

.. code-block:: bash

    # Construire tous les services
    docker-compose up --build

    # Accéder à l'API
    # http://localhost:8000/docs (Swagger)

    # Lancer les tests
    cd pytest
    pytest

Ressources
==========

.. toctree::
   :hidden:

   self

- **GitHub** : Dépôt du projet
- **Issues** : Signaler des problèmes
- **Discussions** : Questions et partage

Auteur & Licence
================

**Auteur** : PROCOM Team  
**Version** : 1.0.0  
**Date** : 19 janvier 2026  

Pour plus d'informations, consultez le fichier **DOCUMENTATION.py** ou les fichiers de configuration dans le répertoire racine.

.. note::
   Cette documentation a été générée automatiquement à partir des docstrings PyDoc du code source. Elle est mise à jour en même temps que le code.

Indices et Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
