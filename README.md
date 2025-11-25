# 🤖 RAG Multi-Agent Orchestrator avec MCP

Plateforme d'orchestration multi-agents pour l'IA générative avec Retrieval-Augmented Generation (RAG), utilisant le Model Context Protocol (MCP) pour la communication inter-agents.

## 📋 Vue d'ensemble

### Architecture

```
Interface Utilisateur (Open Web UI)
           ↓
Orchestrateur (FastAPI)
         ↓
    MCP Client
    ↙   ↓    ↘
MCP Server A   MCP Server B   MCP Server C
    ↓              ↓              ↓
PostgreSQL + pgvector
```

### Composants

1.  **Interface Utilisateur (`open-webui`)**: Interface front-end Open Web UI pour interagir avec le système.
2.  **Orchestrateur (`orchestrator`)**: Service central en FastAPI. Il reçoit les requêtes de l'interface utilisateur, communique avec les serveurs de base de données via la passerelle MCP pour récupérer des informations, et synthétise les réponses.
3.  **Agent (`query-management`)**: Un exemple d'agent qui pourrait traiter des requêtes spécifiques. Dans cette architecture, il interagit avec l'orchestrateur.
4.  **Passerelle MCP (`mcp-gateway`)**: Route les requêtes de l'orchestrateur vers le serveur MCP approprié.
5.  **Serveur MCP (`mcp-postgres`)**: Traduit les requêtes MCP en requêtes spécifiques pour PostgreSQL.
6.  **Base de données (`postgres`)**: La base de données PostgreSQL où les données sont stockées. `postgres` est configuré avec pgvector pour la recherche vectorielle (RAG).


## 🚀 Installation et démarrage

### Prérequis

- Docker Desktop installé
- Docker Compose v2+
- Clés API:
  - Google Gemini API Key

### Configuration

1. **Cloner et configurer**

```bash
git clone https://github.com/JLucGauvrit/Kiwi-DB
```

2. **Préparer l'environnement**

Créer le fichier `.env` pour ajouter vos clés API. Aidez-vous de `.env.example`.


Contenu du fichier `.env`:
```bash
GEMINI_API_KEY=votre_clé_gemini_ici
```

### Démarrage

```bash
# Démarrer tous les services
docker compose up --build
```
```bash

# En mode détaché
docker compose up -d --build
```

### Premier lancement

Le système initialise automatiquement:
1. ✅ PostgreSQL avec extension pgvector
2. ✅ Tables et index pour le RAG
3. ✅ Documents de test pour chaque agent
4. ✅ Enregistrement des agents auprès de l'orchestrateur

## 🖥️ Utilisation

### Interface Web

Accédez à l'interface web :
```
http://localhost:3000
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


## 🤝 Contribution

Ce prototype a été créé pour démonstration. N'hésitez pas à l'adapter à vos besoins !

## 📞 Support

Pour toute question sur l'architecture MCP ou le RAG distribué, consultez:
- [Documentation MCP](https://modelcontextprotocol.io)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Gemini API](https://ai.google.dev)
