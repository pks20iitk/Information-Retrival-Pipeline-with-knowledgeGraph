from abc import ABC, abstractmethod


class EmbeddingGenerator(ABC):
    """Base class for embedding generation."""

    @abstractmethod
    async def generate(self, Input: str) -> str:
        """Generate embedding for the given input."""
        pass


class BaseEmbedding(EmbeddingGenerator):
    """Concrete implementation of EmbeddingGenerator."""

    async def generate(self, input: str) -> str:
        """Generate embedding for the given input."""
        # Implement the specific logic for embedding generation
        pass
