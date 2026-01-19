"""
Agent registry for managing and instantiating specialized agents.

Ce module implémente le registre des agents qui gère l'instanciation
et l'accès à tous les agents spécialisés du système.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from typing import Dict, Any
from src.agents.intent_agent import IntentAgent
from src.agents.retriever_agent import RetrieverAgent
from src.agents.sql_agent import SQLAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.composer_agent import ComposerAgent


class AgentRegistry:
    """
    Registre centralisé pour la gestion des agents spécialisés.
    
    Instancie et fournit l'accès à tous les agents du système RAG fédéré.
    
    @param config: Configuration partagée pour tous les agents
    @type config: dict
    
    @ivar config: Configuration stockée
    @ivar agents: Dictionnaire contenant les instances des agents
    """
    
    def __init__(self, config: dict):
        """
        Initialiser le registre des agents.
        
        Instancie tous les agents spécialisés avec la configuration fournie.
        
        @param config: Configuration contenant les paramètres pour les agents
        @type config: dict
        """
        self.config = config
        self.agents = {
            "intent": IntentAgent(config),
            "retriever": RetrieverAgent(config),
            "sql": SQLAgent(config),
            "validator": ValidatorAgent(config),
            "composer": ComposerAgent(config)
        }
    
    def get_agent(self, agent_name: str):
        """
        Récupérer un agent par son nom.
        
        @param agent_name: Nom de l'agent à récupérer
        @type agent_name: str
        @return: Instance de l'agent demandé
        @raise ValueError: Si le nom de l'agent n'existe pas
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.agents[agent_name]
