Déploiement en Production
========================

Prérequis
=========

- Docker & Docker Compose (version 1.25+)
- Git
- Un serveur avec au minimum 2 CPU et 4GB RAM
- PostgreSQL 15+ (optionnel si utilisation managed)
- Ollama (si déploiement local du LLM)

Architectures Supportées
========================

**Développement**
- Exécution locale avec Docker Compose
- Idéal pour tester et développer
- Temps de démarrage : ~30 secondes

**Production**
- Kubernetes (GKE, EKS, AKS)
- Cloud Managed Services (Cloud Run, App Engine)
- Serveur dédié avec Docker Swarm

Déploiement Local avec Docker
==============================

1. Préparer les Fichiers
------------------------

.. code-block:: bash

    git clone <repository-url>
    cd "BDD fédéré par agent"
    cp .env.example .env

2. Configurer les Variables
---------------------------

Éditer ``.env`` :

.. code-block:: bash

    # Orchestrateur
    OLLAMA_BASE_URL=http://ollama:11434
    MCP_GATEWAY_URL=ws://mcp-gateway:8000/ws
    LOG_LEVEL=INFO
    
    # PostgreSQL
    POSTGRES_USER=procom
    POSTGRES_PASSWORD=secure_password_here
    POSTGRES_DB=federated_db
    
    # Google Gemini (optionnel)
    GOOGLE_API_KEY=your_api_key_here
    
    # Environnement
    ENVIRONMENT=production
    DEBUG=false

3. Lancer l'Infrastructure
---------------------------

.. code-block:: bash

    # Construire et démarrer
    docker-compose -f docker-compose.yml up -d --build
    
    # Vérifier le statut
    docker-compose ps
    
    # Voir les logs
    docker-compose logs -f orchestrateur

4. Vérifier le Déploiement
--------------------------

.. code-block:: bash

    # Attendre que tous les services soient prêts (~1 minute)
    sleep 60
    
    # Tester la santé
    curl http://localhost:8000/health
    
    # Tester un endpoint
    curl -X POST http://localhost:8000/api/query \
      -H "Content-Type: application/json" \
      -d '{"query": "Test de déploiement"}'

Déploiement Kubernetes
======================

Prérequis
---------

- Kubectl configuré
- Cluster Kubernetes (GKE, EKS, AKS, local)
- Helm 3+ (optionnel)

Fichiers Kubernetes
-------------------

Créer ``k8s/namespace.yaml`` :

.. code-block:: yaml

    apiVersion: v1
    kind: Namespace
    metadata:
      name: procom
      labels:
        name: procom

Créer ``k8s/configmap.yaml`` :

.. code-block:: yaml

    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: app-config
      namespace: procom
    data:
      OLLAMA_BASE_URL: "http://ollama:11434"
      MCP_GATEWAY_URL: "ws://mcp-gateway:8000/ws"
      LOG_LEVEL: "INFO"
      ENVIRONMENT: "production"

Créer ``k8s/orchestrator-deployment.yaml`` :

.. code-block:: yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: orchestrator
      namespace: procom
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: orchestrator
      template:
        metadata:
          labels:
            app: orchestrator
        spec:
          containers:
          - name: orchestrator
            image: procom/orchestrator:latest
            ports:
            - containerPort: 8000
            envFrom:
            - configMapRef:
                name: app-config
            resources:
              requests:
                memory: "512Mi"
                cpu: "500m"
              limits:
                memory: "2Gi"
                cpu: "1000m"
            livenessProbe:
              httpGet:
                path: /health
                port: 8000
              initialDelaySeconds: 30
              periodSeconds: 10
            readinessProbe:
              httpGet:
                path: /health
                port: 8000
              initialDelaySeconds: 10
              periodSeconds: 5

Créer ``k8s/service.yaml`` :

.. code-block:: yaml

    apiVersion: v1
    kind: Service
    metadata:
      name: orchestrator
      namespace: procom
    spec:
      type: LoadBalancer
      ports:
      - port: 80
        targetPort: 8000
      selector:
        app: orchestrator

Déployer
--------

.. code-block:: bash

    # Créer le namespace et les ressources
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/orchestrator-deployment.yaml
    kubectl apply -f k8s/service.yaml
    
    # Vérifier le déploiement
    kubectl get pods -n procom
    kubectl get svc -n procom
    
    # Obtenir l'IP externe
    kubectl get svc orchestrator -n procom

Déploiement Cloud (Cloud Run)
=============================

Google Cloud Run
----------------

