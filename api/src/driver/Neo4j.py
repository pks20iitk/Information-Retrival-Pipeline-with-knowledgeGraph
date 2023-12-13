from typing import Any, Union, List, Dict, Optional
from neo4j import GraphDatabase, exceptions
from api.src.driver.Schema_builder import SchemaBuilder, SchemaTextFormatter, QueryExecutor


class Neo4jDatabase:
    def __init__(
            self,
            host: str = "neo4j+s://d34db895.databases.neo4j.io",
            user: str = "neo4j",
            password: str = "cq3bB8rRwzbCwAJHUQau9qkkHwkIWz6YMpYd6qxFIOs",
            database: str = "neo4j",
            read_only: bool = True,
    ) -> None:
        """Initialize a neo4j database"""
        self._driver = GraphDatabase.driver(host, auth=(user, password))
        self._database = database
        self._read_only = read_only
        self.schema = ""
        # Verify connection
        try:
            self._driver.verify_connectivity()
        except exceptions.ServiceUnavailable:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the url is correct"
            )
        except exceptions.AuthError:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the username and password are correct"
            )
        try:
            self.refresh_schema()
        except:
            raise ValueError("Missing APOC Core plugin")

    def query(self, cypher_query: str, params: Optional[Dict] = {}) -> List[Dict[str, Any]]:
        with self._driver.session(database=self._database) as session:
            try:
                if self._read_only:
                    result = session.read_transaction(
                        QueryExecutor.execute_read_only_query, cypher_query, params
                    )
                    return result
                else:
                    result = session.run(cypher_query, params)
                    # Limit to at most 10 results
                    return [r.data() for r in result]

            # Catch Cypher syntax errors
            except exceptions.CypherSyntaxError as e:
                return [
                    {
                        "code": "invalid_cypher",
                        "message": f"Invalid Cypher statement due to an error: {e}",
                    }
                ]

            except exceptions.ClientError as e:
                # Catch access mode errors
                if e.code == "Neo.ClientError.Statement.AccessMode":
                    return [
                        {
                            "code": "error",
                            "message": "Couldn't execute the query due to the read only access to Neo4j",
                        }
                    ]
                else:
                    return [{"code": "error", "message": e}]

    def refresh_schema(self) -> None:
        node_props = [el["output"] for el in self.query(SchemaBuilder.generate_node_properties_query())]
        rel_props = [el["output"] for el in self.query(SchemaBuilder.generate_rel_properties_query())]
        rels = [el["output"] for el in self.query(SchemaBuilder.generate_rel_query())]
        schema = self._generate_schema_text(node_props, rel_props, rels)
        self.schema = schema
        print(schema)

    def _generate_schema_text(self, node_props, rel_props, rels):
        """

        @rtype: object
        """
        return SchemaTextFormatter.format(node_props, rel_props, rels)

    def check_if_empty(self) -> bool:
        data = self.query(
            """
        MATCH (n)
        WITH count(n) as c
        RETURN CASE WHEN c > 0 THEN true ELSE false END AS output
        """
        )
        return data[0]["output"]
