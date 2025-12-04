"""Agent registry for managing specialized agents."""
from typing import Dict, Any
from src.agents.intent_agent import IntentAgent
from src.agents.retriever_agent import RetrieverAgent
from src.agents.sql_agent import SQLAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.composer_agent import ComposerAgent


class AgentRegistry:
    def __init__(self, config: dict):
        self.config = config
        self._agents: Dict[str, Any] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all specialized agents."""
        self._agents["intent"] = IntentAgent(self.config)
        self._agents["retriever"] = RetrieverAgent(self.config)
        self._agents["sql"] = SQLAgent(self.config)
        self._agents["validator"] = ValidatorAgent(self.config)
        self._agents["composer"] = ComposerAgent(self.config)

    def get_agent(self, agent_type: str):
        """Get agent by type."""
        if agent_type not in self._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return self._agents[agent_type]

    def register_agent(self, agent_type: str, agent):
        """Register a new agent."""
        self._agents[agent_type] = agent
