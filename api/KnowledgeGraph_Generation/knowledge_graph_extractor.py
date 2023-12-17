import os
from typing import List, Optional
from langchain.chains.openai_functions import create_openai_fn_chain, create_structured_output_chain
from langchain.prompts import ChatPromptTemplate
from api.KnowledgeGraph_Generation.chat_openai_initializer import ChatOpenAIInitializer
from api.KnowledgeGraph_Generation.knowledge_graph_model import KnowledgeGraph
from langchain.prompts import ChatPromptTemplate


class KnowledgeGraphExtractor:
    """Class for extracting information and building a knowledge graph."""

    def __init__(self):
        self.llm = ChatOpenAIInitializer(openai_key="OPENAI_API_KEY").chat_openai

    def get_extraction_chain(
            self,
            allowed_nodes: Optional[List[str]] = None,
            allowed_rels: Optional[List[str]] = None
    ) -> callable:
        """Generate a chain for extracting structured information for the knowledge graph."""
        prompt = self._create_knowledge_graph_prompt(allowed_nodes, allowed_rels)
        return create_structured_output_chain(KnowledgeGraph, self.llm, prompt, verbose=False)

    @staticmethod
    def _create_knowledge_graph_prompt(
            allowed_nodes: Optional[List[str]] = None,
            allowed_rels: Optional[List[str]] = None
    ) -> ChatPromptTemplate:
        """Create a prompt for guiding knowledge graph extraction."""
        system_message = f"""# Knowledge Graph Instructions for GPT-3.5
        "system",
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
## 2. Labeling Nodes
- **Consistency**: Ensure you use basic or elementary types for node labels.
  - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
{'- **Allowed Node Labels:**' + ", ".join(allowed_nodes) if allowed_nodes else ""}
{'- **Allowed Relationship Types**:' + ", ".join(allowed_rels) if allowed_rels else ""}
## 3. Handling Numerical Data and Dates
- Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
- **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
- **Property Format**: Properties must be in a key-value format.
- **Quotation Marks**: Never use escaped single or double quotes within property values.
- **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
## 4. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
## 5. Strict Compliance
Adhere to the rules strictly. Non-compliance will result in termination.
          """
        human_messages = [
            ("human", "Use the given format to extract information from the following input: {input}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ]
        return ChatPromptTemplate.from_messages([("system", system_message)] + human_messages)

