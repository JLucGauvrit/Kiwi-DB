import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import google.generativeai as genai

# Charger les variables d'environnement du fichier .env
load_dotenv()

# --- Configuration de l'API Gemini ---
# La clé est lue depuis le fichier .env
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("La variable d'environnement GOOGLE_API_KEY n'est pas définie. Veuillez la créer dans un fichier .env.")
genai.configure(api_key=api_key)


# Création de l'application Flask
app = Flask(__name__)

# Initialisation du modèle Gemini (gemini-2.5-flash est rapide et efficace)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Erreur lors de l'initialisation du modèle Gemini : {e}")
    model = None

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Point de terminaison pour recevoir les requêtes.
    Attend un JSON avec une clé "prompt".
    Ex: {"prompt": "Quelle est la capitale de la France ?"}
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
        # Envoyer la requête à l'API Gemini
        response = model.generate_content(prompt)
        
        # Retourner la réponse textuelle de Gemini
        return jsonify({"response": response.text})

    except Exception as e:
        # Gérer les erreurs potentielles de l'API
        print(f"Une erreur est survenue lors de l'appel à l'API Gemini: {e}")
        return jsonify({"error": "Échec de la communication avec l'API Gemini."}), 500

if __name__ == '__main__':
    # Lancer le serveur sur le port 5000
    # Le serveur sera accessible depuis n'importe quelle adresse IP (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)
