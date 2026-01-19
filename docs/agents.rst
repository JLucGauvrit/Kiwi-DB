Les Agents du Système
====================

Vue d'Ensemble
==============

Le système RAG fédéré utilise 6 agents spécialisés, chacun responsable d'une tâche spécifique dans le pipeline.

.. code-block::

    ┌─────────────────────────────────────────────────────────┐
    │              Agent Registry & Pool                       │
    └─────────────────────────────────────────────────────────┘
    │
    ├─ IntentAgent          ◄─── Analyse intention
    ├─ RetrieverAgent       ◄─── Récupère schémas
    ├─ SQLAgent             ◄─── Génère SQL
    ├─ ValidatorAgent       ◄─── Valide SQL
    ├─ ExecutorAgent        ◄─── Exécute requêtes
    └─ ComposerAgent        ◄─── Compose réponses

BaseAgent (Classe de Base)
=========================

Tous les agents héritent de ``BaseAgent``.

.. code-block:: python

    @abstractmethod
    class BaseAgent:
        """
        Classe abstraite pour tous les agents RAG.
        
        Responsabilités:
        - Initialiser un modèle de langage (Ollama)
        - Fournir une interface run() pour le traitement
        - Gérer les erreurs et logging
        """
        
        def __init__(self, config: dict):
            """
            Initialiser l'agent.
            
            @param config: Configuration de l'agent
                - ollama_base_url: URL du serveur Ollama
                - model: Nom du modèle Ollama
                - temperature: Température (0-1)
            """
            self.llm = ChatOllama(
                base_url=config.get('ollama_base_url'),
                model=config.get('model', 'mistral'),
                temperature=config.get('temperature', 0.7)
            )
        
        @abstractmethod
        def run(self, state: QueryState) -> dict:
            """
            Exécuter l'agent.
            
            @param state: État courant du pipeline
            @return: Mise à jour de l'état
            """
            pass

Architecture d'Héritage
---------------------

.. code-block::

    ┌──────────────────┐
    │   BaseAgent      │
    │  (abstract)      │
    └────────┬─────────┘
             │
       ┌─────┴─────────────────────────┬─────────────────┬───────┐
       │                               │                 │       │
       ▼                               ▼                 ▼       ▼
    IntentAgent              RetrieverAgent         SQLAgent   ValidatorAgent
    ComposerAgent                 ExecutorAgent

IntentAgent
===========

**Responsabilité** : Classifier l'intention de la requête utilisateur.

**Location** : ``orchestrateur/src/agents/intent_agent.py``

Flux
----

.. code-block::

    Requête utilisateur
           │
           ▼
    ┌──────────────────────────────┐
    │ Prompt d'analyse d'intention │
    │ - Intention: ?               │
    │ - Entités: ?                 │
    │ - Bases concernées: ?        │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │    Appel ChatOllama          │
    │ (Modèle de langage local)    │
    └──────────────────────────────┘
           │
           ▼
    Parsing réponse LLM
           │
           ▼
    state['intent'] = "general_knowledge" | "sql_query" | "analysis"
    state['entities'] = {...}
    state['databases'] = [...]

Paramètres d'Entrée
------------------

.. code-block:: python

    state['query']      # Requête utilisateur (obligatoire)

Paramètres de Sortie
-------------------

.. code-block:: python

    state['intent']     # Type: str - L'intention détectée
    state['entities']   # Type: dict - Entités extraites
    state['databases']  # Type: list - Bases concernées

Intentions Possibles
-------------------

.. csv-table::
   :header: "Intention", "Exemple", "Nécessite BD"
   :widths: 20, 40, 20

   "general_knowledge", "Quelle est la capitale de la France?", "Non"
   "sql_query", "Liste tous les employés du département IT", "Oui"
   "analysis", "Analysez les tendances de vente 2025", "Probablement"

Prompt Utilisé
--------------

.. code-block:: text

    Analyse la requête suivante et détermine:
    1. L'intention (general_knowledge, sql_query, ou analysis)
    2. Les entités nommées (personnes, lieux, dates, etc.)
    3. Les bases de données probablement concernées
    
    Requête: {query}
    
    Réponds au format JSON:
    {
        "intent": "...",
        "entities": {...},
        "databases": [...]
    }

RetrieverAgent
==============

**Responsabilité** : Récupérer les schémas des bases de données via MCP.

**Location** : ``orchestrateur/src/agents/retriever_agent.py``

Flux
----

.. code-block::

    Intention + Bases concernées
           │
           ▼
    ┌──────────────────────────────┐
    │  Itération sur les bases     │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │   Appel MCP via Gateway      │
    │   (SSE → PostgreSQL)         │
    │   Tool: list_schemas         │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │ Récupération des colonnes    │
    │ pour chaque table            │
    │ Tool: get_schema             │
    └──────────────────────────────┘
           │
           ▼
    state['schemas'] = {
        'db1': {
            'table1': {...},
            'table2': {...}
        }
    }

