"""Base agent class."""
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI


class BaseAgent(ABC):
    def __init__(self, config: dict):
        self.config = config
        api_key = config.get("openrouter_api_key", "")
        model = config.get("openrouter_model", "nvidia/nemotron-3-nano-30b-a3b:free")

        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model,
            temperature=0.1
        )
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt."""
        response = self.llm.invoke(prompt)
        return response.content

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute agent logic."""
        pass
