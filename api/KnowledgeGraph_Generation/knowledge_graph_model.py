from typing import List, Optional
from pydantic import Field, BaseModel


class Property(BaseModel):
    """A single property consisting of key and value."""
    key: str = Field(..., description="Key")
    value: str = Field(..., description="Value")


class GraphElement(BaseModel):
    """Base class for graph elements."""
    id: str = Field(..., description="Unique identifier for the graph element")
    properties: Optional[List[Property]] = Field(
        None, description="List of properties for the graph element"
    )

    def __str__(self):
        properties_str = ""
        if self.properties:
            properties_str = ", ".join([f"{prop.key}: {prop.value}" for prop in self.properties])
        return f"GraphElement(properties=[{properties_str}])"

    def __eq__(self, other):
        if isinstance(other, GraphElement):
            return self.properties == other.properties
        return False

    def __hash__(self):
        return hash((type(self), self.properties))


class Node(GraphElement):
    def __init__(__pydantic_self__, **data: Any):
        super().__init__(data)
        __pydantic_self__.type = None

    """A node in the knowledge graph."""
    # Additional node-specific attributes can be added here.
    pass


class Relationship(GraphElement):
    def __init__(__pydantic_self__, **data: Any):
        super().__init__(data)
        __pydantic_self__.source = None
        __pydantic_self__.type = None

    """A relationship in the knowledge graph."""
    # Additional relationship-specific attributes can be added here.
    pass


class KnowledgeGraph(BaseModel):
    """Generate a knowledge graph with entities and relationships."""
    nodes: List[Node] = Field(
        ..., description="List of nodes in the knowledge graph"
    )
    rels: List[Relationship] = Field(
        ..., description="List of relationships in the knowledge graph"
    )
