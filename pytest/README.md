# Tests du Projet PROCOM

## Structure des tests

Le dossier `pytest/` contient tous les tests du projet:

- **test_db_available.py** - Test de disponibilité des serveurs/bases de données
- **test_BDD.py** - Tests de la base de données PostgreSQL (extraction de PDF)
- **test_query.py** - Tests des requêtes via la passerelle MCP (WebSocket)

## Configuration

### Environnement local

```bash
# Créer un fichier .env à la racine du projet
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=entreprise
POSTGRES_URL=postgresql://user:password@localhost:5432/entreprise
```

### Dépendances

```bash
pip install -r pytest/requirements.txt
```

## Exécution des tests

### Tous les tests
```bash
pytest pytest/
```

### Un fichier spécifique
```bash
pytest pytest/test_db_available.py -v
```

### Avec couverture de code
```bash
pytest pytest/ --cov=orchestrateur --cov-report=html
```

### Par marqueur
```bash
# Tests d'intégration uniquement
pytest pytest/ -m integration

# Tests unitaires
pytest pytest/ -m unit

# Tests de base de données
pytest pytest/ -m db
```

## GitHub Actions

### Workflow Build (build.yml)
- Construit les images Docker
- Valide la configuration Docker Compose
- S'exécute avant les tests

### Workflow Tests (test.yml)
- Utilise un service PostgreSQL fourni par GitHub Actions
- Installe les dépendances Python
- Exécute tous les tests pytest
- Génère les résultats de test

## Bonnes pratiques

1. **Marquer les tests**:
   ```python
   @pytest.mark.integration
   @pytest.mark.db
   def test_something():
       pass
   ```

2. **Utiliser les fixtures**:
   ```python
   def test_with_postgres(postgres_config):
       # postgres_config contient host, port, user, password, database
       pass
   ```

3. **Gérer l'environnement**:
   ```python
   def test_env_usage(test_env_vars):
       # test_env_vars contient les variables d'environnement
       pass
   ```

## Dépannage

### "Database connection refused"
- Vérifier que PostgreSQL est démarré et accessible
- Vérifier les variables d'environnement (PGHOST, PGUSER, etc.)
- Vérifier la configuration du .env

### Tests lents
- Marquer les tests lents avec `@pytest.mark.slow`
- Utiliser pytest-cov pour identifier les goulots d'étranglement

### Erreurs de WebSocket
- Vérifier que la passerelle MCP est accessible sur localhost:9000
- Vérifier la configuration du docker-compose.yml
