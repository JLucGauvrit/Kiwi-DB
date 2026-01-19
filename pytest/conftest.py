"""
Pytest configuration and fixtures for the RAG system tests.

Ce module contient la configuration Pytest et les fixtures communes
utilisées par tous les tests du système RAG fédéré.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
import os
import sys
from pathlib import Path

import pytest


# Ajouter le répertoire parent au chemin Python pour importer les modules du projet
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def postgres_config():
    """
    Fixture fournissant la configuration de connexion PostgreSQL.
    
    Lit les paramètres de connexion depuis les variables d'environnement
    avec des valeurs par défaut pour le développement local.
    
    @return: Dictionnaire de configuration PostgreSQL
    @rtype: dict
    @return_keys:
        - host (str): Hostname du serveur PostgreSQL
        - port (int): Port du serveur PostgreSQL
        - user (str): Utilisateur PostgreSQL
        - password (str): Mot de passe PostgreSQL
        - database (str): Nom de la base de données
    """
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "user"),
        "password": os.getenv("PGPASSWORD", "password"),
        "database": os.getenv("PGDATABASE", "entreprise"),
    }


@pytest.fixture(scope="session")
def postgres_url(postgres_config):
    """
    Fixture fournissant l'URL de connexion PostgreSQL complète.
    
    @param postgres_config: Configuration PostgreSQL (injecté par pytest)
    @return: URL de connexion PostgreSQL
    @rtype: str
    """
    config = postgres_config
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"


@pytest.fixture
def test_env_vars(monkeypatch):
    """
    Fixture définissant les variables d'environnement de test.
    
    Configure les variables d'environnement standard pour les tests
    avec des valeurs appropriées pour l'environnement de test.
    
    @param monkeypatch: Fixture pytest pour modifier les variables d'environnement
    @return: Dictionnaire des variables d'environnement définies
    @rtype: dict
    """
    test_vars = {
        "PGHOST": "localhost",
        "PGPORT": "5432",
        "PGUSER": "user",
        "PGPASSWORD": "password",
        "PGDATABASE": "entreprise",
    }
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    return test_vars


def pytest_configure(config):
    """
    Hook de configuration de Pytest.
    
    Enregistre les marqueurs personnalisés pour catégoriser les tests.
    
    @param config: Configuration Pytest
    """
    config.addinivalue_line("markers", "integration: integration test")
    config.addinivalue_line("markers", "unit: unit test")
    config.addinivalue_line("markers", "db: database test")
    config.addinivalue_line("markers", "slow: slow test")
