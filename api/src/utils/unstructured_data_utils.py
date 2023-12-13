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

            name = node_list[0].strip().replace('"', "")
            label = node_list[1].strip().replace('"', "")
            properties = re.search(r"\{.*}", node)
            if properties is None:
                properties = "{}"
            else:
                properties = properties.group(0)
            properties = properties.replace("True", "true")
            try:
                properties = json.loads(properties)
            except:
                properties = {}
            result.append({"name": name, "label": label, "properties": properties})
        return result


class RelationshipsTextConverter(DataConverter):
    def text_to_list_of_dict(self, relationships_text: str) -> List[dict]:
        result = []
        for relation in relationships_text:
            relation_list = relation.split(",")
            if len(relation) < 3:
                continue
            start = relation_list[0].strip().replace('"', "")
            end = relation_list[1].strip().replace('"', "")
            relation_type = relation_list[1].strip().replace('"', "")

            properties = re.search(r'\{.*}', relation)
            if properties is None:
                properties = "{}"
            else:
                properties = properties.group(0)
            properties = properties.replace("True", "true")
            try:
                properties = json.loads(properties)
            except:
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
