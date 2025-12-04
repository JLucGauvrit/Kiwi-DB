"""Base agent class."""
from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI


class BaseAgent(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1
        )

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute agent logic."""
        pass
