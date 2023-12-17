from typing import List, Optional
from langchain.graphs.graph_document import Node as BaseNode, Relationship as BaseRelationship
from api.KnowledgeGraph_Generation.knowledge_graph_model import Node, Relationship, Property


class KnowledgeGraphMapper:
    """Class for mapping KnowledgeGraph elements to base graph elements."""

    @staticmethod
    def format_property_key(s: str) -> str:
        """Format property key."""
        words = s.split()
        if not words:
            return s
        first_word = words[0].lower()
        capitalized_words = [word.capitalize() for word in words[1:]]
        return "".join([first_word] + capitalized_words)

    @staticmethod
    def props_to_dict(props: Optional[List[Property]]) -> dict:
        """Convert properties to a dictionary."""
        properties = {}
        if not props:
            return properties
        for p in props:
            properties[KnowledgeGraphMapper.format_property_key(p.key)] = p.value
        return properties

    @staticmethod
    def map_to_base_node(node: Node) -> BaseNode:
        """Map the KnowledgeGraph Node to the base Node."""
        properties = KnowledgeGraphMapper.props_to_dict(node.properties)
        properties["name"] = node.id.title()
        return BaseNode(id=node.id.title(), type=node.type.capitalize(), properties=properties)

    @staticmethod
    def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
        """Map the KnowledgeGraph Relationship to the base Relationship."""
        source = KnowledgeGraphMapper.map_to_base_node(rel.source)
        target = KnowledgeGraphMapper.map_to_base_node(rel.target)
        properties = KnowledgeGraphMapper.props_to_dict(rel.properties)
        return BaseRelationship(source=source, target=target, type=rel.type, properties=properties)
