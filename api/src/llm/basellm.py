from abc import ABC, abstractmethod
from typing import Any, List, Dict


class LLMException(Exception):
    pass


class TokenGenerator:
    @staticmethod
    def raise_exception(ex):
        raise ex


class BaseLLM(ABC):
    """LLM wrapper should take in a prompt and return a string."""

    @abstractmethod
    def generate(self, messages: None) -> str:
        """Generates output based on the given prompt messages."""
        pass

    @abstractmethod
    async def generate_streaming(self, messages: List[str], on_token_callback) -> List[Any]:
        """Generates output asynchronously based on the given prompt messages."""
        pass

    @abstractmethod
    async def num_tokens_from_string(self, string: str) -> int:
        """Given a string, returns the number of tokens the string consists of."""
        pass

    @abstractmethod
    async def max_allowed_token_length(self) -> int:
        """Returns the maximum number of tokens the LLM can handle.
        :rtype: object
        """
        pass

    def generateStreaming(self, messages, onTokenCallback):
        pass
