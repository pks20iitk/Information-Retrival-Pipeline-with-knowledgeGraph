from abc import ABC, abstractmethod
from typing import List, Union, Any


class DataDisambiguationSystemMessageProvider(ABC):
    @abstractmethod
    def generate_system_message_for_nodes(self) -> str:
        pass

    @abstractmethod
    def generate_system_message_for_relationships(self) -> str:
        pass


class DataDisambiguationPromptProvider(ABC):
    @abstractmethod
    def generate_prompt(self, data: Any) -> str:
        pass
