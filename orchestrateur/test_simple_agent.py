"""Script de test pour l'agent simplifié."""
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le chemin du module au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.simple_agent import SimpleAgent


async def test_simple_agent():
    """Test de l'agent simplifié."""

    # Configuration
    config = {
        "mcp_gateway_url": os.getenv("MCP_GATEWAY_URL", "ws://localhost:9000"),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
    }

    print("Configuration:")
    print(f"  - Gateway MCP: {config['mcp_gateway_url']}")
    print(f"  - Ollama URL: {config['ollama_url']}")
    print(f"  - Modèle Ollama: {config['ollama_model']}")
    print()

    # Créer l'agent
    agent = SimpleAgent(config)

    # Requêtes de test
    test_queries = [
        "Quelle est la version de PostgreSQL ?",
        "Liste toutes les tables de la base de données",
        "Combien d'enregistrements y a-t-il au total ?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print('='*60)

        try:
            result = await agent.process_query(query)

            if result.get("success"):
                print(f"\n✓ Requête réussie")
                print(f"\nSQL généré:\n{result.get('sql', 'N/A')}")
                print(f"\nRésultats:")
                print(result.get('results', 'N/A'))
                print(f"\nRéponse:\n{result.get('answer', 'N/A')}")
            else:
                print(f"\n✗ Erreur: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"\n✗ Exception: {str(e)}")

    print(f"\n{'='*60}")
    print("Tests terminés")
    print('='*60)


if __name__ == "__main__":
    asyncio.run(test_simple_agent())
