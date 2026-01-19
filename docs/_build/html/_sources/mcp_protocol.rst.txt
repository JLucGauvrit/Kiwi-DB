Protocole MCP (Model Context Protocol)
======================================

Vue d'Ensemble
==============

MCP est un protocole standardisé pour la communication entre les modèles de langage et les ressources externes (bases de données, APIs, fichiers, etc.).

.. code-block::

    ┌──────────────────┐
    │   Orchestrateur  │
    │   (Client MCP)   │
    └────────┬─────────┘
             │
             │ WebSocket
             │
    ┌────────▼─────────┐
    │  MCP Gateway     │
    │  (Server MCP)    │
    └────────┬─────────┘
             │
             │ SSE (Server-Sent Events)
             │
    ┌────────▼──────────────┐
    │  MCP Server Sessio    │
    │  (PostgreSQL, etc.)   │
    └───────────────────────┘

Architecture MCP
================

Couches de Communication
------------------------

1. **Transport Layer** (Couche Transport)
   - WebSocket (Orchestrateur → Gateway)
   - SSE (Gateway → Serveur MCP)

2. **Protocol Layer** (Couche Protocole)
   - JSON-RPC 2.0
   - Requêtes/Réponses standardisées

3. **Resource Layer** (Couche Ressources)
   - Tools (Outils disponibles)
   - Resources (Ressources disponibles)

Requête MCP Standard
--------------------

.. code-block:: json

    {
      "jsonrpc": "2.0",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "method": "tools/call",
      "params": {
        "name": "execute_sql",
        "arguments": {
          "sql": "SELECT * FROM employees",
          "database": "postgres"
        }
      }
    }

Réponse MCP Standard
--------------------

.. code-block:: json

    {
      "jsonrpc": "2.0",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "result": {
        "content": [
          {
            "type": "text",
            "text": "Requête exécutée avec succès"
          },
          {
            "type": "text",
            "text": "[{\"id\": 1, \"name\": \"Alice\"}, ...]"
          }
        ]
      }
    }

Outils Disponibles
==================

liste_schemas
-----------

**Description** : Lister tous les schémas/bases disponibles

**Requête** :

.. code-block:: json

    {
      "method": "tools/call",
      "params": {
        "name": "list_schemas",
        "arguments": {
          "database": "public"
        }
      }
    }

**Réponse** :

.. code-block:: json

    {
      "result": {
        "content": [
          {
            "type": "text",
            "text": "Schémas disponibles: public, information_schema"
          }
        ]
      }
    }

get_schema
----------

**Description** : Récupérer le schéma d'une table

**Requête** :

.. code-block:: json

    {
      "method": "tools/call",
      "params": {
        "name": "get_schema",
        "arguments": {
          "database": "public",
          "table": "employees"
        }
      }
    }

**Réponse** :

.. code-block:: json

    {
      "result": {
        "content": [
          {
            "type": "text",
            "text": "Schéma de employees..."
          }
        ]
      }
    }

execute_sql
-----------

**Description** : Exécuter une requête SQL

**Requête** :

.. code-block:: json

    {
      "method": "tools/call",
      "params": {
        "name": "execute_sql",
        "arguments": {
          "sql": "SELECT id, name FROM employees LIMIT 10",
          "database": "postgres"
        }
      }
    }

**Réponse** :

.. code-block:: json

    {
      "result": {
        "content": [
          {
            "type": "text",
            "text": "Résultats (10 lignes):"
          },
          {
            "type": "text",
            "text": "[{\"id\": 1, \"name\": \"Alice\", \"email\": \"alice@example.com\"}, ...]"
          }
        ]
      }
    }

Flux d'Exécution Complet
=========================

Étape 1 : Requête
-----------------

L'orchestrateur envoie une requête MCP au gateway :

.. code-block:: python

    # orchestrateur/src/mcp_client.py
    response = await mcp_client.call_tool(
        'execute_sql',
        {
            'sql': 'SELECT * FROM employees',
            'database': 'postgres'
        }
    )

Étape 2 : Gateway Reçoit
------------------------

Le gateway WebSocket reçoit et valide :

.. code-block:: python

    # mcp/mcp-gateway/main.py
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        message = await websocket.receive_json()
        response = await handle_request(message)
        await websocket.send_json(response)

