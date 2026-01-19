FAQ (Questions Fréquemment Posées)
==================================

Installation & Configuration
============================

Q: Comment installer le projet?
-------------------------------

**R:** Voir :doc:`guide_demarrage` pour les instructions complètes.

Résumé rapide:

.. code-block:: bash

    git clone <url>
    cd "BDD fédéré par agent"
    docker-compose up --build
    curl http://localhost:8000/health

Q: Quels sont les prérequis système?
------------------------------------

**R:** 

- **OS** : Windows, macOS, Linux
- **RAM** : 4GB minimum (8GB recommandé)
- **CPU** : 2 cores minimum (4 cores recommandé)
- **Disque** : 10GB d'espace libre
- **Logiciels** : Docker 20.10+, Docker Compose 1.29+

Q: Comment configurer les variables d'environnement?
---------------------------------------------------

**R:** Créer un fichier `.env` à la racine:

.. code-block:: bash

    # Copier le template
    cp .env.example .env
    
    # Éditer avec votre éditeur
    nano .env

Q: Peut-on utiliser le projet sans Docker?
-------------------------------------------

**R:** Oui, mais c'est plus complexe. Il faut :

1. Installer Python 3.9+
2. Installer PostgreSQL 15+
3. Installer Ollama
4. Installer les dépendances pip
5. Configurer les variables d'environnement
6. Démarrer chaque service manuellement

**Recommandation** : Utilisez Docker pour simplifier le déploiement.

Déploiement
===========

Q: Comment déployer en production?
----------------------------------

**R:** Voir :doc:`deployment` pour des instructions détaillées.

Options disponibles:

1. **Docker Compose** : Pour serveur unique
2. **Kubernetes** : Pour haute disponibilité
3. **Cloud Run** : Pour serverless
4. **Heroku** : Pour simple déploiement

Q: Quel serveur pour la production?
-----------------------------------

**R:** Recommandations:

- **Petite charge** (< 100 req/min) : 1 CPU, 2GB RAM
- **Charge moyenne** (100-500 req/min) : 2 CPU, 4GB RAM
- **Haute charge** (> 500 req/min) : 4+ CPU, 8GB+ RAM

Utiliser un load balancer si plusieurs instances.

Q: Comment configurer les logs en production?
---------------------------------------------

**R:** Dans `docker-compose.yml`:

.. code-block:: yaml

    services:
      orchestrator:
        environment:
          LOG_LEVEL: INFO
          LOG_FILE: /var/log/orchestrator.log

Utiliser ELK Stack ou Datadog pour centraliser.

API & Requêtes
==============

Q: Comment appeler l'API?
------------------------

**R:** Voir :doc:`api_reference` pour documentation complète.

Exemple simple:

.. code-block:: bash

    curl -X POST "http://localhost:8000/api/query" \
      -H "Content-Type: application/json" \
      -d '{"query": "Quelle est la capitale de la France?"}'

Q: Quels types de requêtes sont supportées?
-------------------------------------------

**R:**

1. **Connaissances générales** : "Quelle est la capitale de la France?"
2. **Requêtes SQL** : "Liste les employés du département IT"
3. **Analyses** : "Analysez les ventes de 2025"
4. **Recherche** : "Trouve tous les clients à Paris"

Le système détecte automatiquement le type.

Q: Quel est le délai d'une requête?
----------------------------------

**R:** Typiquement 1-3 secondes:

- 100-200ms : Analyse intention
- 100-200ms : Récupération schémas
- 100-200ms : Génération SQL
- 50-100ms : Validation
- 100-1000ms : Exécution (dépend de la BD)
- 50-100ms : Composition réponse

Q: Y a-t-il une limite de taille de requête?
--------------------------------------------

**R:**

- **Requête utilisateur** : 500 caractères par défaut
- **Requête SQL générée** : 10000 caractères max
- **Résultats retournés** : 10 lignes par défaut (configurable)

Configurable via variables d'environnement.

Q: Comment ajouter l'authentification?
-------------------------------------

**R:** Le projet supporte (à implémenter):

.. code-block:: python

    # Dans orchestrateur/main.py
    from fastapi.security import HTTPBearer
    
    security = HTTPBearer()
    
    @app.post("/api/query")
    async def process_query(
        request: QueryRequest,
        credentials: HTTPAuthCredentials = Depends(security)
    ):
        # Valider le token JWT
        user = validate_token(credentials.credentials)
        ...

