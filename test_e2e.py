#!/usr/bin/env python3
"""Test end-to-end pour Kiwi-DB Orchestrator"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoints"""
    print("=" * 50)
    print("TEST: Health Check")
    print("=" * 50)

    # Orchestrator health
    r = requests.get(f"{BASE_URL}/health")
    print(f"Orchestrator: {r.json()}")

    # MCP Gateway health
    r = requests.get("http://localhost:9000/health")
    print(f"MCP Gateway: {r.json()}")

    # MCP Servers
    r = requests.get("http://localhost:9000/servers")
    print(f"MCP Servers: {r.json()}")
    print()

def test_tools():
    """Test available tools"""
    print("=" * 50)
    print("TEST: Available Tools")
    print("=" * 50)

    r = requests.get(f"{BASE_URL}/tools")
    data = r.json()
    print(f"Total tools: {data['total']}")
    for tool in data['tools']:
        print(f"  - {tool['name']}")
    print()

def test_query(query: str):
    """Test a query against the orchestrator"""
    print("=" * 50)
    print(f"TEST: Query")
    print(f"Query: {query}")
    print("=" * 50)

    r = requests.post(
        f"{BASE_URL}/api/query",
        headers={"Content-Type": "application/json"},
        json={"query": query}
    )

    data = r.json()
    result = data.get("result", {})

    print(f"\nSuccess: {result.get('success')}")
    print(f"Intent: {result.get('intent', {}).get('intent_type')}")
    print(f"Requires DB: {result.get('intent', {}).get('requires_database')}")
    print(f"Iterations: {result.get('iterations')}")

    if result.get('tool_calls'):
        print(f"\nTools called:")
        for tc in result['tool_calls']:
            print(f"  - {tc.get('tool')}")

    print(f"\nAnswer:\n{result.get('answer', 'No answer')[:500]}...")
    print()

    return data

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("KIWI-DB END-TO-END TEST")
    print("=" * 50 + "\n")

    # Test 1: Health
    test_health()

    # Test 2: Tools
    test_tools()

    # Test 3: Queries
    queries = [
        "J'aimerai supprimer une base de donnée postgres"
    ]

    for q in queries:
        try:
            test_query(q)
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)