Étape 3 : Routage vers Server
-----------------------------

Le gateway appelle le bon serveur MCP :

.. code-block:: python

    # mcp/mcp-gateway/mcp_client.py
    async def call_tool(self, database, tool_name, arguments):
        client = self.client_pool.get_client(database)
        result = await client.call_tool(tool_name, arguments)
        return result

Étape 4 : Exécution Server
---------------------------

Le serveur MCP exécute le tool :

.. code-block:: python

    # PostgreSQL MCP Server
    async def execute_sql(arguments):
        sql = arguments['sql']
        conn = await get_connection()
        result = await conn.fetch(sql)
        return format_result(result)

Étape 5 : Retour de Réponse
---------------------------

Le résultat remonte à l'orchestrateur :

.. code-block:: python

    response = {
        'success': True,
        'rows': [...],
        'count': 42,
        'execution_time': 0.125
    }

Implémentation côté Client (Orchestrateur)
===========================================

MCPGatewayClient
----------------

.. code-block:: python

    class MCPGatewayClient:
        """Client WebSocket pour MCP Gateway."""
        
        def __init__(self, gateway_url: str):
            """Initialiser le client."""
            self.gateway_url = gateway_url
            self.websocket = None
            self.lock = asyncio.Lock()
        
        async def connect(self):
            """Établir la connexion WebSocket."""
            self.websocket = await websockets.connect(
                f"ws://{self.gateway_url}/ws"
            )
        
        async def send_request(self, request: dict) -> dict:
            """Envoyer une requête et attendre la réponse."""
            async with self.lock:
                await self.websocket.send(json.dumps(request))
                response = await self.websocket.recv()
                return json.loads(response)
        
        async def call_tool(self, tool_name: str, arguments: dict) -> dict:
            """Appeler un tool MCP."""
            request = {
                'method': 'tools/call',
                'params': {
                    'name': tool_name,
                    'arguments': arguments
                }
            }
            return await self.send_request(request)

Utilisation
-----------

.. code-block:: python

    # Créer le client
    mcp_client = MCPGatewayClient('localhost:8000')
    
    # Connecter
    await mcp_client.connect()
    
    # Appeler un tool
    result = await mcp_client.call_tool(
        'execute_sql',
        {
            'sql': 'SELECT * FROM employees',
            'database': 'postgres'
        }
    )

Implémentation côté Server (Gateway)
=====================================

MCPClientPool
-----------

.. code-block:: python

    class MCPClientPool:
        """Gère plusieurs connexions MCP vers différents serveurs."""
        
        def __init__(self, servers_config: dict):
            """
            Initialiser le pool.
            
            @param servers_config: Dict {database: {uri, env}}
            """
            self.clients = {}
            self.config = servers_config
        
        async def initialize(self):
            """Initialiser tous les clients."""
            for db_name, db_config in self.config.items():
                client = MCPClient(db_name, db_config)
                await client.connect()
                self.clients[db_name] = client
        
        async def call_tool(self, database: str, tool_name: str, 
                           arguments: dict) -> dict:
            """Appeler un tool sur un serveur spécifique."""
            client = self.clients.get(database)
            if not client:
                raise ValueError(f"Database {database} not found")
            
            return await client.call_tool(tool_name, arguments)

MCPClient (Single Server)
------------------------

.. code-block:: python

    class MCPClient:
        """Client MCP pour un serveur unique."""
        
        def __init__(self, name: str, config: dict):
            """Initialiser le client."""
            self.name = name
            self.uri = config['uri']  # sse://localhost:8000/sse
            self.session = None
        
        async def connect(self):
            """Se connecter au serveur MCP."""
            # SSE connection via sse_client
            self.session = await sse_client(self.uri)
        
        async def call_tool(self, tool_name: str, arguments: dict):
            """Appeler un tool."""
            return await self.session.call_tool(tool_name, arguments)

Gestion des Erreurs
===================

Types d'Erreurs MCP
-------------------

.. code-block:: json

    {
      "jsonrpc": "2.0",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "error": {
        "code": -32600,
        "message": "Invalid Request",
        "data": {
          "details": "Missing 'sql' parameter"
        }
      }
    }

