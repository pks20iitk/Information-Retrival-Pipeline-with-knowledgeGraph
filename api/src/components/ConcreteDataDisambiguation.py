from api.src.components.data_disambigution_base import (DataDisambiguationSystemMessageProvider,
                                                        DataDisambiguationPromptProvider)
from api.src.components.base_components import BaseComponent
from typing import List, Union, Any, Dict
import json
import re
from itertools import groupby
from api.src.utils.unstructured_data_utils import RelationshipsTextConverter, NodesTextConverter
from api.src.llm.openai import OpenAIChat

regex = "Nodes:\s+(.*?)\s?\s?Relationships:\s+(.*)"
internalRegex = "\[(.*?)\]"
jsonRegex = "\{.*\}"


class ConcreteDataDisambiguationSystemMessageProvider(DataDisambiguationSystemMessageProvider):
    def generate_system_message_for_nodes(self) -> str:
        return """Your task is to identify if there are duplicated nodes and if so merge them into one nod. Only merge the nodes that refer to the same entity.
                You will be given different datasets of nodes and some of these nodes may be duplicated or refer to the same entity. 
                The datasets contains nodes in the form [ENTITY_ID, TYPE, PROPERTIES]. When you have completed your task please give me the 
                resulting nodes in the same format. Only return the nodes and relationships no other text. If there is no duplicated nodes return the original nodes.

                Here is an example of the input you will be given:
                ["alice", "Person", {"age": 25, "occupation": "lawyer", "name":"Alice"}], ["bob", "Person", {"occupation": "journalist", "name": "Bob"}], ["alice.com", "Webpage", {"url": "www.alice.com"}], ["bob.com", "Webpage", {"url": "www.bob.com"}]
                """

    def generate_system_message_for_relationships(self) -> str:
        return """
               Your task is to identify if a set of relationships make sense.
               If they do not make sense please remove them from the dataset.
               Some relationships may be duplicated or refer to the same entity. 
               Please merge relationships that refer to the same entity.
               The datasets contains relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES].
               You will also be given a set of ENTITY_IDs that are valid.
               Some relationships may use ENTITY_IDs that are not in the valid set but refer to a entity in the valid set.
               If a relationships refer to a ENTITY_ID in the valid set please change the ID so it matches the valid ID.
               When you have completed your task please give me the valid relationships in the same format. Only return the relationships no other text.

               Here is an example of the input you will be given:
               ["alice", "roommate", "bob", {"start": 2021}], ["alice", "owns", "alice.com", {}], ["bob", "owns", "bob.com", {}]
               """


class ConcreteDataDisambiguationPromptProvider(DataDisambiguationPromptProvider):
    def generate_prompt(self, data: Any) -> str:
        return "Concrete System Message for Prompt"


class DataDisambiguation(BaseComponent):
    def __init__(self, llm=None, system_message_provider=None, prompt_provider=None, runner=None) -> None:
        super().__init__(runner)
        self.llm = OpenAIChat(openai_api_key="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")
        self.system_message_provider = system_message_provider
        self.prompt_provider = prompt_provider

    def run(self, data: dict) -> Dict[str, List[Any]]:
        nodes = sorted(data["nodes"], key=lambda x: x["label"])
        relationships = data["relationships"]
        new_nodes = []
        new_relationships = []

        node_groups = groupby(nodes, lambda x: x["label"])
        for group in node_groups:
            disString = ""
            nodes_in_group = list(group[1])
            if len(nodes_in_group) == 1:
                new_nodes.extend(nodes_in_group)
                continue

            for node in nodes_in_group:
                disString += (
                        '["'
                        + node["name"]
                        + '", "'
                        + node["label"]
                        + '", '
                        + json.dumps(node["properties"])
                        + "]\n"
                )

            messages = [
                {"role": "system", "content": self.system_message_provider.generate_system_message_for_nodes()},
                {"role": "user", "content": self.prompt_provider.generate_prompt(disString)},
            ]
            rawNodes = self.llm.generate(messages)

            n = re.findall(internalRegex, rawNodes)

            # Instantiate NodesTextConverter with 'n' as an argument
            nodes_converter = NodesTextConverter()
            # Call the text_to_list_of_dict method to perform the conversion
            new_nodes.extend(nodes_converter.text_to_list_of_dict(nodes_text=n))

        relationship_data = "Relationships:\n"
        for relation in relationships:
            relationship_data += (
                    '["'
                    + relation["start"]
                    + '", "'
                    + relation["type"]
                    + '", "'
                    + relation["end"]
                    + '", '
                    + json.dumps(relation["properties"])
                    + "]\n"
            )

        node_labels = [node["name"] for node in new_nodes]
        relationship_data += "Valid Nodes:\n" + "\n".join(node_labels)

        messages = [
            {
                "role": "system",
                "content": self.system_message_provider.generate_system_message_for_relationships(),
            },
            {"role": "user", "content": self.prompt_provider.generate_prompt(relationship_data)},
        ]
        rawRelationships = self.llm.generate(messages)
        rels = re.findall(internalRegex, rawRelationships)
        relations_converter = RelationshipsTextConverter()
        new_relationships.extend(relations_converter.text_to_list_of_dict(relationships_text=rels))
        return {"nodes": new_nodes, "relationships": new_relationships}


if __name__ == "__main__":
    # Sample input data for debugging
    sample_data = {
        "nodes": [
            {"name": "Alice", "label": "Person", "properties": {"age": 25}},
            {"name": "Bob", "label": "Person", "properties": {"age": 30}},
        ],
        "relationships": [
            {"start": "Alice", "type": "knows", "end": "Bob", "properties": {}},
            {"start": "Bob", "type": "works_with", "end": "Charlie", "properties": {}},
        ],
    }

    llm = OpenAIChat(
        openai_api_key="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")  # Replace with your llm instance
    system_message_provider = ConcreteDataDisambiguationSystemMessageProvider()
    prompt_provider = ConcreteDataDisambiguationPromptProvider()
    runner = None  # Replace with your runner instance

    data_disambiguation = DataDisambiguation(llm, system_message_provider, prompt_provider, runner)
    result = data_disambiguation.run(sample_data)

    # Debugging output
    print("Debugging Result:")
    print(result)
