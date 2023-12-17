from typing import List, Optional
from langchain_community.graphs.graph_document import GraphDocument
from api.KnowledgeGraph_Generation.knowledgeGraph_mapper import KnowledgeGraphMapper
from api.KnowledgeGraph_Generation.knowledge_graph_extractor import KnowledgeGraphExtractor
from api.KnowledgeGraph_Generation.neo4j_graph_connector import graph
from langchain.schema import Document


def extract_and_store_graph(
        document: Document,
        nodes: Optional[List[str]] = None,
        rels: Optional[List[str]] = None) -> None:
    """

    @param rels:
    @param document:
    @type nodes: object
    """
    # Extract graph data using OpenAI functions
    extract_chain = KnowledgeGraphExtractor.get_extraction_chain(nodes, rels)
    data = extract_chain.run(document.page_content)
    # Construct a graph document
    graph_document = GraphDocument(
        nodes=[KnowledgeGraphMapper.map_to_base_node(node) for node in data.nodes],
        relationships=[KnowledgeGraphMapper.map_to_base_relationship(rel) for rel in data.rels],
        source=document
    )
    # Store information into a graph
    graph.add_graph_documents([graph_document])

    # Store information into a graph
    graph.add_graph_documents([graph_document])

