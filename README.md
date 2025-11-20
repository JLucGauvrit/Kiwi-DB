# 🤖 RAG Multi-Agent Orchestrator avec MCP

Plateforme d'orchestration multi-agents pour l'IA générative avec Retrieval-Augmented Generation (RAG), utilisant le Model Context Protocol (MCP) pour la communication inter-agents.

## 📋 Vue d'ensemble

### Architecture

```
User Interface (Web UI)
         ↓
Orchestrateur (FastAPI + MCP Server)
         ↓
    MCP Server
    ↙   ↓    ↘
MCP Client A   MCP Client B   MCP Client C
    ↓              ↓              ↓
Agent RAG 1    Agent RAG 2    Agent RAG 3
(Gemini)      (Perplexity)   (Gemini)
General       Current        Analysis
    ↓              ↓              ↓
PostgreSQL + pgvector (Base vectorielle partagée)
```

### Composants

1. **Orchestrateur** (Port 8000)
   - Interface web de monitoring et debug
   - API FastAPI pour les requêtes utilisateur
   - Serveur MCP pour la distribution des tâches
   - Synthèse des réponses avec Gemini

2. **Agent RAG 1** - Gemini General Knowledge
   - Spécialité: Connaissances générales
   - LLM: Gemini 1.5 Flash
   - Base vectorielle dédiée

3. **Agent RAG 2** - Perplexity Current Events
   - Spécialité: Actualités et données actuelles
   - LLM: Perplexity Sonar (online)
   - Base vectorielle dédiée

4. **Agent RAG 3** - Gemini Analysis
   - Spécialité: Analyse de données
   - LLM: Gemini 1.5 Flash
   - Base vectorielle dédiée

5. **PostgreSQL + pgvector**
   - Stockage des documents
   - Recherche vectorielle avec pgvector
   - Logs et métriques

## 🚀 Installation et démarrage

### Prérequis

