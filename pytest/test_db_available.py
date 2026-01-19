
import sys
import json
from pathlib import Path

JSON_PATH = Path("servers.json")  # chemin statique dans le repo

def main():
    if not JSON_PATH.exists():
        print(f"Fichier non trouvé: {JSON_PATH}")
        sys.exit(1)

    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON invalide dans {JSON_PATH}: {e}")
        sys.exit(1)

    servers = data.get("servers", [])
    if not isinstance(servers, list):
        print("Format de réponse inattendu: 'servers' doit être une liste")
        sys.exit(1)

    status_by_name = {}
    for s in servers:
        name = s.get("name")
        connected = s.get("connected")
        if name is None:
            continue
        status_by_name[name] = bool(connected)

    print("Liste des serveurs disponibles (statique):")
    for name, connected in status_by_name.items():
        etat = "CONNECTED" if connected else "DISCONNECTED"
        print(f"- {name}: {etat}")

    not_connected = [n for n, c in status_by_name.items() if not c]
    if not_connected:
        print(f"Serveurs non connectés: {', '.join(not_connected)}")
        sys.exit(1)

    print("Tous les serveurs sont connectés.")
    sys.exit(0)

if __name__ == "__main__":
    main()
