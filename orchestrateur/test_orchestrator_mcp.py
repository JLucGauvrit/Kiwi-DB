#!/usr/bin/env python3
"""Test end-to-end de l'orchestrateur avec MCP"""
import asyncio
import sys
from src.orchestrator.orchestrator import FederatedRAGOrchestrator


async def main():
    """Test end-to-end de l'orchestrateur avec MCP"""
    print("=" * 60)
    print("   Test End-to-End: Orchestrateur -> MCP -> DB")
    print("=" * 60 + "\n")

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
        print("[OK] Orchestrateur initialise\n")

        # Requete a executer
        query = "Liste tous les utilisateurs"
        print(f"[2/4] Requete utilisateur: '{query}'")
        print()

        # Execution du flow complet
        print("[3/4] Execution du flow complet:")
        print("      Intent -> Retrieval -> SQL -> Validation -> Execution (MCP) -> Composition")
        print()

        result = await orchestrator.run_async(query)

        # Affichage des resultats
        print("[4/4] Resultats:\n")

        print("--- Intent ---")
        print(f"  {result.get('intent', {})}\n")

        print("--- Schemas recuperes ---")
        schemas = result.get('schemas', [])
        print(f"  {len(schemas)} schema(s) trouve(s)")
        for schema in schemas:
            print(f"    - DB: {schema.get('database')}, Tables: {schema.get('tables', [])}")
        print()

        print("--- Requetes SQL generees ---")
        sql_queries = result.get('sql_queries', {})
        for db, query_info in sql_queries.items():
            print(f"  - {db}: {query_info.get('query')}")
        print()

        print("--- Validation ---")
        validation = result.get('validation_results', {})
        valid = validation.get('valid', False)
        print(f"  Statut: {'[OK] VALIDE' if valid else '[X] INVALIDE'}")
        if not valid:
            print(f"  Issues: {validation.get('issues', [])}")
        print()

        print("--- Execution via MCP ---")
        execution_results = result.get('execution_results', {})
        if execution_results:
            for db, exec_result in execution_results.items():
                if exec_result.get("success"):
                    print(f"  [OK] {db}: {exec_result.get('rows')} ligne(s) retournee(s)")
                    data = exec_result.get('data', [])
                    if data:
                        print(f"    Apercu: {data[:2]}")
                else:
                    print(f"  [X] {db}: ERREUR - {exec_result.get('error')}")
        else:
            print("  Aucune execution (validation echouee)")
        print()

        print("--- Reponse finale ---")
        final_output = result.get('final_output', '')
        if final_output:
            print(f"  {final_output[:300]}...")
        else:
            print("  Pas de reponse finale generee")
        print()

        if result.get('errors'):
            print("--- Erreurs ---")
            for error in result.get('errors', []):
                print(f"  [X] {error}")
            print()

        # Verdict
        print("=" * 60)
        if execution_results and all(r.get("success") for r in execution_results.values()):
            print("              [OK] TEST REUSSI")
        else:
            print("              [FAIL] TEST ECHOUE")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
