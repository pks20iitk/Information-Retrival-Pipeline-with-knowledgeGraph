import json.decoder
from json import JSONDecodeError
from api.src.components.base_components import DataConverter
from typing import List, Union
import json
import re


class NodesTextConverter(DataConverter):

    def text_to_list_of_dict(self, nodes_text: str) -> List[dict]:
        result = []
        for node in nodes_text:
            node_list = node.split(",")
            if len(node_list) < 2:
                continue

            name = re.sub(r'[^a-zA-Z0-9_]', '', node_list[0])
            label = re.sub(r'[^a-zA-Z0-9_]', '', node_list[1])

            properties_start = node.find("{")
            properties_end = node.find("}")
            if properties_start != -1 and properties_end != -1:
                properties = node[properties_start:properties_end+1]
            else:
                properties = "{}"
            properties = json.loads(properties.replace("True", "true"), ensure_ascii=False)

            try:
                properties = json.loads(properties)
            except JSONDecodeError:
                properties = {}

            result.append({"name": name, "label": label, "properties": properties})
        return result


class RelationshipsTextConverter(DataConverter):
    def text_to_list_of_dict(self, relationships_text: str) -> List[dict]:
        result = []
        for relation in relationships_text:
            relation_list = relation.split(",")
            if len(relation_list) < 3:
                continue
            start = relation_list[0].strip().replace('"', "")
            end = relation_list[1].strip().replace('"', "")
            relation_type = relation_list[2].strip().replace('"', "")

            properties = re.search(r'\{.*?\}', relation)
            if properties is None:
                properties = "{}"
            else:
                properties = properties.group(0)
            properties = properties.replace("True", "true").replace("False", "false")
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                properties = {}
            result.append({"start": start, "end": end, "type": relation_type, "properties": properties})
        return result


if __name__ == "__main__":
    # Example usage for debugging
    nodes_text = '["Alice", "Person", {"age": 25}]', '["Bob", "Person", {"age": 30}]'
    relationships_text = '["Alice", "knows", "Bob", {}]', '["Bob", "works_with", "Charlie", {}]'

    nodes_converter = NodesTextConverter()
    nodes_result = nodes_converter.text_to_list_of_dict(nodes_text)
    print(f"Nodes Result: {nodes_result}")

    relationships_converter = RelationshipsTextConverter()
    relationships_result = relationships_converter.text_to_list_of_dict(relationships_text)
    print(f"Relationships Result: {relationships_result}")
