from typing import Any, Awaitable, Callable, Dict, List

from api.src.components.base_components import BaseComponent
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat


def generate_user_prompt(question: str, results: List[Dict[str, str]], exclude_embeddings: bool) -> str:
    return f"""
    The question was {question}
    Answer the question by using the following results:{results}
    """


# {[SummarizeCypherResult.remove_large_lists(el) for el in results] if exclude_embeddings else results}
class DataProcessor:
    @staticmethod
    def remove_large_lists(d: Dict[str, Any]) -> Dict[str, Any]:
        LIST_CUTOFF = 56
        CHARACTER_CUTOFF = 5000
        for key, value in d.items():
            if isinstance(value, list) and len(value) > LIST_CUTOFF:
                if all(isinstance(item, dict) for item in value):
                    d[key] = [DataProcessor.remove_large_lists(item) for item in value]
                else:
                    d[key] = None
            if isinstance(value, str) and len(value) > CHARACTER_CUTOFF:
                d[key] = d[key][:CHARACTER_CUTOFF]
            elif isinstance(value, dict):
                DataProcessor.remove_large_lists(d[key])
        return d


class SummarizeCypherResult(BaseComponent):
    llm: BaseLLM
    exclude_embeddings: bool
    system: str

    def __init__(self, System: str, llm: BaseLLM, exclude_embeddings: bool = True, runner=None) -> None:
        """

        @rtype: object
        @type llm: object
        """
        super().__init__(runner)
        self.llm = llm
        self.exclude_embeddings = exclude_embeddings
        self.System = System

    def create_messages(self, question: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {"role": "system", "content": self.System},
            {"role": "user",
             "content": generate_user_prompt(question, results, self.exclude_embeddings)},
        ]

    def run(
            self,
            question: str,
            results: List[Dict[str, Any]],
    ) -> str:
        messages = self.create_messages(question, results)
        output = self.llm.generate(messages)
        return output

    async def run_async(
            self,
            question: str,
            results: List[Dict[str, Any]],
            callback: Callable[[str], Awaitable[Any]] = None,
    ) -> str:
        if callback is None:
            callback = self.default_callback
        messages = self.create_messages(question, results)
        output = await self.llm.generateStreaming(messages, onTokenCallback=callback)
        return "".join(output)

    async def default_callback(self, output: str) -> None:
        pass

    @classmethod
    def remove_large_lists(cls, el):
        pass