Agents & Modèles
================

Q: Comment personnaliser les prompts des agents?
-----------------------------------------------

**R:** Éditer les fichiers agents:

.. code-block:: python

    # orchestrateur/src/agents/intent_agent.py
    INTENT_PROMPT = """
    Votre prompt personnalisé ici...
    """

Q: Peut-on changer le modèle LLM?
---------------------------------

**R:** Oui! Dans `orchestrateur/src/agents/base_agent.py`:

.. code-block:: python

    self.llm = ChatOllama(
        model="mistral",  # Changer ici
        base_url="http://ollama:11434"
    )

Modèles Ollama disponibles:

.. code-block:: bash

    # Lancer Ollama
    ollama pull mistral
    ollama pull neural-chat
    ollama pull dolphin2.2-mvc

Q: Peut-on utiliser un modèle externe?
--------------------------------------

**R:** Oui, par exemple Google Gemini:

.. code-block:: python

    from langchain_google_genai import ChatGoogleGenerativeAI
    
    self.llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        api_key="YOUR_API_KEY"
    )

Q: Comment améliorer la qualité des réponses?
---------------------------------------------

**R:**

1. **Améliorer les prompts** : Rendre plus spécifiques
2. **Fine-tuning** : Entraîner sur données propres
3. **Few-shot learning** : Ajouter des exemples
4. **Retrieval amélioration** : Meilleurs schémas de BD
5. **Validation stricte** : Plus de règles

Bases de Données
================

Q: Quelles bases de données sont supportées?
--------------------------------------------

**R:** Le système supporte:

- **PostgreSQL** : Natif (avec pgvector)
- **MySQL** : Via adaptateur MCP
- **MongoDB** : Via adaptateur MCP
- **Autres** : Créer un serveur MCP personnalisé

Voir :doc:`mcp_protocol` pour détails.

Q: Comment ajouter une nouvelle base de données?
-----------------------------------------------

**R:**

1. Créer un serveur MCP pour la BD
2. Configurer dans `config/servers.json`
3. Redémarrer le gateway
4. Les agents peuvent l'utiliser automatiquement

Q: Comment optimiser les requêtes SQL générées?
----------------------------------------------

**R:**

1. **Améliorer le SQLAgent** : Meilleur prompt
2. **Créer des indexes** : Sur colonnes fréquentes
3. **Valider les requêtes** : Plus strict
4. **Utiliser des vues** : Pour requêtes complexes
5. **Limiter les résultats** : Pagination

Q: Comment gérer les gros volumes de données?
--------------------------------------------

**R:**

1. **Pagination** : Limiter résultats par page
2. **Aggregation** : Grouper plutôt que retourner tout
3. **Indexes** : Pour recherches rapides
4. **Caching** : Mettre en cache les schémas
5. **Parallelisation** : Exécution fédérée en parallèle

Performance & Scalabilité
=========================

Q: Comment améliorer les performances?
-------------------------------------

**R:**

1. **Caching** : Redis pour schémas/résultats
2. **Connection pooling** : Réutiliser connexions
3. **Compression** : Gzip pour réponses
4. **Parallelisation** : Requests concurrentes
5. **Load balancing** : Distribuer charge
6. **Hardware** : Plus CPU/RAM

Q: Peut-on scaler horizontalement?
---------------------------------

**R:** Oui! Le système est stateless:

.. code-block:: bash

    # Scale orchestrator à 3 instances
    docker-compose up -d --scale orchestrator=3
    
    # Avec Kubernetes
    kubectl scale deployment orchestrator --replicas=3

Q: Quelle est la capacité maximale?
----------------------------------

**R:** Dépend de:

- **Orchestrateur** : ~100-500 req/s par instance
- **MCP Gateway** : ~1000 req/s (connection pooling)
- **Base de données** : Dépend du hardware
- **Réseau** : Latence + bande passante

Testez avec votre charge réelle.

Dépannage
=========

Q: "ModuleNotFoundError: No module named 'src'"
----------------------------------------------

**R:** Cause: PYTHONPATH non configuré

Solution:

.. code-block:: bash

    # Ajouter au PYTHONPATH
    export PYTHONPATH="./orchestrateur:$PYTHONPATH"
    python -m orchestrateur.main

Q: "Connection refused" au lancement
-----------------------------------

**R:** Les services ne sont pas prêts

Solution:

