"""
Serveur FastAPI pour l'orchestrateur.
Simule une API Ollama pour être compatible nativement avec OpenWebUI.
"""
import os
import logging
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

# Import de votre logique d'orchestration
from src.orchestrator.orchestrator import FederatedRAGOrchestrator

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Kiwi Orchestrator (Ollama Compatible)")

# --- Configuration & Initialisation ---
config = {
    "mcp_gateway_url": os.getenv("MCP_GATEWAY_URL", "ws://mcp-gateway:9000"),
    "ollama_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
    "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
}

# On initialise l'orchestrateur au démarrage
orchestrator = FederatedRAGOrchestrator(config)

# --- Modèles Pydantic (Protocole Ollama) ---

class Message(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None

class OllamaChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = False
    options: Optional[Dict[str, Any]] = None
    keep_alive: Optional[Any] = None

class OllamaGenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[int]] = None
    options: Optional[Dict[str, Any]] = None

class OllamaShowRequest(BaseModel):
    name: str

# --- Endpoints API (Compatibilité Ollama) ---

@app.get("/")
async def root():
    """Vérification rapide que le service tourne."""
    return "Ollama is running"

@app.get("/api/version")
async def api_version():
    """
    Requis par OpenWebUI pour valider la connexion.
    Retourne une version fictive d'Ollama.
    """
    return {"version": "0.1.30"}

@app.get("/api/tags")
async def api_tags():
    """
    Liste les modèles disponibles.
    CORRECTION: Ajout de ':latest' pour satisfaire OpenWebUI.
    """
    return {
        "models": [
            {
                "name": "Kiwi-Orchestrator:latest",  # <-- IMPORTANT: :latest ajouté
                "model": "Kiwi-Orchestrator:latest", # <-- IMPORTANT: :latest ajouté
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 0,
                "digest": "sha256:1234567890abcdef",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": "7B",
                    "quantization_level": "Q4_0"
                }
            }
        ]
    }

@app.post("/api/show")
async def api_show(request: OllamaShowRequest):
    """
    Retourne les métadonnées du modèle.
    """
    # On accepte n'importe quel nom pour éviter les erreurs 404
    return {
        "license": "MIT",
        "modelfile": f"# Modelfile for {request.name}\nFROM llama3",
        "parameters": "",
        "template": "",
        "system": "Tu es un orchestrateur intelligent connecté à plusieurs bases de données.",
        "details": {
            "parent_model": "",
            "format": "gguf",
            "family": "llama",
            "families": ["llama"],
            "parameter_size": "7B",
            "quantization_level": "Q4_0"
        },
        "messages": []
    }

@app.post("/api/chat")
async def api_chat(request: OllamaChatRequest):
    """
    Endpoint principal pour la conversation.
    """
    logger.info(f"Chat request received for model: {request.model}")
    
    # Validation basique
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    user_query = request.messages[-1].content
    
    # Mesure du temps pour les stats Ollama
    start_time = time.time()
    
    try:
        # Exécution de l'orchestrateur (LangGraph)
        result = await orchestrator.run_async(user_query)
        
        # Extraction de la réponse finale
        # On sécurise l'accès au dictionnaire result
        if isinstance(result, dict):
            response_content = result.get("final_output", str(result))
            # Gestion des erreurs internes rapportées par l'agent
            if result.get("errors"):
                logger.error(f"Orchestrator logic errors: {result['errors']}")
        else:
            response_content = str(result)

    except Exception as e:
        logger.error(f"Critical error executing orchestrator: {e}", exc_info=True)
        response_content = f"Je rencontre une erreur technique : {str(e)}"

    # Calcul de la durée en nanosecondes (requis par spec Ollama)
    duration_ns = int((time.time() - start_time) * 1e9)

    return {
        "model": request.model,
        "created_at": "2024-01-01T00:00:00Z",
        "message": {
            "role": "assistant",
            "content": response_content
        },
        "done": True,
        "total_duration": duration_ns,
        "load_duration": 0,
        "prompt_eval_count": 0,
        "eval_count": 0
    }

@app.post("/api/generate")
async def api_generate(request: OllamaGenerateRequest):
    """
    Endpoint pour la génération de texte simple (titres, suggestions).
    """
    logger.info(f"Generate request received: {request.prompt[:50]}...")
    
    try:
        # Pour la génération de titre, on peut appeler l'orchestrateur 
        # ou un LLM direct si l'orchestrateur est trop lourd.
        # Ici on utilise l'orchestrateur pour rester simple.
        result = await orchestrator.run_async(request.prompt)
        
        if isinstance(result, dict):
            response_content = result.get("final_output", str(result))
        else:
            response_content = str(result)
        
        return {
            "model": request.model,
            "created_at": "2024-01-01T00:00:00Z",
            "response": response_content,
            "done": True,
            "context": [],
            "total_duration": 0,
            "load_duration": 0,
            "prompt_eval_count": 0,
            "eval_count": 0
        }
    except Exception as e:
        logger.error(f"Error in generate: {e}")
        return {
            "response": f"Error: {str(e)}",
            "done": True
        }

# --- Endpoints Utilitaires ---

@app.get("/health")
async def health_check():
    """Health check standard."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    