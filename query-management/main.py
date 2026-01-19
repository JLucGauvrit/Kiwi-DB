"""
Query Management Service - Handles query processing with Google Gemini API.

Ce module implémente un service de gestion des requêtes qui traite
les requêtes utilisateur via l'API Google Gemini. Il sert comme
agent spécialisé dans le système RAG fédéré.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import google.generativeai as genai

# Charger les variables d'environnement du fichier .env
load_dotenv()

# --- Configuration de l'API Gemini ---
# La clé API est lue depuis le fichier .env
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("La variable d'environnement GOOGLE_API_KEY n'est pas définie. Veuillez la créer dans un fichier .env.")
genai.configure(api_key=api_key)


# Création de l'application Flask
app = Flask(__name__)

# Initialisation du modèle Gemini
# gemini-2.5-flash offre un bon équilibre entre rapidité et qualité
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Erreur lors de l'initialisation du modèle Gemini : {e}")
    model = None

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Point de terminaison principal pour traiter les requêtes.
    
    Accepte des requêtes JSON contenant un prompt utilisateur,
    les envoie au modèle Gemini et retourne la réponse générée.
    
    Format de requête attendu :
    ```json
    {
        "prompt": "Votre question ici"
    }
    ```
    
    @return: Réponse JSON contenant la réponse générée ou un message d'erreur
    @rtype: dict with 'response' or 'error' key
    @status_code: 200 si succès, 400 si requête invalide, 500 si erreur serveur, 503 si service indisponible
    """
    if not model:
        return jsonify({"error": "Le modèle Gemini n'a pas pu être initialisé."}), 503

    # Vérifier que la requête est au format JSON
    if not request.is_json:
        return jsonify({"error": "Requête invalide, JSON manquant."}), 400

    data = request.get_json()
    prompt = data.get('prompt')

    # Vérifier la présence du prompt
    if not prompt:
        return jsonify({"error": "La clé 'prompt' est manquante dans le corps de la requête."}), 400

    try:
        # Envoyer la requête à l'API Gemini et obtenir la réponse
        response = model.generate_content(prompt)
        
        # Retourner la réponse textuelle de Gemini au format JSON
        return jsonify({"response": response.text})

    except Exception as e:
        # Gérer les erreurs potentielles de l'API Gemini
        print(f"Une erreur est survenue lors de l'appel à l'API Gemini: {e}")
        return jsonify({"error": "Échec de la communication avec l'API Gemini."}), 500

if __name__ == '__main__':
    # Lancer le serveur Flask sur le port 220
    # Le serveur sera accessible depuis n'importe quelle adresse IP (0.0.0.0)
    # debug=True permet le rechargement automatique lors des modifications
    app.run(host='0.0.0.0', port=220, debug=True)
