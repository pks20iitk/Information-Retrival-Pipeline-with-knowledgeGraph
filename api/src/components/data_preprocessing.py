from typing import List
from api.src.llm.basellm import BaseLLM


class StringSplitter:
    @staticmethod
    def split(string, max_length) -> List[str]:
        return [string[i: i + max_length] for i in range(0, len(string), max_length)]


class TokenSpaceSplitter:
    @staticmethod
    def split(llm: BaseLLM, string: str, token_use_per_string: int) -> List[str]:
        allowed_tokens = llm.max_allowed_token_length() - token_use_per_string
        chunked_data = StringSplitter.split(string, 500)
        combined_chunks = []
        current_chunk = ""

        for chunk in chunked_data:
            if (
                    llm.num_tokens_from_string(current_chunk)
                    + llm.num_tokens_from_string(chunk)
                    < allowed_tokens
            ):
                current_chunk += chunk
            else:
                combined_chunks.append(current_chunk)
                current_chunk = chunk

        combined_chunks.append(current_chunk)
        return combined_chunks
