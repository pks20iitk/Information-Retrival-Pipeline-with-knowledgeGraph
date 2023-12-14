import secrets
from typing import Callable, List

import openai
import tiktoken
from api.src.llm.basellm import BaseLLM
from retry import retry


class LLMException(Exception):
    pass


class TokenGenerator:
    @staticmethod
    def generate_token():
        """
        Generates a secure token using a secure random number generator.
        """
        return secrets.token_hex(16)

    @staticmethod
    def validate_token(token):
        """
        Validates the given token.
        """
        # code for validating token

    def invalidate_token(self, token):
        """
        Invalidates the given token.
        """
        # code to invalidate the token


class OpenAIChat(BaseLLM):
    """Wrapper around OpenAI Chat large language models."""

    def __init__(
            self,
            openai_api_key: str = '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',
            model_name: str = "gpt-3.5-turbo",
            max_tokens: int = 3000,
            temperature: float = 0.0,
    ) -> None:
        openai.api_key = openai_api_key
        self.model = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

    @retry(tries=3, delay=1)
    def generate(self, messages):
        try:
            completions = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=messages,
            )
            return completions.choices[0].message.content
        except openai.error.InvalidRequestError as e:
            raise LLMException(f"Error: {e}")
        except openai.error.AuthenticationError as e:
            raise LLMException("Error: The provided OpenAI api key is invalid")
        except openai.error.APIError as e:
            raise LLMException(f"Retrying LLM call {e}")

    async def generate_streaming(
            self,
            messages: List[str],
            on_token_callback: Callable[[str], None],
    ) -> List[str]:
        result = []
        try:
            completions = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=messages,
                stream=True,
            )
            for message in completions:
                delta = message["choices"][0]["delta"]
                if "content" in delta:
                    result.append(delta["content"])
                await on_token_callback(message)
            return result
        except openai.error.APIError as e:
            raise LLMException(f"Retrying LLM call {e}")

    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def max_allowed_token_length(self) -> int:
        # TODO: list all models and their max tokens from api
        return 2049
