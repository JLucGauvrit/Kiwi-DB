Référence API
=============

Endpoints Principaux
====================

Orchestrateur (Port 8000)
-------------------------

.. http:post:: /api/query

   Traiter une requête utilisateur.

   **Content Type**: ``application/json``

   **Request Body**:

   .. code-block:: json

      {
        "query": "Votre requête ici",
        "context": "Contexte optionnel",
        "max_results": 10
      }

   **Response** (200 OK):

   .. code-block:: json

      {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "query": "Votre requête ici",
        "intent": "general_knowledge|sql_query|analysis",
        "status": "completed|error|timeout",
        "final_output": "Réponse en langage naturel",
        "execution_time": 1.23,
        "metadata": {
          "agents_used": ["intent", "composer"],
          "databases_queried": [],
          "sql_queries": {}
        }
      }

   **Possible Status Codes**:
   
   - ``200 OK`` : Succès
   - ``400 Bad Request`` : Requête invalide
   - ``500 Internal Server Error`` : Erreur interne
   - ``504 Gateway Timeout`` : Dépassement délai

   **Example**:

   .. code-block:: bash

      curl -X POST "http://localhost:8000/api/query" \
        -H "Content-Type: application/json" \
        -d '{
          "query": "Quelle est la capital de la France?",
          "context": "Questions de géographie",
          "max_results": 5
        }'

.. http:get:: /health

   Vérifier la santé du service.

   **Response** (200 OK):

   .. code-block:: json

      {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2026-01-19T10:30:00Z",
        "services": {
          "mcp_gateway": "connected",
          "ollama": "connected",
          "database": "connected"
        }
      }

.. http:get:: /docs

   Interface Swagger UI (interactive API documentation).

.. http:get:: /redoc

   Interface ReDoc (API documentation alternative).

MCP Gateway (Port 8000)
-----------------------

.. http:get:: /health

   Vérifier la santé de la passerelle MCP.

   **Response**:

   .. code-block:: json

      {
        "status": "healthy",
        "servers": [
          {
            "name": "postgres",
            "status": "connected",
            "tools_count": 5
          }
        ]
      }

.. http:get:: /servers

   Lister tous les serveurs MCP connectés.

   **Response**:

   .. code-block:: json

      {
        "servers": [
          {
            "name": "postgres",
            "uri": "sse://localhost:8000/sse",
            "connected": true,
            "tools": [
              {
                "name": "execute_sql",
                "description": "Exécute une requête SQL",
                "input_schema": {...}
              }
            ]
          }
        ]
      }

.. http:websocket:: /ws

   Endpoint WebSocket pour le protocole MCP.

   **Message Format**:

   .. code-block:: json

      {
        "method": "call_tool|list_tools|list_resources|get_resource",
        "params": {...}
      }

   **Response**:

   .. code-block:: json

      {
        "result": "...",
        "error": null
      }

Modèles de Données
==================

QueryRequest
-----------

.. code-block:: python

    from pydantic import BaseModel
    from typing import Optional

    class QueryRequest(BaseModel):
        """Requête utilisateur vers le système RAG."""
        
        query: str
            """Requête en langage naturel."""
        
        context: Optional[str] = None
            """Contexte additionnel pour la requête."""
        
        max_results: int = 10
            """Nombre maximum de résultats à retourner."""

QueryResponse
-----------

.. code-block:: python

    from pydantic import BaseModel
    from typing import Dict, List

    class QueryResponse(BaseModel):
        """Réponse du système RAG."""
        
        request_id: str
            """Identifiant unique de la requête."""
        
        query: str
            """Requête originale."""
        
        intent: str
            """Intention détectée (general_knowledge|sql_query|analysis)."""
        
        status: str
            """Statut de traitement (completed|error|timeout)."""
        
        final_output: str
            """Réponse en langage naturel."""
        
        execution_time: float
            """Temps d'exécution en secondes."""
        
        metadata: Dict
            """Métadonnées supplémentaires."""

Exemples d'Utilisation
======================

Python avec Requests
--------------------

