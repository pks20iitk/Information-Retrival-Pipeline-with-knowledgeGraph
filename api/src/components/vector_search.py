from typing import Dict, List, Union

from api.src.components.base_components import BaseComponent
from api.src.driver.Neo4j import Neo4jDatabase


class CypherConstructor:
    def construct_cypher(self, label, property, k) -> str:
        """
        Construct a Cypher query to find nodes with the highest similarity to a given input vector.

        Args:
            label (str): The label of the nodes to match.
            property (str): The property of the nodes to compare similarity.
            k (int): The number of nodes to return.

        Returns:
            str: The constructed Cypher query.
        """
        if label is None or label == "" or property is None or property == "" or k is None or k == "":
            raise ValueError("Invalid input parameters")

        escaped_label = label.replace("`", "``")
        escaped_property = property.replace("`", "``")

        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer")

        return f"""
        MATCH (n:`{label}`)
        WHERE n.`{property}` IS NOT NULL
        WITH n, gds.similarity.cosine($input_vector, n.`{property}`) AS similarity
        ORDER BY similarity DESC
        LIMIT $k
        RETURN apoc.map.removeKey(properties(n), $property) AS output
        """


class VectorSearch(BaseComponent):
    def __init__(self, database: Neo4jDatabase, label: str, property: str, k: int, runner: None) -> None:
        super().__init__(runner)
        if label is None or label == "" or property is None or property == "" or k is None or k == "":
            raise ValueError("Invalid input parameters")

        self.database = database
        self.cypher_constructor = CypherConstructor()
        self.generated_cypher = self.cypher_constructor.construct_cypher(label, property, k)

    def run(self, input_vector: str) -> Dict[str, List[str]]:
        if input_vector is None or input_vector == "":
            raise ValueError("Invalid input parameter")

        try:
            return {
                "output": [
                    str(el["output"])
                    for el in self.database.query(
                        self.generated_cypher, {"input_vector ": input_vector}
                    )
                ],
            }
        except Exception as e:
            raise e
