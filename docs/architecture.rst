Architecture du Système
======================

Vue d'Ensemble
==============

Le système est architecturé en microservices conteneurisés avec une communication par WebSocket et MCP.

.. graphviz::

   digraph architecture {
     rankdir=LR;
     
     User [shape=box, label="Utilisateur"];
     Web [shape=box, label="Interface Web"];
     FastAPI [shape=box, label="Orchestrateur\n(FastAPI)", color=lightblue];
     LangGraph [shape=box, label="Pipeline LangGraph"];
     Agents [shape=box, label="Agents Spécialisés", color=lightgreen];
     MCP [shape=box, label="Passerelle MCP"];
     DBs [shape=box, label="Bases de Données\n(PostgreSQL+pgvector)"];
     
     User -> Web;
     Web -> FastAPI;
     FastAPI -> LangGraph;
     LangGraph -> Agents;
     Agents -> MCP;
     MCP -> DBs;
     
     style=filled;
     fillcolor=lightyellow;
   }

Composants Principaux
=====================

Orchestrateur (FastAPI)
-----------------------

**Location** : ``orchestrateur/main.py``

**Responsabilités** :

- Réception des requêtes utilisateur
- Orchestration du pipeline LangGraph
- Gestion des états et transitions
- Réponse avec résultats finaux

**Points d'Entrée** :

.. code-block:: python

    POST /api/query          # Traiter une requête
    GET  /health            # Vérifier la santé du service

Pipeline LangGraph
------------------

**Location** : ``orchestrateur/src/orchestrator/orchestrator.py``

**Architecture** :

Le pipeline utilise LangGraph avec un graphe d'états défini :

.. code-block::

    ┌─────────────┐
    │   START     │
    └──────┬──────┘
           │
           ▼
    ┌──────────────────┐
    │  Intent Agent    │ ◄─── Analyse l'intention de la requête
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ Retriever Agent  │ ◄─── Récupère les schémas des BDD
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │   SQL Agent      │ ◄─── Génère les requêtes SQL
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ Validator Agent  │ ◄─── Valide les requêtes SQL
    └──────┬───────────┘
           │
      [Conditionnel]
      /    |     \
     ✓     ✗     ?
    │      │      │
    ▼      ▼      ▼
   EXEC  ERREUR RETRY
    │      │
    ▼      ▼
    ┌──────────────────┐
    │ Execute Agent    │ ◄─── Exécute les requêtes en fédéré
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ Composer Agent   │ ◄─── Compose la réponse finale
    └──────┬───────────┘
           │
           ▼
    ┌─────────────┐
    │     END     │
    └─────────────┘

État du Système (QueryState)
-----------------------------

.. code-block:: python

    class QueryState(TypedDict):
        """État partagé du pipeline"""
        query: str                           # Requête utilisateur
        intent: str                          # Intention détectée
        schemas: dict                        # Schémas des BDD
        sql_queries: dict                    # Requêtes SQL générées
        validation_results: dict             # Résultats validation
        execution_results: dict              # Résultats exécution
        final_output: str                    # Réponse finale
        errors: list[str]                    # Erreurs accumulées

Agents Spécialisés
==================

Architecture Agent
------------------

Tous les agents héritent de ``BaseAgent`` et implémentent une méthode ``run()``.

.. code-block:: python

    BaseAgent (abstract)
    │
    ├─ IntentAgent       # Classification intention
    ├─ RetrieverAgent    # Récupération schémas
    ├─ SQLAgent          # Génération SQL
    ├─ ValidatorAgent    # Validation SQL
    └─ ComposerAgent     # Composition réponse

Flux par Agent
--------------

IntentAgent
~~~~~~~~~~~

.. code-block::

    Requête utilisateur
           │
           ▼
    ┌──────────────────┐
    │  Analyse LLM     │
    │ (Intent Match)   │
    └──────┬───────────┘
           │
           ▼
    {intent, entities, databases}

RetrieverAgent
~~~~~~~~~~~~~~

.. code-block::

    Liste des bases à interroger
           │
           ▼
    ┌──────────────────┐
    │  Appel MCP       │
    │ (Récupération)   │
    └──────┬───────────┘
           │
           ▼
    {schemas: {db1: {...}, db2: {...}}}

SQLAgent
~~~~~~~~

.. code-block::

    Intention + Schémas
           │
           ▼
    ┌──────────────────┐
    │ Génération LLM   │
    │  (Fallback: RB)  │
    └──────┬───────────┘
           │
           ▼
    {sql_queries: {db1: "SELECT...", db2: "..."}}

ValidatorAgent
~~~~~~~~~~~~~~

.. code-block::

    Requêtes SQL
           │
           ▼
    ┌──────────────────┐
    │ Validation       │
    │ (Structure+Len)  │
    └──────┬───────────┘
           │
           ▼
    {validation_results: {db1: {valid: true}, db2: {valid: true}}}

ExecutorAgent
~~~~~~~~~~~~~

.. code-block::

    Requêtes SQL validées
           │
           ▼
    ┌──────────────────┐
    │  Exécution MCP   │
    │  (Fédérée)       │
    └──────┬───────────┘
           │
           ▼
    {execution_results: {db1: {...}, db2: {...}}}

