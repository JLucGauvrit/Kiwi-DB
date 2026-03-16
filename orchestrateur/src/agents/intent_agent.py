"""Intent classification agent."""
from src.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    def run(self, query: str) -> dict:
        """Classify user intent from query."""
        prompt = f"""Analyze this user query and determine if it requires database access.

Available databases:
- PostgreSQL: contains data about cars (voitures), brands (marques), models (modeles), sales (ventes)
- MongoDB: contains data about animals (animaux) with fields like species, habitat, weight, conservation status
- MySQL: contains data about a library (bibliotheque) with tables auteurs (authors), livres (books), emprunts (loans/borrows)

Query: "{query}"

You must determine:
1. Is this query asking for data stored in one of the above databases?
2. Or is this a general question unrelated to cars, animals or the library?

Return ONLY a JSON object with this exact structure:
{{
    "requires_database": true/false,
    "intent_type": "search" | "aggregate" | "general_knowledge",
    "entities": ["list", "of", "entities"],
    "databases": ["postgres"] or ["mongo"] or ["mysql"] or any combination or [],
    "reason": "brief explanation"
}}

Examples:
- "Quelles voitures sont disponibles ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["voitures"], "databases": ["postgres"], "reason": "Asking for car data"}}
- "Quel est le poids du lion ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["animaux"], "databases": ["mongo"], "reason": "Asking for animal data"}}
- "Combien de ventes ce mois ?" -> {{"requires_database": true, "intent_type": "aggregate", "entities": ["ventes"], "databases": ["postgres"], "reason": "Asking for sales statistics"}}
- "Quels animaux sont en danger ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["animaux"], "databases": ["mongo"], "reason": "Asking for animal conservation data"}}
- "Quels livres sont disponibles ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["livres"], "databases": ["mysql"], "reason": "Asking for library book data"}}
- "Qui a écrit Germinal ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["auteurs", "livres"], "databases": ["mysql"], "reason": "Asking for book/author data"}}
- "Quels emprunts sont en retard ?" -> {{"requires_database": true, "intent_type": "search", "entities": ["emprunts"], "databases": ["mysql"], "reason": "Asking for loan data"}}
- "Quelle est la capitale de la France ?" -> {{"requires_database": false, "intent_type": "general_knowledge", "entities": [], "databases": [], "reason": "General knowledge question"}}
"""
        response = self.invoke(prompt)
        
        # Try to parse the JSON response
        import json
        try:
            # Extract JSON from response (might have markdown code blocks)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON object in the text
            import re
            json_match = re.search(r'\{[^{}]*"requires_database"[^{}]*\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            
            intent_data = json.loads(json_str)
            
            # Ensure databases field is set correctly
            if intent_data.get("requires_database", False) and not intent_data.get("databases"):
                intent_data["databases"] = ["postgres"]
            
            # Add the raw response
            intent_data["raw_response"] = response
            return intent_data
        except Exception as e:
            # Fallback: try to extract key information from text
            requires_db = "requires_database\": true" in response or "database" in response.lower()
            entities = []
            
            # Try to extract entities from the response
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