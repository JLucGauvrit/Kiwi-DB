"""Test de l'orchestrateur simplifié."""
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le chemin du module au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "orchestrateur"))

from src.orchestrator.orchestrator import FederatedRAGOrchestrator


async def test_orchestrator():
    """Test de l'orchestrateur simplifié."""

    # Configuration
    config = {
        "mcp_gateway_url": os.getenv("MCP_GATEWAY_URL", "ws://localhost:9000"),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
    }

    print("="*70)
    print("TEST DE L'ORCHESTRATEUR SIMPLIFIÉ")
    print("="*70)
    print("\nConfiguration:")
    print(f"  - Gateway MCP: {config['mcp_gateway_url']}")
    print(f"  - Ollama URL: {config['ollama_url']}")
    print(f"  - Modèle: {config['ollama_model']}")

    # Créer l'orchestrateur
    orchestrator = FederatedRAGOrchestrator(config)

    # Requête de test
    query = "Quelle est la version de PostgreSQL utilisée ?"

    print(f"\n{'='*70}")
    print(f"REQUÊTE: {query}")
    print('='*70)

    try:
        result = await orchestrator.run_async(query)

        if result.get("success"):
            print("\n✓ SUCCÈS\n")
            print(f"SQL généré:")
            print(f"  {result.get('sql', 'N/A')}\n")
            print(f"Résultats:")
            print(f"  {result.get('results', 'N/A')}\n")
            print(f"Réponse finale:")
            print(f"  {result.get('answer', 'N/A')}")
        else:
            print(f"\n✗ ÉCHEC")
            print(f"Erreur: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n✗ EXCEPTION")
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*70}")
    print("Test terminé")
    print('='*70)


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