ComposerAgent
~~~~~~~~~~~~~

.. code-block::

    Résultats exécution
           │
           ▼
    ┌──────────────────┐
    │ Composition LLM  │
    │ (Langage nat.)   │
    └──────┬───────────┘
           │
           ▼
    "Réponse naturelle..."

Communication MCP
=================

Passerelle MCP
--------------

**Location** : ``mcp/mcp-gateway/``

**Rôle** :

- Serveur FastAPI avec WebSocket
- Pool de clients MCP (un par serveur de base de données)
- Routage des requêtes outils et ressources

Flux de Communication
---------------------

.. code-block::

    ┌──────────────────┐
    │   Orchestrateur  │
    └────────┬─────────┘
             │
             │ WebSocket
             │ {"method": "call_tool", "tool": "execute_sql", ...}
             ▼
    ┌──────────────────┐
    │  MCP Gateway     │
    └────────┬─────────┘
             │
             │ SSE
             │ {"method": "call_tool", ...}
             ▼
    ┌──────────────────┐
    │   MCP Server     │
    │ (PostgreSQL)     │
    └────────┬─────────┘
             │
             │ Résultat
             ▼
    ┌──────────────────┐
    │   Base de Données│
    └──────────────────┘

Outils MCP Disponibles
----------------------

.. code-block:: json

    {
      "tools": [
        {
          "name": "execute_sql",
          "description": "Exécute une requête SQL",
          "inputSchema": {
            "properties": {
              "sql": {"type": "string"},
              "database": {"type": "string"}
            }
          }
        },
        {
          "name": "list_schemas",
          "description": "Liste les schémas disponibles"
        },
        {
          "name": "get_schema",
          "description": "Récupère le schéma d'une table"
        }
      ]
    }

Flux de Requête Complet
======================

Étape 1 : Réception
-------------------

.. code-block:: bash

    POST /api/query
    Content-Type: application/json
    {
      "query": "Quelle est la capitale de la France?"
    }

Étape 2 : Pipeline
------------------

1. **Intent Analysis** (IntentAgent)
   - Déterminer : général / base de données
   - Extraire entités
   - Identifier bases concernées

2. **Schema Retrieval** (RetrieverAgent)
   - Appeler MCP pour schémas
   - Contextualiser pour LLM

3. **SQL Generation** (SQLAgent)
   - Générer requêtes SQL
   - Validation syntaxe basique

4. **SQL Validation** (ValidatorAgent)
   - Vérifier structure
   - Vérifier longueur (sécurité)

5. **Execution** (QueryRunner)
   - Exécuter via MCP (fédéré)
   - Récupérer résultats

6. **Response Composition** (ComposerAgent)
   - Générer réponse naturelle
   - Contextualiser résultats

Étape 3 : Réponse
-----------------

.. code-block:: json

    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "query": "Quelle est la capitale de la France?",
      "intent": "general_knowledge",
      "status": "completed",
      "final_output": "La capitale de la France est Paris.",
      "execution_time": 1.23,
      "metadata": {
        "agents_used": ["intent", "composer"],
        "databases_queried": []
      }
    }

Modèles de Données
==================

QueryRequest
------------

.. code-block:: python

    class QueryRequest(BaseModel):
        """Requête entrante"""
        query: str                  # Requête utilisateur
        context: Optional[str]      # Contexte optionnel
        max_results: int = 10       # Limite résultats

QueryResponse
-------------

.. code-block:: python

    class QueryResponse(BaseModel):
        """Réponse du système"""
        request_id: str             # ID unique
        query: str                  # Requête originale
        intent: str                 # Intention détectée
        status: str                 # completed/error/timeout
        final_output: str           # Réponse finale
        execution_time: float       # Temps en secondes
        metadata: dict              # Métadonnées additionnelles

Sécurité & Validation
====================

Stratégies de Sécurité
----------------------

1. **SQL Injection Prevention**
   - Validation syntaxe SQL
   - Vérification longueur
   - Parameterized queries (MCP)

2. **Access Control**
   - Authentification API (à venir)
   - Autorisation par base de données

3. **Rate Limiting**
   - Limiter requêtes par utilisateur
   - Limiter temps exécution

4. **Error Handling**
   - Ne pas exposer détails BD
   - Logs sécurisés

Validation SQL
--------------

Le ValidatorAgent vérifie :

- Syntaxe SQL valide
- Longueur raisonnable (< 10000 caractères)
- Pas de patterns dangereux (DROP, TRUNCATE, etc.)

Performances
============

Optimisations
-------------

1. **Async/Await** : Requêtes non-bloquantes
2. **MCP Pooling** : Réutilisation connexions
3. **Caching** : Schémas en cache
4. **Parallelisation** : Exécution fédérée en parallèle

Métriques
---------

- Temps moyen requête : ~1-2 secondes
- Throughput : ~100 req/min par instance
- Latence MCP : ~100-200ms

Scalabilité
-----------

- Orchestrateur : Stateless (scale horizontalement)
- MCP Gateway : Pool de connexions (scale verticalement)
- Bases de données : Fédération (indépendantes)

Voir aussi
==========

- :doc:`agents` pour détails des agents
- :doc:`mcp_protocol` pour le protocole MCP
- :doc:`api_reference` pour les endpoints