Paramètres d'Entrée
------------------

.. code-block:: python

    state['databases']  # Bases à interroger (de IntentAgent)

Paramètres de Sortie
-------------------

.. code-block:: python

    state['schemas']    # Type: dict - Schémas récupérés

Exemple de Schéma Retourné
--------------------------

.. code-block:: python

    {
        'employees': {
            'columns': [
                {'name': 'id', 'type': 'integer', 'nullable': False},
                {'name': 'name', 'type': 'varchar', 'nullable': False},
                {'name': 'email', 'type': 'varchar', 'nullable': True},
                {'name': 'department_id', 'type': 'integer', 'nullable': False},
            ],
            'primary_key': 'id',
            'foreign_keys': [
                {'column': 'department_id', 'references': 'departments.id'}
            ]
        }
    }

Communication MCP
-----------------

.. code-block:: python

    # Appel MCP pour lister les schémas
    schemas = await mcp_client.call_tool(
        'list_schemas',
        {'database': 'public'}
    )
    
    # Appel MCP pour obtenir une table spécifique
    table_schema = await mcp_client.call_tool(
        'get_schema',
        {
            'database': 'public',
            'table': 'employees'
        }
    )

SQLAgent
========

**Responsabilité** : Générer les requêtes SQL basées sur l'intention et les schémas.

**Location** : ``orchestrateur/src/agents/sql_agent.py``

Flux
----

.. code-block::

    Intention + Entités + Schémas
           │
           ▼
    ┌──────────────────────────────┐
    │  Construction contexte       │
    │  pour le LLM                 │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │   Génération LLM (primaire)  │
    │   Prompt avec schémas        │
    └──────────────────────────────┘
           │
           ▼
    [Succes?]──NO──▶ Fallback: Génération basée règles
           │
          YES
           │
           ▼
    state['sql_queries'] = {
        'db1': 'SELECT ...',
        'db2': 'SELECT ...'
    }

Génération LLM (Primaire)
------------------------

.. code-block:: python

    prompt = """
    Sur la base de la requête utilisateur et du schéma fourni,
    génère une requête SQL sécurisée.
    
    Schéma:
    {schémas formatés}
    
    Requête utilisateur: {requête}
    
    Contraintes:
    - Requête SELECT uniquement
    - Pas de JOIN complexes sans besoin
    - Commentaires explicatifs dans la requête
    
    Réponse au format JSON:
    {"sql_query": "..."}
    """

Fallback : Génération Basée Règles
---------------------------------

.. code-block:: python

    def generate_rule_based(intent, entities, schemas):
        """
        Générer une requête SQL basée sur des règles
        si le LLM échoue.
        """
        if intent == 'list_all':
            table = next(iter(schemas.keys()))
            return f"SELECT * FROM {table} LIMIT 100;"
        
        elif intent == 'search':
            # Construire une requête de recherche simple
            ...
        
        else:
            raise ValueError(f"Intent non supporté: {intent}")

Paramètres d'Entrée
------------------

.. code-block:: python

    state['intent']     # Intention de la requête
    state['entities']   # Entités extraites
    state['schemas']    # Schémas des bases
    state['query']      # Requête originale

Paramètres de Sortie
-------------------

.. code-block:: python

    state['sql_queries']    # Type: dict[str, str] - SQL générée

ValidatorAgent
==============

**Responsabilité** : Valider la sécurité et la correction syntaxique des requêtes SQL.

**Location** : ``orchestrateur/src/agents/validator_agent.py``

Flux
----

.. code-block::

    Requêtes SQL générées
           │
           ▼
    ┌──────────────────────────────┐
    │ Validation Syntaxe           │
    │ - Parsage SQL                │
    │ - Vérification tokens        │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │ Validation Sécurité          │
    │ - Longueur < 10000 chars     │
    │ - Pas de DROP/TRUNCATE/etc   │
    │ - Pas de UNION ALL           │
    └──────────────────────────────┘
           │
           ▼
    state['validation_results'] = {
        'db1': {'valid': True},
        'db2': {'valid': False, 'error': '...'}
    }

Règles de Validation
-------------------

.. csv-table::
   :header: "Règle", "Détail", "Critique"
   :widths: 20, 40, 15

   "Syntaxe SQL", "Vérifier parsage valide", "Oui"
   "Longueur", "< 10000 caractères", "Oui"
   "Commandes interdites", "DROP, TRUNCATE, EXEC, etc.", "Oui"
   "UNION", "Pas de UNION ALL", "Oui"
   "Temps d'exécution", "Estimation < 30s", "Non"

Patterns Interdits
------------------

