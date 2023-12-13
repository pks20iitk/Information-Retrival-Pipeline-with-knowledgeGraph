from api.src.embedding.base_embedding import BaseEmbedding
import openai


class OpenAIEmbedding(BaseEmbedding):
    """Wrapper around OpenAI embedding models."""

    def __init__(self, openai_api_key: str, model_name: str = "text-embedding-ada-002") -> None:
        super().__init__()
        openai.api_key = openai_api_key
        self.model = model_name

    async def generate(self, Input: str) -> str:
        embedding = openai.Embedding.create(input=input, model=self.model)
        return embedding["data"][0]["embedding"]
