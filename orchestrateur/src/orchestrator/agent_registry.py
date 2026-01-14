"""Agent registry for managing agent instances."""
from src.agents.intent_agent import IntentAgent
from src.agents.retriever_agent import RetrieverAgent
from src.agents.sql_agent import SQLAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.composer_agent import ComposerAgent


class AgentRegistry:
    def __init__(self, config: dict):
        self.config = config
        self.agents = {
            "intent": IntentAgent(config),
            "retriever": RetrieverAgent(config),
            "sql": SQLAgent(config),
            "validator": ValidatorAgent(config),
            "composer": ComposerAgent(config)
        }
    
    def get_agent(self, agent_name: str):
        """Get an agent by name."""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.agents[agent_name]
