Guide de Démarrage
==================

Installation
============

Prérequis
---------

- Docker & Docker Compose
- Python 3.9+
- PostgreSQL 15+
- Git

Clonage du Projet
-----------------

.. code-block:: bash

    git clone <repository-url>
    cd "BDD fédéré par agent"

Installation des Dépendances
-----------------------------

Pour chaque service Python :

.. code-block:: bash

    # Orchestrateur
    cd orchestrateur
    pip install -r requirements.txt
    
    # MCP Gateway
    cd ../mcp/mcp-gateway
    pip install -r requirements.txt
    
    # Query Management
    cd ../../query-management
    pip install -r requirements.txt

Configuration
=============

Variables d'Environnement
-------------------------

Créez un fichier ``.env`` à la racine :

.. code-block:: bash

    # Orchestrateur
    OLLAMA_BASE_URL=http://localhost:11434
    MCP_GATEWAY_URL=ws://localhost:8000/ws
    
    # Query Management
    GOOGLE_API_KEY=your_api_key_here
    
    # PostgreSQL
    POSTGRES_USER=procom
    POSTGRES_PASSWORD=procom_password
    POSTGRES_DB=federated_db
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    
    # MCP Gateway
    MCP_SERVERS_CONFIG=config/servers.json

Fichier de Configuration MCP
-----------------------------

Créez ``config/servers.json`` :

.. code-block:: json

    {
      "postgres": {
        "uri": "sse://localhost:8000/sse",
        "env": {}
      }
    }

Démarrage Rapide avec Docker
============================

Démarrage
---------

.. code-block:: bash

    # Construire et démarrer tous les services
    docker-compose up --build
    
    # En arrière-plan
    docker-compose up -d --build

Vérification
-----------

.. code-block:: bash

    # Vérifier les services
    docker-compose ps
    
    # Voir les logs
    docker-compose logs -f orchestrateur
    
    # Tester la connexion
    curl http://localhost:8000/health

Arrêt
-----

.. code-block:: bash

    docker-compose down
    
    # Avec suppression des volumes
    docker-compose down -v

Utilisation
===========

Interface Swagger
-----------------

L'interface interactive est disponible sur :

    http://localhost:8000/docs

Vous pouvez :

- Voir tous les endpoints disponibles
- Tester les requêtes directement
- Consulter les schémas Pydantic

Exemple de Requête
-------------------

.. code-block:: bash

    curl -X POST "http://localhost:8000/api/query" \
      -H "Content-Type: application/json" \
      -d '{"query": "Quelle est la capital de la France?"}'

Réponse Attendue
~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "request_id": "uuid-here",
      "query": "Quelle est la capital de la France?",
      "intent": "general_knowledge",
      "status": "completed",
      "final_output": "La capitale de la France est Paris.",
      "execution_time": 1.23
    }

Tests
=====

Lancer les Tests
----------------

.. code-block:: bash

    cd pytest
    
    # Tous les tests
    pytest
    
    # Avec verbosité
    pytest -v
    
    # Tests spécifiques
    pytest test_query.py -v
    
    # Avec couverture
    pytest --cov=orchestrateur

Tests Disponibles
-----------------

- **test_query.py** : Tests WebSocket et MCP gateway
- **test_BDD.py** : Tests de connexion PostgreSQL
- **test_db_available.py** : Vérification de disponibilité

Dépannage
=========

Erreur : « ModuleNotFoundError: No module named 'src' »
-------------------------------------------------------

**Cause** : PYTHONPATH n'est pas configuré correctement

**Solution** :

.. code-block:: bash

    # Windows PowerShell
    $env:PYTHONPATH=".\orchestrateur"
    python -m orchestrateur.main
    
    # Linux/macOS
    export PYTHONPATH="./orchestrateur"
    python -m orchestrateur.main

Erreur : « Connection refused »
-------------------------------

**Cause** : Les services ne sont pas accessibles

**Solution** :

.. code-block:: bash

    # Vérifier que Docker est en cours d'exécution
    docker ps
    
    # Redémarrer les services
    docker-compose restart
    
    # Vérifier les logs
    docker-compose logs

Erreur : « MCP Gateway not connected »
--------------------------------------

**Cause** : Le serveur MCP n'est pas connecté

**Solution** :

.. code-block:: bash

    # Vérifier que le serveur MCP est actif
    curl http://localhost:8000/servers
    
    # Vérifier la configuration
    cat config/servers.json
    
    # Redémarrer le gateway
    docker-compose restart mcp-gateway

Prochaines Étapes
=================

- Lire la section :doc:`architecture` pour comprendre le système
- Consulter :doc:`api_reference` pour les endpoints disponibles
- Explorer :doc:`agents` pour les détails des agents
- Voir :doc:`deployment` pour la mise en production

Ressources Supplémentaires
==========================

- :doc:`../DOCUMENTATION`
- `FastAPI Documentation <https://fastapi.tiangolo.com>`_
- `LangGraph Documentation <https://langchain-ai.github.io/langgraph/>`_
- `MCP Protocol <https://modelcontextprotocol.io>`_
