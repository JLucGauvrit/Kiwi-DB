"""Pytest configuration and fixtures"""
import os
import sys
from pathlib import Path

import pytest


# Add parent directory to path so we can import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def postgres_config():
    """PostgreSQL connection configuration"""
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "user"),
        "password": os.getenv("PGPASSWORD", "password"),
        "database": os.getenv("PGDATABASE", "entreprise"),
    }


@pytest.fixture(scope="session")
def postgres_url(postgres_config):
    """PostgreSQL connection URL"""
    config = postgres_config
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"


@pytest.fixture
def test_env_vars(monkeypatch):
    """Set test environment variables"""
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
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: integration test")
    config.addinivalue_line("markers", "unit: unit test")
    config.addinivalue_line("markers", "db: database test")
    config.addinivalue_line("markers", "slow: slow test")