.. code-block:: bash

    # 1. Construire l'image
    docker build -t gcr.io/PROJECT_ID/orchestrator orchestrateur/
    
    # 2. Pousser vers Registry
    docker push gcr.io/PROJECT_ID/orchestrator
    
    # 3. Déployer sur Cloud Run
    gcloud run deploy orchestrator \
      --image gcr.io/PROJECT_ID/orchestrator \
      --platform managed \
      --region europe-west1 \
      --memory 512Mi \
      --timeout 300 \
      --set-env-vars="OLLAMA_BASE_URL=http://ollama:11434,MCP_GATEWAY_URL=ws://gateway:8000/ws"

Monitoring & Logs
=================

Prometheus
----------

Créer ``prometheus.yml`` :

.. code-block:: yaml

    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'orchestrator'
        static_configs:
          - targets: ['localhost:8000']

Déployer Prometheus :

.. code-block:: bash

    docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

Logs Centralisés (ELK Stack)
----------------------------

.. code-block:: bash

    # Déployer ELK avec Docker Compose
    docker-compose -f elk-compose.yml up -d
    
    # Accéder à Kibana
    # http://localhost:5601

Maintenance
===========

Backup Base de Données
----------------------

.. code-block:: bash

    # Sauvegarder PostgreSQL
    docker exec procom_postgres_1 pg_dump -U procom federated_db > backup.sql
    
    # Restaurer
    docker exec -i procom_postgres_1 psql -U procom federated_db < backup.sql

Mise à Jour
-----------

.. code-block:: bash

    # Récupérer les nouvelles sources
    git pull origin main
    
    # Reconstruire les images
    docker-compose build
    
    # Redémarrer les services
    docker-compose up -d
    
    # Vérifier la santé
    curl http://localhost:8000/health

Scaling Horizontal
------------------

.. code-block:: bash

    # Augmenter le nombre de réplicas Orchestrator
    docker-compose up -d --scale orchestrator=3

Dépannage Déploiement
====================

Service ne démarre pas
----------------------

.. code-block:: bash

    # Vérifier les logs
    docker-compose logs orchestrator
    
    # Inspecter l'image
    docker inspect procom:orchestrator
    
    # Vérifier les dépendances
    docker-compose ps

Port déjà utilisé
-----------------

.. code-block:: bash

    # Changer le port dans docker-compose.yml
    # Ou tuer le processus
    lsof -i :8000
    kill -9 <PID>

Connexion MCP échouée
---------------------

.. code-block:: bash

    # Vérifier que la passerelle MCP est active
    curl http://localhost:8000/servers
    
    # Vérifier la configuration
    cat config/servers.json
    
    # Redémarrer le service
    docker-compose restart mcp-gateway

Certificats SSL/TLS
===================

Générer un Certificat Auto-Signé
---------------------------------

.. code-block:: bash

    # Générer clé privée et certificat
    openssl req -x509 -newkey rsa:4096 -nodes \
      -out cert.pem -keyout key.pem -days 365
    
    # Placer dans certs/
    mkdir -p certs
    mv cert.pem certs/
    mv key.pem certs/

Configurer Nginx avec SSL
--------------------------

Dans ``nginx/nginx.conf`` :

.. code-block:: nginx

    server {
        listen 443 ssl;
        server_name your-domain.com;
        
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;
        
        location / {
            proxy_pass http://orchestrator:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

Optimisations Performance
=========================

Caching
-------

.. code-block:: python

    # Dans orchestrator/main.py
    from fastapi_cache2 import FastAPICache2
    from fastapi_cache2.backends.redis import RedisBackend
    
    redis_url = "redis://redis:6379"
    FastAPICache2.init(RedisBackend(redis_url), prefix="fastapi-cache")

Connection Pooling
------------------

Augmenter la taille du pool MCP dans ``mcp/mcp-gateway/main.py`` :

.. code-block:: python

    pool_size = 20  # Par défaut 10
    mcp_client = MCPClientPool(pool_size=pool_size)

Compression
-----------

Dans ``nginx/nginx.conf`` :

.. code-block:: nginx

    gzip on;
    gzip_types text/plain application/json text/css;
    gzip_min_length 1000;

Checklist de Déploiement
=======================

.. code-block:: text

    ✓ Variables d'environnement configurées
    ✓ Base de données initialisée
    ✓ MCP Gateway accessible
    ✓ Certificats SSL générés (production)
    ✓ Health checks en place
    ✓ Monitoring configuré
    ✓ Logs centralisés
    ✓ Backup automatisé
    ✓ Alertes définies
    ✓ Documentation mise à jour

Voir aussi
==========

- :doc:`guide_demarrage` pour installation locale
- :doc:`architecture` pour comprendre le système
- `Docker Documentation <https://docs.docker.com/>`_
- `Kubernetes Documentation <https://kubernetes.io/docs/>`_
