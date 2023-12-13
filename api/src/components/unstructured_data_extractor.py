import re
from typing import List, Dict, Union

from api.src.components.data_preprocessing import StringSplitter, TokenSpaceSplitter
from api.src.utils.unstructured_data_utils import NodesTextConverter, RelationshipsTextConverter
from api.src.components.base_components import BaseComponent
from api.src.llm.basellm import BaseLLM
from api.src.components.message_generator import SystemMessageGenerator, PromptGenerator


class ResultParser:
    @staticmethod
    def parse(result):
        regex = "Nodes:\s+(.*?)\s?\s?Relationships:\s?\s?(.*)"
        internal_regex = "\[(.*?)\]"
        nodes = []
        relationships = []

        for row in result:
            parsing = re.match(regex, row, flags=re.S)
            if parsing is None:
                continue
            raw_nodes = str(parsing.group(1))
            raw_relationships = parsing.group(2)
            nodes.extend(re.findall(internal_regex, raw_nodes))
            relationships.extend(re.findall(internal_regex, raw_relationships))

        parsed_result = dict()
        parsed_result["nodes"] = NodesTextConverter()
        parsed_result["relationships"] = RelationshipsTextConverter()
        return parsed_result


class DataExtractor(BaseComponent):
    llm: BaseLLM

    def __init__(self, llm: BaseLLM, result_parser: ResultParser, runner) -> None:
        super().__init__(runner)
        self.llm = llm
        self.result_parser = result_parser

    def process_with_labels(self, chunk, labels):
        messages = [
            {"role": "system", "content": SystemMessageGenerator.generate_system_message_with_schema()},
            {"role": "user", "content": PromptGenerator.generate(chunk, labels)},
        ]
        output = self.llm.generate(messages)
        return output

    def run(self, data: str) -> dict[str, Union[NodesTextConverter, RelationshipsTextConverter]]:
        system_message = SystemMessageGenerator.generate_system_message()
        prompt_string = PromptGenerator.generate("")
        token_usage_per_prompt = self.llm.num_tokens_from_string(
            system_message + prompt_string
        )
        chunked_data = TokenSpaceSplitter()

        results = []
        labels = set()
        print("Starting chunked processing")

        for chunk in chunked_data:
            proceeded_chunk = self.process_with_labels(chunk, list(labels))
            print("proceeded_chunk", proceeded_chunk)
            chunk_result = self.result_parser.parse([proceeded_chunk])
            print("chunk_result", chunk_result)
            new_labels = [node["label"] for node in chunk_result["nodes"]]
            print("new_labels", new_labels)
            results.append(proceeded_chunk)
            labels.update(new_labels)

        return self.result_parser.parse(results)


class DataExtractorWithSchema(BaseComponent):
    llm: BaseLLM

    def __init__(self, llm, result_parser: ResultParser, runner) -> None:
        super().__init__(runner)
        self.llm = llm
        self.result_parser = result_parser

    def run(self, data: str, schema: str) -> dict[str, Union[NodesTextConverter, RelationshipsTextConverter]]:
        system_message = SystemMessageGenerator.generate_system_message_with_schema()
        prompt_string = (
                SystemMessageGenerator.generate_system_message_with_schema()
                + PromptGenerator.generate(schema=schema, data="")
        )
        token_usage_per_prompt = self.llm.num_tokens_from_string(
            system_message + prompt_string
        )

        chunked_data = TokenSpaceSplitter()
        result = []
        print("Starting chunked processing")

        for chunk in chunked_data:
            print("prompt", PromptGenerator.generate(chunk, schema))
            messages = [
                {
                    "role": "system",
                    "content": system_message,
                },
                {"role": "user", "content": PromptGenerator.generate(chunk, schema)},
            ]
            output = self.llm.generate(messages)
            result.append(output)
        return self.result_parser.parse(result)
