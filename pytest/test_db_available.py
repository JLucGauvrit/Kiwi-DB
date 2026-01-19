"""
Database availability check from static servers.json configuration.

Ce script lit un fichier servers.json statique et vérifie l'état
de connexion de tous les serveurs MCP configurés.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""

import sys
import json
from pathlib import Path

# Chemin du fichier de configuration statique
JSON_PATH = Path("servers.json")


def main():
    """
    Vérifier la disponibilité des serveurs depuis le fichier servers.json.
    
    Lit le fichier servers.json, vérifie que tous les serveurs sont
    connectés et affiche leur statut.
    
    @exit: 0 si tous les serveurs sont connectés, 1 sinon
    @raise FileNotFoundError: Si le fichier servers.json n'existe pas
    @raise json.JSONDecodeError: Si le fichier JSON est malformé
    """
    if not JSON_PATH.exists():
        print(f"Fichier non trouvé: {JSON_PATH}")
        sys.exit(1)

    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON invalide dans {JSON_PATH}: {e}")
        sys.exit(1)

    # Extraire la liste des serveurs
    servers = data.get("servers", [])
    if not isinstance(servers, list):
        print("Format de réponse inattendu: 'servers' doit être une liste")
        sys.exit(1)

    # Construire un dictionnaire nom -> statut de connexion
    status_by_name = {}
    for s in servers:
        name = s.get("name")
        connected = s.get("connected")
        if name is None:
            continue
        status_by_name[name] = bool(connected)

    # Afficher l'état de chaque serveur
    print("Liste des serveurs disponibles (statique):")
    for name, connected in status_by_name.items():
        etat = "CONNECTED" if connected else "DISCONNECTED"
        print(f"- {name}: {etat}")

    # Vérifier si tous les serveurs sont connectés
    not_connected = [n for n, c in status_by_name.items() if not c]
    if not_connected:
        print(f"Serveurs non connectés: {', '.join(not_connected)}")
        sys.exit(1)

    print("Tous les serveurs sont connectés.")
    sys.exit(0)

if __name__ == "__main__":
    main()
