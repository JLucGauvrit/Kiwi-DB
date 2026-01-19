"""
Intent classification agent for determining query requirements.

Ce module implémente l'agent de classification d'intention qui analyse
les requêtes utilisateur pour déterminer si elles nécessitent un accès
à la base de données ou s'il s'agit de questions de connaissances générales.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from src.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    """
    Agent de classification d'intention des requêtes utilisateur.
    
    Analyse les requêtes utilisateur et détermine :
    - Si la requête nécessite un accès à la base de données
    - Le type d'intention (recherche, agrégation, connaissances générales)
    - Les entités mentionnées dans la requête
    - Les bases de données pertinentes
    """
    
    def run(self, query: str) -> dict:
        """
        Classifier l'intention de la requête utilisateur.
        
        Envoie la requête au modèle de langage pour déterminer son intention
        et retourne un dictionnaire avec les informations sur l'intention.
        
        @param query: La requête utilisateur à analyser
        @type query: str
        @return: Dictionnaire contenant les résultats de la classification d'intention
        @rtype: dict
        @return_keys:
            - requires_database (bool): Indique si l'accès à la base de données est nécessaire
            - intent_type (str): Type d'intention ("search", "aggregate", "general_knowledge")
            - entities (list): Liste des entités mentionnées dans la requête
            - databases (list): Bases de données pertinentes (ex: ["postgres"])
            - reason (str): Explication brève de la classification
            - raw_response (str): Réponse brute du modèle de langage
        """
        prompt = f"""Analyze this user query and determine if it requires database access:

Query: "{query}"

You must determine:
1. Is this query asking for data that would be stored in a database? (users, products, orders, transactions, etc.)
2. Or is this a general knowledge question? (what is Google, explain concepts, etc.)

Return ONLY a JSON object with this exact structure:
{{
    "requires_database": true/false,
    "intent_type": "search" | "aggregate" | "general_knowledge",
    "entities": ["list", "of", "entities"],
    "databases": ["postgres"] or [],
    "reason": "brief explanation"
}}

Examples:
- "Show me all users" -> {{"requires_database": true, "intent_type": "search", "entities": ["users"], "databases": ["postgres"], "reason": "Asking for user data"}}
- "What is Google?" -> {{"requires_database": false, "intent_type": "general_knowledge", "entities": [], "databases": [], "reason": "General knowledge question"}}
- "How many orders today?" -> {{"requires_database": true, "intent_type": "aggregate", "entities": ["orders"], "databases": ["postgres"], "reason": "Asking for order statistics"}}
"""
        response = self.invoke(prompt)
        
        # Essayer de parser la réponse JSON
        import json
        try:
            # Extraire JSON de la réponse (peut avoir des blocs de code markdown)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            # Essayer de trouver un objet JSON dans le texte
            import re
            json_match = re.search(r'\{[^{}]*"requires_database"[^{}]*\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            
            intent_data = json.loads(json_str)
            
            # Assurer que le champ databases est défini correctement
            if intent_data.get("requires_database", False) and not intent_data.get("databases"):
                intent_data["databases"] = ["postgres"]
            
            # Ajouter la réponse brute
            intent_data["raw_response"] = response
            return intent_data
        except Exception as e:
            # Fallback : essayer d'extraire les informations clés du texte
            requires_db = "requires_database\": true" in response or "database" in response.lower()
            entities = []
            
            # Essayer d'extraire les entités de la réponse
            import re
            entities_match = re.search(r'"entities":\s*\[([^\]]+)\]', response)
            if entities_match:
                entities_str = entities_match.group(1)
                entities = [e.strip(' "\'') for e in entities_str.split(',')]
            
            return {
                "requires_database": requires_db,
                "intent_type": "search",
                "entities": entities,
                "databases": ["postgres"] if requires_db else [],
                "reason": "Parsed from text response",
                "raw_response": response
            }
