"""Intent classification agent."""
from src.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    def run(self, query: str) -> dict:
        """Classify user intent from query."""
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