- Docker Desktop installé
- Docker Compose v2+
- Clés API:
  - Google Gemini API Key
  - Perplexity API Key (optionnel mais recommandé pour l'agent 2)

### Configuration

1. **Cloner et configurer**

```bash
# Créer la structure de dossiers
mkdir -p rag-orchestration/{orchestrator,agents/{agent_1,agent_2,agent_3},shared}
cd rag-orchestration

# Copier tous les fichiers dans leur emplacement respectif
```

2. **Structure des fichiers**

```
rag-orchestration/
├── docker-compose.yml
├── .env                          # À créer depuis .env.example
├── init_db.sql
├── orchestrator/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── static/
│       └── debug_ui.html
├── agents/
│   ├── agent_1/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── agent.py
│   ├── agent_2/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── agent.py
│   └── agent_3/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── agent.py
└── shared/
    ├── models.py
    └── database.py
```

3. **Configuration des clés API**

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos clés
nano .env
```

Contenu du fichier `.env`:
```bash
GEMINI_API_KEY=votre_clé_gemini_ici
PERPLEXITY_API_KEY=votre_clé_perplexity_ici
```

### Démarrage

```bash
# Démarrer tous les services
docker compose up --build

# En mode détaché
docker compose up -d --build

# Suivre les logs
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f orchestrator
docker compose logs -f agent-rag-1
```

### Premier lancement

Le système initialise automatiquement:
1. ✅ PostgreSQL avec extension pgvector
2. ✅ Tables et index pour le RAG
3. ✅ Documents de test pour chaque agent
4. ✅ Enregistrement des agents auprès de l'orchestrateur

## 🖥️ Utilisation

### Interface Web

Accédez à l'interface de monitoring:
```
http://localhost:8000
```

Fonctionnalités:
- 📝 Formulaire de requête
- 🎯 État des agents en temps réel
- 💬 Affichage des réponses agrégées
- 📊 Logs en temps réel via WebSocket

### API REST

**Envoyer une requête:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is data federation in distributed AI?"
  }'
```

**Lister les agents:**
```bash
curl http://localhost:8000/api/agents
```

**Health check:**
```bash
curl http://localhost:8000/api/health
```

### Exemples de requêtes

```bash
# Connaissances générales (Agent 1)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain machine learning basics"}'

# Actualités (Agent 2)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest developments in AI technology"}'

# Analyse (Agent 3)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze performance metrics of distributed systems"}'
```

## 📚 Ingestion de documents

### Via l'API d'un agent

```bash
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document content here...",
    "metadata": {
      "source": "manual",
      "topic": "AI",
      "date": "2025-11-07"
    }
  }'
```

### Via la base de données

```sql
-- Se connecter à PostgreSQL
docker exec -it rag-postgres psql -U postgres -d rag_db

-- Insérer un document
INSERT INTO documents (agent_id, content, metadata)
VALUES (
  'agent-1',
  'New knowledge to index',
  '{"source": "manual", "topic": "test"}'
);
```

## 🔧 Configuration avancée

### Ajuster le nombre d'agents

Modifier `docker-compose.yml` pour ajouter/retirer des agents:

```yaml
agent-rag-4:
  build:
    context: ./agents/agent_4
  environment:
    - AGENT_ID=agent-4
    - AGENT_NAME=Custom Agent
    - AGENT_SPECIALTY=technical
```

### Modifier les LLM utilisés

Dans `agents/agent_X/agent.py`, modifier:
- `gemini_model` pour changer le modèle Gemini
- `query_perplexity()` pour utiliser un autre modèle Perplexity

### Augmenter la capacité vectorielle

Dans `init_db.sql`:
```sql
-- Augmenter la dimension des embeddings
embedding vector(1536)  -- Modifier selon votre modèle

-- Ajuster les paramètres de l'index
CREATE INDEX ... WITH (lists = 100);  -- Augmenter pour plus de données
```

## 📊 Monitoring et Debug

### Logs centralisés

```bash
# Tous les services
docker compose logs -f

# Filtrer par service
docker compose logs -f orchestrator
docker compose logs -f postgres

# Dernières 100 lignes
docker compose logs --tail=100 -f
```

### Métriques dans PostgreSQL

```sql
-- Voir les logs des requêtes
SELECT * FROM mcp_logs ORDER BY created_at DESC LIMIT 10;

-- Stats des agents
SELECT 
  agent_id, 
  agent_name, 
  total_queries, 
  avg_response_time_ms,
  status
FROM agent_status;

-- Compter les documents par agent
SELECT agent_id, COUNT(*) 
FROM documents 
GROUP BY agent_id;
```

### WebSocket monitoring

L'interface web utilise WebSocket pour le monitoring temps réel:
- Connexion automatique à `ws://localhost:8000/ws/monitor`
- Événements: `agent_registered`, `query_received`, `query_completed`

## 🛠️ Développement

### Hot reload activé

Docker Compose watch est configuré pour le développement:
- Modification de `.py` → Rechargement automatique
- Modification de `requirements.txt` → Rebuild du container

```bash
# Mode développement avec watch
docker compose watch
```

### Tests

```bash
# Tester un agent directement
curl http://localhost:8080/health

# Tester l'orchestrateur
curl http://localhost:8000/api/health
```

## 🐛 Dépannage

### Les agents ne s'enregistrent pas

```bash
# Vérifier les logs de l'orchestrateur
docker compose logs orchestrator

# Vérifier la connectivité réseau
docker compose exec agent-rag-1 ping orchestrator

# Redémarrer un agent
docker compose restart agent-rag-1
```

### Erreurs PostgreSQL

```bash
# Vérifier l'état
docker compose exec postgres pg_isready -U postgres

# Se connecter manuellement
docker compose exec postgres psql -U postgres -d rag_db

# Réinitialiser complètement
docker compose down -v
docker compose up --build
```

### Problèmes de performance

```sql
-- Vérifier l'utilisation de l'index vectoriel
EXPLAIN ANALYZE 
SELECT * FROM documents 
WHERE agent_id = 'agent-1' 
ORDER BY embedding <=> '[1,2,3...]'::vector 
LIMIT 5;

-- Réindexer si nécessaire
REINDEX INDEX documents_embedding_idx;
```

## 📝 Notes importantes

### Limitations

- **Pas de persistance entre redémarrages** sans volumes Docker
- **Recherche vectorielle** limitée par la RAM pour de gros volumes
- **MCP simplifié** - implémentation HTTP au lieu du protocole complet

### Sécurité

⚠️ **Production:**
- Changer les mots de passe PostgreSQL
- Activer HTTPS
- Restreindre CORS
- Ajouter authentification API
- Chiffrer les clés API

### Performance

- **Recherche vectorielle** : O(n) sans index, O(log n) avec index IVFFlat
- **Concurrence** : FastAPI gère async nativement
- **Scaling** : Augmenter `lists` dans l'index pgvector pour plus de documents

## 🎯 Roadmap

- [ ] Implémentation complète du protocole MCP
- [ ] Support de modèles locaux (Ollama)
- [ ] Interface d'administration pour gérer les documents
- [ ] Métriques Prometheus/Grafana
- [ ] Support multi-utilisateurs avec auth
- [ ] Cache Redis pour les embeddings fréquents
- [ ] Support de fichiers PDF/DOCX pour l'ingestion

## 📄 Licence

MIT License - Libre d'utilisation pour vos projets

## 🤝 Contribution

Ce prototype a été créé pour démonstration. N'hésitez pas à l'adapter à vos besoins !

## 📞 Support

Pour toute question sur l'architecture MCP ou le RAG distribué, consultez:
- [Documentation MCP](https://modelcontextprotocol.io)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Gemini API](https://ai.google.dev)
- [Perplexity API](https://docs.perplexity.ai)
