import logging
import re
from typing import Union, Dict

from api.src.components.data_preprocessing import StringSplitter, TokenSpaceSplitter
from api.src.utils.unstructured_data_utils import NodesTextConverter, RelationshipsTextConverter
from api.src.components.base_components import BaseComponent
from api.src.llm.basellm import BaseLLM
from api.src.components.message_generator import SystemMessageGenerator, PromptGenerator


class ResultParser:
    def __init__(self, nodes_text_converter: NodesTextConverter, relationships_text_converter: RelationshipsTextConverter):
        self.nodes_text_converter = nodes_text_converter
        self.relationships_text_converter = relationships_text_converter

    def parse(self, result):
        """
        Parses the result and returns a dictionary containing the nodes and relationships.

        Args:
            result (list): The result to parse.

        Returns:
            dict: A dictionary containing the nodes and relationships.
        """
        if not isinstance(result, (list, tuple, set)):
            raise ValueError("Input 'result' must be a list or iterable.")

        nodes_regex = re.compile(r"Nodes:\s+(.*?)\s?\s?Relationships:\s?\s?(.*)")
        internal_regex = re.compile(r"\[(.*?)]")
        nodes = []
        relationships = []

        row: object
        for row in result:
            try:
                parsing = nodes_regex.match(row)
                if parsing is None:
                    continue
                raw_nodes = str(parsing.group(1))
                raw_relationships = parsing.group(2)
                nodes.extend(internal_regex.findall(raw_nodes))
                relationships.extend(internal_regex.findall(raw_relationships))
            except Exception as e:
                # Handle the exception here
                print(f"Error occurred: {e}")

        return {"nodes": nodes, "relationships": relationships}


class DataExtractor(BaseComponent):
    def __init__(self, llm: BaseLLM, result_parser: ResultParser, runner) -> None:
        super().__init__(runner)
        self.llm = llm
        self.result_parser = result_parser
        self.logger = logging.getLogger(__name__)
        self.runner = runner

    def process_with_labels(self, chunk, labels):
        if chunk is None or labels is None:
            return None
    
        try:
            messages = [
                {"role": "system", "content": SystemMessageGenerator.generate_system_message_with_schema()},
                {"role": "user", "content": PromptGenerator.generate(chunk, labels)},
            ]
            output = self.llm.generate(messages)
        except Exception as e:
            # Handle the exception here
            print(f"Error occurred: {e}")
            return None
    
        # Validate the output structure and content
        if not isinstance(output, str):
            raise ValueError("Output must be a string.")
    
        # Additional validation logic...
    
        self.logger.debug("Output: %s", output)
        return output

    def run(self, data: str) -> Dict[str, Union[NodesTextConverter, RelationshipsTextConverter]]:
        if not isinstance(data, str):
            raise ValueError("Input 'data' must be a string.")

        if not data:
            raise ValueError("Input 'data' cannot be empty.")

        system_message = SystemMessageGenerator.generate_system_message()
        prompt_string = PromptGenerator.generate("")
        token_usage_per_prompt = self.llm.num_tokens_from_string(
            system_message + prompt_string
        )
        chunked_data = TokenSpaceSplitter()

        results = []
        labels = set()
        self.logger.info("Starting chunked processing")

        try:
            for chunk in chunked_data:
                proceeded_chunk = self.process_with_labels(chunk, list(labels))
                self.logger.debug("proceeded_chunk: %s", proceeded_chunk)
                chunk_result = self.result_parser.parse([proceeded_chunk])
                self.logger.debug("chunk_result: %s", chunk_result)
                new_labels = [node["label"] for node in chunk_result["nodes"]]
                self.logger.debug("new_labels: %s", new_labels)
                results.append(proceeded_chunk)
                labels.update(new_labels)
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            return None

        return self.result_parser.parse(results)


class DataExtractorWithSchema(BaseComponent):
    llm: BaseLLM

    def __init__(self, llm, result_parser: ResultParser, runner) -> None:
        super().__init__(runner)
        self.llm = llm
        self.result_parser = result_parser

    def run(self, data: str, schema: str) -> Dict[str, Union[NodesTextConverter, RelationshipsTextConverter]]:
        system_message = SystemMessageGenerator.generate_system_message_with_schema()
        prompt_string = (
                system_message
                + PromptGenerator.generate(schema=schema, data="")
        )
        token_usage_per_prompt = self.llm.num_tokens_from_string(
            system_message + prompt_string
        )

        chunked_data = TokenSpaceSplitter()
        result = []
        logging.info("Starting chunked processing")

        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": ""},
        ]

        for chunk in chunked_data:
            messages[1]["content"] = PromptGenerator.generate(chunk, schema)
            logging.info("prompt %s", messages[1]["content"])
            try:
                output = self.llm.generate(messages)
            except Exception as e:
                output = str(e)
            result.append(output)
        return self.result_parser.parse(result)
