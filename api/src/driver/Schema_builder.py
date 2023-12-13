import logging
from typing import Optional, Dict, List, Any


class SchemaBuilder:
    """Builds a schema representation of a Neo4j database."""

    @staticmethod
    def generate_node_properties_query() -> str:
        """
        Returns a Cypher query that retrieves the properties of all nodes in the database.
        The query filters out relationship elements and returns the labels and properties of each node.

        :return: A Cypher query string.
        """
        return """
                    CALL apoc.meta.data()
                    YIELD label, other, elementType, type, property
                    WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
                    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
                    RETURN {labels: nodeLabels, properties: properties} AS output
                """

    @staticmethod
    def generate_rel_properties_query() -> str:
        """
        Returns a Cypher query that retrieves the properties of all relationships in the database.
        The query filters out node elements and returns the types and properties of each relationship.

        :return: A Cypher query string.
        """
        return """
                CALL apoc.meta.data()
                YIELD label, other, elementType, type, property
                WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
                WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
                RETURN {type: nodeLabels, properties: properties} AS output
                """

    @staticmethod
    def generate_rel_query() -> str:
        """
        Returns a Cypher query that retrieves all relationships in the database.
        The query returns a string representation of each relationship.

        :return: A Cypher query string.
        """
        return """
                   CALL apoc.meta.data()
                   YIELD label, other, elementType, type, property
                   WHERE type = "RELATIONSHIP" AND elementType = "node"
                   RETURN "(:" + label + ")-[:" + property + "]->(:" + toString(other[0]) + ")" AS output
                   """


class SchemaTextFormatter:
    @staticmethod
    def format(node_props: Optional[str], rel_props: Optional[str], rels: Optional[str]) -> str:
        """

        @rtype: object
        """
        return f"""
          This is the schema representation of the Neo4j database.
          Node properties are the following:
          {node_props}
          Relationship properties are the following:
          {rel_props}
          The relationships are the following
          {rels}
          """


class QueryExecutor:
    """
    This class executes read-only queries.
    """

    @staticmethod
    def execute_read_only_query(tx, cypher_query: str, params: Optional[Dict] = {}) -> List[Dict[str, Any]]:
        """
        Executes a read-only query.

        Args:
            tx: The transaction object.
            cypher_query: The Cypher query to execute.
            params: Optional parameters for the query.

        Returns:
            A list of dictionaries containing the query results.
        """
        result = tx.run(cypher_query, params)
        return [r.data() for r in result]