.. code-block:: python

    DANGEROUS_PATTERNS = [
        r'DROP\s+(TABLE|DATABASE)',
        r'TRUNCATE',
        r'DELETE.*FROM.*WHERE',
        r'UPDATE.*SET',
        r'INSERT\s+INTO',
        r'CREATE\s+TABLE',
        r'ALTER\s+TABLE',
        r'EXECUTE|EXEC',
        r'DECLARE.*CURSOR',
        r';.*--.*DROP',  # Commentaires cachés
    ]

Paramètres d'Entrée
------------------

.. code-block:: python

    state['sql_queries']    # Requêtes à valider

Paramètres de Sortie
-------------------

.. code-block:: python

    state['validation_results']     # Type: dict[str, dict]

ExecutorAgent (QueryRunner)
===========================

**Responsabilité** : Exécuter les requêtes SQL validées via MCP.

**Location** : ``orchestrateur/src/executor/query_runner.py``

Flux
----

.. code-block::

    Requêtes SQL validées
           │
           ▼
    ┌──────────────────────────────┐
    │  Itération sur requêtes      │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │  Appel MCP en parallèle      │
    │  Tool: execute_sql           │
    │  Database: db1, db2, ...     │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │  Collecte résultats SSE      │
    │  Gestion erreurs             │
    └──────────────────────────────┘
           │
           ▼
    state['execution_results'] = {
        'db1': {
            'success': True,
            'rows': [...],
            'count': 42,
            'execution_time': 0.125
        }
    }

Exécution Parallèle
-------------------

.. code-block:: python

    async def execute_federated(sql_queries: dict) -> dict:
        """
        Exécuter plusieurs requêtes en parallèle.
        """
        tasks = [
            execute_via_mcp(db, sql)
            for db, sql in sql_queries.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            db: result
            for db, result in zip(sql_queries.keys(), results)
        }

Format du Résultat
------------------

.. code-block:: python

    {
        'success': True,           # Booléen
        'rows': [
            {'col1': 'val1', 'col2': 'val2'},
            ...
        ],
        'count': 42,               # Nombre de lignes
        'execution_time': 0.125,   # Secondes
        'error': None              # Message erreur ou None
    }

Paramètres d'Entrée
------------------

.. code-block:: python

    state['sql_queries']              # Requêtes à exécuter
    state['validation_results']       # Résultats validation

Paramètres de Sortie
-------------------

.. code-block:: python

    state['execution_results']        # Type: dict

ComposerAgent
=============

**Responsabilité** : Composer une réponse en langage naturel à partir des résultats.

**Location** : ``orchestrateur/src/agents/composer_agent.py``

Flux
----

.. code-block::

    Intention + Requête + Résultats
           │
           ▼
    ┌──────────────────────────────┐
    │  Préparation contexte LLM    │
    │  - Résultats formatés        │
    │  - Requête originale         │
    │  - Intention                 │
    └──────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────┐
    │  Appel ChatOllama            │
    │  (Composition naturelle)      │
    └──────────────────────────────┘
           │
           ▼
    state['final_output'] = "Réponse naturelle..."

Prompt Utilisé
--------------

.. code-block:: text

    Basé sur les résultats suivants, réponse à la question
    de l'utilisateur de manière concise et naturelle.
    
    Requête originale: {query}
    
    Résultats obtenus:
    {results_formatted}
    
    Remarques:
    - Soyez concis et clair
    - Utilisez le français
    - Si aucun résultat, expliquez-le
    - Évitez de montrer le SQL

Paramètres d'Entrée
------------------

.. code-block:: python

    state['query']                  # Requête originale
    state['intent']                 # Intention
    state['execution_results']      # Résultats exécution
    state['final_output']           # Réponse

Paramètres de Sortie
-------------------

.. code-block:: python

    state['final_output']           # Type: str - Réponse finale

Registry des Agents
===================

Le ``AgentRegistry`` gère l'instanciation et l'accès à tous les agents.

.. code-block:: python

    class AgentRegistry:
        """Registre centralisé des agents."""
        
        def __init__(self, config: dict):
            """Initialiser tous les agents."""
            self.agents = {
                'intent': IntentAgent(config),
                'retriever': RetrieverAgent(config),
                'sql': SQLAgent(config),
                'validator': ValidatorAgent(config),
                'executor': ExecutorAgent(config),
                'composer': ComposerAgent(config),
            }
        
        def get_agent(self, agent_name: str):
            """Récupérer un agent par nom."""
            if agent_name not in self.agents:
                raise ValueError(f"Agent inconnu: {agent_name}")
            return self.agents[agent_name]

Utilisation
-----------

.. code-block:: python

    # Créer le registre
    registry = AgentRegistry(config)
    
    # Utiliser dans le pipeline
    intent_agent = registry.get_agent('intent')
    state = intent_agent.run(state)

Voir aussi
==========

- :doc:`architecture` pour le flux global
- :doc:`api_reference` pour les endpoints
- :doc:`mcp_protocol` pour la communication