Codes d'Erreur Standard
----------------------

.. csv-table::
   :header: "Code", "Signification", "Explication"
   :widths: 10, 25, 65

   "-32700", "Parse error", "Erreur parsing JSON"
   "-32600", "Invalid Request", "Requête invalide"
   "-32601", "Method not found", "Outil inexistant"
   "-32602", "Invalid params", "Paramètres invalides"
   "-32603", "Internal error", "Erreur interne serveur"
   "-32000", "Server error", "Erreur serveur générale"

Handling côté Orchestrateur
----------------------------

.. code-block:: python

    async def execute_with_retry(tool_name: str, arguments: dict, 
                                 max_retries: int = 3):
        """Exécuter un tool avec retry."""
        for attempt in range(max_retries):
            try:
                result = await mcp_client.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

Sécurité MCP
============

Validation Requêtes
-------------------

.. code-block:: python

    # Dans le Gateway
    def validate_sql_query(sql: str):
        """Valider une requête SQL."""
        dangerous_patterns = [
            r'DROP\s+TABLE',
            r'TRUNCATE',
            r'DELETE.*FROM',
            r'UPDATE\s+',
            r'INSERT\s+INTO',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                raise ValueError(f"Requête dangereuse détectée")

Authentification
----------------

.. code-block:: python

    # Futur: Ajouter authentification JWT
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        # Valider le token
        token = websocket.headers.get('Authorization')
        if not is_valid_token(token):
            await websocket.close(code=1008)

Timeouts
--------

.. code-block:: python

    async def call_tool_with_timeout(tool_name: str, arguments: dict,
                                     timeout: int = 30):
        """Appeler un tool avec timeout."""
        try:
            result = await asyncio.wait_for(
                mcp_client.call_tool(tool_name, arguments),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool {tool_name} timed out after {timeout}s")

Monitoring & Debugging
======================

Logs MCP
--------

.. code-block:: python

    import logging
    
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Sending MCP request: {request}")
    logger.info(f"Tool {tool_name} executed in {elapsed_time}ms")
    logger.error(f"MCP error: {error_message}")

Métriques Prometheus
-------------------

.. code-block:: python

    from prometheus_client import Counter, Histogram
    
    mcp_calls = Counter('mcp_calls_total', 'Total MCP calls', ['tool'])
    mcp_duration = Histogram('mcp_duration_seconds', 'MCP call duration', ['tool'])
    
    @mcp_duration.labels(tool=tool_name).time()
    async def execute():
        mcp_calls.labels(tool=tool_name).inc()
        return await mcp_client.call_tool(tool_name, arguments)

Tracing Distribué
-----------------

.. code-block:: python

    from opentelemetry import trace
    
    tracer = trace.get_tracer(__name__)
    
    async def call_tool(tool_name: str, arguments: dict):
        with tracer.start_as_current_span("mcp.call_tool") as span:
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tool.arguments", str(arguments))
            
            result = await mcp_client.call_tool(tool_name, arguments)
            
            span.set_attribute("tool.success", True)
            return result

Exemples Complets
=================

Exemple 1 : Récupérer Schéma
---------------------------

.. code-block:: python

    async def get_database_schema(database: str, table: str):
        """Récupérer le schéma d'une table."""
        try:
            schema = await mcp_client.call_tool(
                'get_schema',
                {
                    'database': database,
                    'table': table
                }
            )
            return schema
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return None

Exemple 2 : Exécuter Requête avec Gestion d'Erreur
---------------------------------------------------

.. code-block:: python

    async def execute_sql_safe(sql: str, database: str):
        """Exécuter une requête SQL de manière sécurisée."""
        # Valider la requête
        validate_sql_query(sql)
        
        # Exécuter avec timeout
        try:
            result = await asyncio.wait_for(
                mcp_client.call_tool(
                    'execute_sql',
                    {'sql': sql, 'database': database}
                ),
                timeout=30
            )
            return {'success': True, 'data': result}
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

Voir aussi
==========

- :doc:`architecture` pour l'architecture complète
- :doc:`api_reference` pour les endpoints
- `MCP Official Spec <https://modelcontextprotocol.io>`_
