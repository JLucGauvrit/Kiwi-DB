"""Base agent class."""
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama


class BaseAgent(ABC):
    def __init__(self, config: dict):
        self.config = config
        ollama_url = config.get("ollama_url", "http://ollama:11434")
        model = config.get("ollama_model", "llama3.2")
        
        self.llm = ChatOllama(
            base_url=ollama_url,
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
