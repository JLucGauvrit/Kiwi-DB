#!/usr/bin/env python3
"""Test end-to-end de l'orchestrateur avec MCP"""
import asyncio
import sys
from src.orchestrator.orchestrator import FederatedRAGOrchestrator


async def main():
    """Test end-to-end de l'orchestrateur avec MCP"""
    print("╔════════════════════════════════════════════════════╗")
    print("║   Test End-to-End: Orchestrateur → MCP → DB       ║")
    print("╚════════════════════════════════════════════════════╝\n")

    # Configuration
    config = {
        "mcp_gateway_url": "localhost:9000",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.2"
    }

    try:
        # Initialisation de l'orchestrateur
        print("[1/4] Initialisation de l'orchestrateur...")
        orchestrator = FederatedRAGOrchestrator(config)
        print("✓ Orchestrateur initialisé\n")

        # Requête à exécuter
        query = "Liste tous les utilisateurs"
        print(f"[2/4] Requête utilisateur: '{query}'")
        print()

        # Exécution du flow complet
        print("[3/4] Exécution du flow complet:")
        print("      Intent → Retrieval → SQL → Validation → Execution (MCP) → Composition")
        print()

        result = await orchestrator.run_async(query)

        # Affichage des résultats
        print("[4/4] Résultats:\n")

        print("─── Intent ───")
        print(f"  {result.get('intent', {})}\n")

        print("─── Schémas récupérés ───")
        schemas = result.get('schemas', [])
        print(f"  {len(schemas)} schéma(s) trouvé(s)")
        for schema in schemas:
            print(f"    • DB: {schema.get('database')}, Tables: {schema.get('tables', [])}")
        print()

        print("─── Requêtes SQL générées ───")
        sql_queries = result.get('sql_queries', {})
        for db, query_info in sql_queries.items():
            print(f"  • {db}: {query_info.get('query')}")
        print()

        print("─── Validation ───")
        validation = result.get('validation_results', {})
        valid = validation.get('valid', False)
        print(f"  Statut: {'✓ VALIDE' if valid else '✗ INVALIDE'}")
        if not valid:
            print(f"  Issues: {validation.get('issues', [])}")
        print()

        print("─── Exécution via MCP ───")
        execution_results = result.get('execution_results', {})
        if execution_results:
            for db, exec_result in execution_results.items():
                if exec_result.get("success"):
                    print(f"  ✓ {db}: {exec_result.get('rows')} ligne(s) retournée(s)")
                    data = exec_result.get('data', [])
                    if data:
                        print(f"    Aperçu: {data[:2]}")
                else:
                    print(f"  ✗ {db}: ERREUR - {exec_result.get('error')}")
        else:
            print("  Aucune exécution (validation échouée)")
        print()

        print("─── Réponse finale ───")
        final_output = result.get('final_output', '')
        if final_output:
            print(f"  {final_output[:300]}...")
        else:
            print("  Pas de réponse finale générée")
        print()

        if result.get('errors'):
            print("─── Erreurs ───")
            for error in result.get('errors', []):
                print(f"  ✗ {error}")
            print()

        # Verdict
        print("╔════════════════════════════════════════════════════╗")
        if execution_results and all(r.get("success") for r in execution_results.values()):
            print("║              ✓ TEST RÉUSSI                        ║")
        else:
            print("║              ✗ TEST ÉCHOUÉ                        ║")
        print("╚════════════════════════════════════════════════════╝")

        return 0

    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
