from typing import List
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat


class StringSplitter:
    @staticmethod
    def split(string: str, max_length: int) -> List[str]:
        """
        Splits a string into substrings of a specified maximum length.

        Args:
            string (str): The string to be split.
            max_length (int): The maximum length of each substring.

        Returns:
            List[str]: A list of substrings.

        Raises:
            ValueError: If max_length is less than or equal to 0.
            TypeError: If string is not a string.
        """
        if max_length <= 0:
            raise ValueError("max_length must be greater than 0")
        if string is None or string == "":
            return []
        if not isinstance(string, str):
            raise TypeError("Input 'string' must be a string.")
        if max_length >= len(string):
            return [string]
        return [string[i: i + max_length] for i in range(0, len(string), max_length)]


class TokenSpaceSplitter:
    def split(self, llm: BaseLLM, string: str, token_use_per_string: int) -> List[str]:
        """
        Splits the input string into chunks based on the maximum allowed token length.

        Args:
            llm (BaseLLM): The language model used for tokenization.
            string (str): The input string to be split.
            token_use_per_string (int): The number of tokens used per string.

        Returns:
            List[str]: The list of split chunks.
        """
        try:
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
        except Exception as e:
            # Handle the exception here
            print(f"An error occurred: {str(e)}")
            return []


if __name__ == "__main__":
    # Example input
    example_string = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    example_token_use_per_string = 10  # Replace with your desired value

    # Example language model (replace with your actual implementation)
    example_llm = OpenAIChat(openai_api_key='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')

    # Example TokenSpaceSplitter usage
    token_space_splitter = TokenSpaceSplitter()
    result_chunks = token_space_splitter.split(example_llm, example_string, example_token_use_per_string)

    # Print the result
    print("Original String:")
    print(example_string)
    print("\nResult Chunks:")
    for i, chunk in enumerate(result_chunks):
        print(f"Chunk {i + 1}: {chunk}")