.. code-block:: bash

    # Attendre 30 secondes
    sleep 30
    
    # Vérifier statut
    docker-compose ps
    
    # Voir les logs
    docker-compose logs orchestrator

Q: MCP Gateway ne se connecte pas
---------------------------------

**R:** Cause: Mauvaise configuration MCP

Vérifier:

.. code-block:: bash

    # Vérifier config
    cat config/servers.json
    
    # Tester connexion
    curl http://localhost:8000/servers
    
    # Voir logs du gateway
    docker-compose logs mcp-gateway

Q: Requête qui timeout
---------------------

**R:** Cause: Requête SQL trop lente

Solutions:

1. **Augmenter timeout** : Dans config
2. **Optimiser SQL** : Ajouter indexes
3. **Limiter résultats** : Pagination
4. **Augmenter hardware** : Plus CPU/RAM
5. **Cacher résultats** : Redis

Q: Erreur de mémoire (OutOfMemory)
---------------------------------

**R:** Cause: Trop de données

Solutions:

1. **Paginer résultats** : Limiter max_results
2. **Augmenter RAM** : Allouer plus à Docker
3. **Optimiser requêtes** : Sélectionner colonnes
4. **Nettoyer cache** : Redémarrer services
5. **Monitorer** : Vérifier utilisation mémoire

Développement
=============

Q: Comment contribuer au projet?
-------------------------------

**R:**

1. Fork le repository
2. Créer une branche (`git checkout -b feature/xyz`)
3. Faire les changements
4. Écrire les tests
5. Push et créer Pull Request

Q: Comment exécuter les tests?
-----------------------------

**R:**

.. code-block:: bash

    cd pytest
    pip install -r requirements.txt
    pytest -v

Pour les tests spécifiques:

.. code-block:: bash

    pytest test_query.py -v
    pytest test_BDD.py::test_connection -v

Q: Comment déboguer le système?
------------------------------

**R:**

1. **Logs** : `docker-compose logs -f [service]`
2. **Breakpoints** : Debug mode dans IDE
3. **Curl** : Tester endpoints manuellement
4. **Monitoring** : Prometheus + Grafana
5. **Tracing** : Jaeger pour requêtes distribuées

Q: Où sont les fichiers de log?
------------------------------

**R:**

- **Docker** : `docker-compose logs [service]`
- **Fichiers** : `/var/log/orchestrator.log` (si configuré)
- **Centralisés** : Kibana si ELK déployé
- **Cloud** : CloudWatch/Stackdriver si cloud

Documentation
=============

Q: Comment générer la documentation?
-----------------------------------

**R:**

.. code-block:: bash

    cd docs
    make html
    
    # Ou manuellement
    sphinx-build -b html . _build/html
    
    # Servir localement
    python -m http.server 8000 -d _build/html

Q: Comment mettre à jour la documentation?
------------------------------------------

**R:**

1. Éditer les fichiers `.rst` dans `docs/`
2. Vérifier: `sphinx-build -W --keep-going -b html . _build/html`
3. Pousser vers main: Documentation déployée automatiquement

Q: Où trouver la documentation complète?
---------------------------------------

**R:**

- **Locale** : http://localhost:8000 (après `make serve`)
- **GitHub Pages** : https://github.com/.../docs
- **Code source** : PyDoc dans les fichiers Python

Support & Ressources
====================

Q: Comment obtenir de l'aide?
----------------------------

**R:**

1. **Documentation** : Lire les guides
2. **Issues GitHub** : Signaler bugs
3. **Discussions** : Questions/partage
4. **Email** : contact@procom.fr

Q: Où trouver des exemples?
---------------------------

**R:**

- **Code source** : Voir `orchestrateur/main.py`
- **Tests** : Voir `pytest/test_*.py`
- **Documentation** : Tous les fichiers RST
- **GitHub** : Repository public

Q: Y a-t-il une roadmap?
-----------------------

**R:** Prévu pour les prochaines versions:

- ✓ Version 1.0 : Release stable
- ⏳ Version 1.1 : Authentification JWT
- ⏳ Version 1.2 : Cache Redis
- ⏳ Version 2.0 : Interface web graphique
- ⏳ Version 2.1 : Support multi-langues

Voir les issues GitHub pour détails.

Voir aussi
==========

- :doc:`guide_demarrage` pour installation
- :doc:`architecture` pour comprendre le système
- :doc:`deployment` pour la mise en production
- :doc:`api_reference` pour les endpoints
