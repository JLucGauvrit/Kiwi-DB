"""
Base agent class for all specialized agents.

Ce module définit la classe de base abstraite pour tous les agents
spécialisés du système RAG fédéré. Les agents héritent de cette classe
et implémentent leur propre logique métier via la méthode run().

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama


class BaseAgent(ABC):
    """
    Classe de base abstraite pour tous les agents du système.
    
    Fournit les fonctionnalités communes pour l'interaction avec
    le modèle de langage Ollama. Les agents spécialisés héritent
    de cette classe et implémentent leur logique métier.
    
    @param config: Configuration contenant les paramètres du modèle
    @type config: dict
    
    @ivar config: Configuration stockée de l'agent
    @ivar llm: Instance du modèle de langage ChatOllama
    """
    
    def __init__(self, config: dict):
        """
        Initialiser l'agent de base avec la configuration.
        
        @param config: Configuration contenant les URLs Ollama et le modèle à utiliser
        @type config: dict
        """
        self.config = config
        ollama_url = config.get("ollama_url", "http://ollama:11434")
        model = config.get("ollama_model", "llama3.2")
        
        self.llm = ChatOllama(
            base_url=ollama_url,
            model=model,
            temperature=0.1
        )
    
    def invoke(self, prompt: str) -> str:
        """
        Invoquer le modèle de langage avec un prompt.
        
        Envoie un prompt au modèle Ollama et retourne la réponse textuelle.
        Cette méthode est généralement appelée par les agents spécialisés
        pour obtenir les résultats du modèle de langage.
        
        @param prompt: Le prompt à envoyer au modèle de langage
        @type prompt: str
        @return: La réponse textuelle du modèle de langage
        @rtype: str
        """
        response = self.llm.invoke(prompt)
        return response.content

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Exécuter la logique métier de l'agent.
        
        Cette méthode abstraite doit être implémentée par tous les agents spécialisés.
        Elle contient la logique métier spécifique à l'agent pour traiter les entrées
        et produire les résultats appropriés.
        
        @param args: Arguments positionnels spécifiques à chaque agent
        @param kwargs: Arguments nommés spécifiques à chaque agent
        @return: Résultat du traitement de l'agent
        @rtype: Varie selon l'agent (dict, list, str, etc.)
        """
        pass