.. code-block:: python

    import requests
    import json

    # Configuration
    BASE_URL = "http://localhost:8000"
    
    # Requête
    payload = {
        "query": "Quelle est la capital de la France?",
        "context": "Questions de géographie",
        "max_results": 5
    }
    
    # Appel API
    response = requests.post(
        f"{BASE_URL}/api/query",
        json=payload,
        timeout=30
    )
    
    # Résultat
    if response.status_code == 200:
        result = response.json()
        print(f"Réponse: {result['final_output']}")
        print(f"Temps: {result['execution_time']}s")
    else:
        print(f"Erreur: {response.status_code}")

Python avec AsyncIO
-------------------

.. code-block:: python

    import asyncio
    import aiohttp

    async def query_system(query_text):
        """Requête asynchrone du système RAG."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query_text,
                "context": "Questions",
                "max_results": 10
            }
            
            async with session.post(
                "http://localhost:8000/api/query",
                json=payload
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"Erreur: {resp.status}")

    # Utilisation
    asyncio.run(query_system("Quelle est la capitale de la France?"))

JavaScript avec Fetch
---------------------

.. code-block:: javascript

    async function querySystem(query) {
        const response = await fetch('http://localhost:8000/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                context: 'Questions',
                max_results: 10
            })
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Réponse:', result.final_output);
            return result;
        } else {
            throw new Error(`Erreur: ${response.status}`);
        }
    }

    // Utilisation
    querySystem('Quelle est la capitale de la France?')
        .then(result => console.log(result))
        .catch(error => console.error(error));

WebSocket Client
----------------

.. code-block:: python

    import asyncio
    import websockets
    import json

    async def test_mcp_gateway():
        """Test de la passerelle MCP."""
        uri = "ws://localhost:8000/ws"
        
        async with websockets.connect(uri) as websocket:
            # Demander liste des outils
            request = {
                "method": "list_tools",
                "params": {}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            
            print(f"Outils disponibles: {response}")

    asyncio.run(test_mcp_gateway())

Gestion des Erreurs
===================

Codes d'Erreur HTTP
-------------------

.. csv-table::
   :header: "Code", "Signification", "Explication"
   :widths: 10, 25, 65

   "200", "OK", "Requête traitée avec succès"
   "400", "Bad Request", "Paramètres invalides ou manquants"
   "401", "Unauthorized", "Authentification requise"
   "403", "Forbidden", "Accès refusé"
   "404", "Not Found", "Endpoint inexistant"
   "429", "Too Many Requests", "Limite de requêtes dépassée"
   "500", "Internal Server Error", "Erreur interne du serveur"
   "502", "Bad Gateway", "Passerelle MCP indisponible"
   "503", "Service Unavailable", "Service temporairement indisponible"
   "504", "Gateway Timeout", "Délai d'exécution dépassé"

Format d'Erreur
---------------

.. code-block:: json

    {
      "status": "error",
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "error": {
        "type": "ValidationError|ExecutionError|TimeoutError",
        "message": "Description de l'erreur",
        "details": {
          "field": "query",
          "reason": "Requête vide"
        }
      }
    }

Authentification (Futur)
========================

OAuth2 + JWT
-----------

.. code-block:: bash

    # Obtenir un token
    curl -X POST "http://localhost:8000/token" \
      -d "username=user&password=pass"

    # Utiliser le token
    curl -H "Authorization: Bearer <token>" \
      -X POST "http://localhost:8000/api/query" \
      -d {...}

Rate Limiting
=============

Limites par Défaut
------------------

- **50 requêtes par minute** par utilisateur
- **500 caractères maximum** par requête
- **30 secondes de timeout** par requête

Configuration Personnalisée
----------------------------

Dans le fichier ``.env`` :

.. code-block:: bash

    # Rate limiting
    RATE_LIMIT_PER_MINUTE=100
    RATE_LIMIT_BURST=10
    
    # Timeouts
    REQUEST_TIMEOUT=60
    
    # Limites de requête
    MAX_QUERY_LENGTH=1000
    MAX_RESULTS=100

Voir aussi
==========

- :doc:`guide_demarrage` pour l'installation
- :doc:`architecture` pour comprendre le système
- :doc:`mcp_protocol` pour le protocole MCP
- `FastAPI Docs <https://fastapi.tiangolo.com/>`_
