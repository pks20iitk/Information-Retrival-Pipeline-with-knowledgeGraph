from langchain.graphs import Neo4jGraph

url = "neo4j+s://d34db895.databases.neo4j.io"
username = "neo4j"
password = "cq3bB8rRwzbCwAJHUQau9qkkHwkIWz6YMpYd6qxFIOs"
graph = Neo4jGraph(
    url=url,
    username=username,
    password=password
)
