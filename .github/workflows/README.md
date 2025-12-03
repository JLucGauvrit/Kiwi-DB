# GitHub Actions - Kiwi-DB

Ce dossier contient les workflows GitHub Actions pour l'intégration continue (CI) et le déploiement continu (CD) du projet Kiwi-DB.

## 📋 Workflows Disponibles

### 1. CI - Tests et Validation (`ci.yml`)

**Déclencheurs:**
- Push sur `main` et `develop`
- Pull requests vers `main` et `develop`

**Jobs:**
- **Lint et Format**: Vérifie le code Python avec Ruff, Black et isort
- **Build Services**: Compile les images Docker de tous les services
- **Integration Tests**: Lance les services avec Docker Compose et vérifie leur santé
- **Security Scan**: Scan de sécurité avec Trivy

### 2. CD - Build et Push Docker Images (`docker-publish.yml`)

**Déclencheurs:**
- Push sur `main`
- Tags de version (`v*.*.*`)
- Manuel via `workflow_dispatch`

**Fonctionnalités:**
- Construit et pousse les images Docker vers GitHub Container Registry (ghcr.io)
- Crée des tags automatiques (latest, version, SHA)
- Utilise le cache pour optimiser les builds

### 3. Dependency Check (`dependency-check.yml`)

**Déclencheurs:**
- Tous les lundis à 9h (cron)
- Modifications des fichiers `requirements.txt`
- Manuel

**Fonctionnalités:**
- Vérifie les vulnérabilités de sécurité avec pip-audit
- Liste les dépendances obsolètes

### 4. Docker Compose Validation (`docker-compose-validation.yml`)

**Déclencheurs:**
- Modifications du fichier `docker-compose.yml` ou des Dockerfiles
- Push sur `main` et `develop`

**Fonctionnalités:**
- Valide la syntaxe du docker-compose.yml
- Vérifie la présence de bonnes pratiques (health checks, restart policies)

## 🚀 Installation

1. **Créer le dossier `.github/workflows`** dans votre repository:
```bash
mkdir -p .github/workflows
```

2. **Copier les fichiers** de workflow dans ce dossier

3. **Configurer les secrets** (si nécessaire):
   - `GITHUB_TOKEN` est automatiquement disponible
   - Pour publier sur ghcr.io, assurez-vous que les permissions packages sont activées

## ⚙️ Configuration

### Activer GitHub Container Registry

Pour publier vos images Docker:

1. Allez dans **Settings** → **Actions** → **General**
2. Sous "Workflow permissions", sélectionnez **Read and write permissions**
3. Cochez **Allow GitHub Actions to create and approve pull requests**

### Variables d'environnement pour les tests

Le workflow CI crée automatiquement un fichier `.env` avec des valeurs de test. Pour utiliser vos propres valeurs, ajoutez des secrets GitHub:

- `GOOGLE_API_KEY`: Votre clé API Google Gemini (optionnel pour les tests)

## 📊 Badges de Statut

Ajoutez ces badges dans votre README.md principal:

```markdown
![CI](https://github.com/JLucGauvrit/Kiwi-DB/workflows/CI%20-%20Tests%20et%20Validation/badge.svg)
![Docker](https://github.com/JLucGauvrit/Kiwi-DB/workflows/CD%20-%20Build%20et%20Push%20Docker%20Images/badge.svg)
```

## 🔧 Personnalisation

### Modifier les services testés

Dans `ci.yml`, section `build-services`, ajustez la liste des services:

```yaml
strategy:
  matrix:
    service: [orchestrator, mcp-gateway, mcp-postgres, query-management]
```

### Ajouter des tests

Pour ajouter des tests unitaires, créez un nouveau job dans `ci.yml`:

```yaml
unit-tests:
  name: Tests Unitaires
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: pip install pytest
    - run: pytest tests/
```

### Changer la fréquence du scan de dépendances

Dans `dependency-check.yml`, modifiez le cron:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Tous les lundis à 9h
```

## 🐛 Dépannage

### Les builds échouent

1. Vérifiez les logs dans l'onglet **Actions** de GitHub
2. Assurez-vous que tous les Dockerfiles sont présents
3. Vérifiez que `docker-compose.yml` est valide localement

### Les images ne se publient pas

1. Vérifiez les permissions dans **Settings** → **Actions**
2. Assurez-vous d'être sur la branche `main` ou d'avoir créé un tag
3. Vérifiez que `GITHUB_TOKEN` a les permissions nécessaires

### Les tests d'intégration échouent

1. Augmentez le temps d'attente dans le workflow (actuellement 30s)
2. Vérifiez que les services ont des health checks
3. Testez localement avec `docker compose up`

## 📝 Bonnes Pratiques

- **Branching**: Travaillez sur des branches feature et créez des PR vers `develop`
- **Tags**: Utilisez des tags sémantiques (`v1.0.0`) pour les releases
- **Tests**: Ajoutez des tests unitaires avant de pousser
- **Documentation**: Mettez à jour ce README quand vous modifiez les workflows

## 🤝 Contribution

Pour ajouter ou modifier un workflow:

1. Créez une branche feature
2. Testez le workflow localement avec [act](https://github.com/nektos/act) si possible
3. Créez une PR avec une description claire des changements
4. Attendez la validation de l'équipe

## 📚 Ressources

- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
