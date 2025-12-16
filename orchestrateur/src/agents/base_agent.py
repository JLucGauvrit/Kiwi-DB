"""Base agent class."""
from abc import ABC, abstractmethod
import google.generativeai as genai


class BaseAgent(ABC):
    def __init__(self, config: dict):
        self.config = config
        api_key = config.get("google_api_key")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in config")
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel('gemini-2.5-flash')
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt."""
        response = self.llm.generate_content(prompt)
        return response.text

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute agent logic."""
        pass
