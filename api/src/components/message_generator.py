class SystemMessageGenerator:


    @staticmethod
    def system() -> str:
        return f""" You are an assistant that helps to generate text to form nice and human understandable answers 
        based. The latest prompt contains the information, and you need to generate a human readable response based 
        on the given information. Make the answer sound as a response to the question. Do not mention that you based 
        the result on the given information. Do not add any additional information that is not explicitly provided in 
        the latest prompt. I repeat, do not add any information that is not explicitly given. Make the answer as 
        concise as possible and do not use more than 50 words."""


    @staticmethod
    def system_message() -> str:
        return """You will be given a dataset of nodes and relationships. Your task is to convert this data into a 
        CSV format. Return only the data in the CSV format and nothing else. Return a CSV file for every type of node 
        and relationship. The data you will be given is in the form [ENTITY, TYPE, PROPERTIES] and a set of 
        relationships in the form [ENTITY1, RELATIONSHIP, ENTITY2, PROPERTIES]. Important: If you don't get any data 
        or data that does not follow the previously mentioned format return "No data" and nothing else. This is very 
        important. If you don't follow this instruction you will get a 0."""

    @staticmethod
    def generate_system_message() -> str:
        return """You are a data scientist working for a company that is building a graph database. Your task is to 
        extract information from data and convert it into a graph database. Provide a set of Nodes in the form [
        ENTITY_ID, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, 
        PROPERTIES]. It is important that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID. 
        If you can't pair a relationship with a pair of nodes don't add it. When you find a node or relationship you 
        want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a label.

    Example: Data: Alice lawyer and is 25 years old and Bob is her roommate since 2001. Bob works as a journalist. 
    Alice owns a the webpage www.alice.com and Bob owns the webpage www.bob.com. Nodes: ["alice", "Person", 
    {"age": 25, "occupation": "lawyer", "name":"Alice"}], ["bob", "Person", {"occupation": "journalist", 
    "name": "Bob"}], ["alice.com", "Webpage", {"url": "www.alice.com"}], ["bob.com", "Webpage", 
    {"url": "www.bob.com"}] Relationships: ["alice", "roommate", "bob", {"start": 2021}], ["alice", "owns", 
    "alice.com", {}], ["bob", "owns", "bob.com", {}]"""

    @staticmethod
    def generate_system_message_with_labels() -> str:
        return """You are a data scientist working for a company that is building a graph database. Your task is to 
        extract information from data and convert it into a graph database. Provide a set of Nodes in the form [
        ENTITY_ID, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, 
        PROPERTIES]. It is important that the ENTITY_ID_1 and ENTITY_ID_2 exists as nodes with a matching ENTITY_ID. 
        If you can't pair a relationship with a pair of nodes don't add it. When you find a node or relationship you 
        want to add try to create a generic TYPE for it that  describes the entity you can also think of it as a 
        label. You will be given a list of types that you should try to use when creating the TYPE for a node. If you 
        can't find a type that fits the node you can create a new one.

    Example: Data: Alice lawyer and is 25 years old and Bob is her roommate since 2001. Bob works as a journalist. 
    Alice owns a the webpage www.alice.com and Bob owns the webpage www.bob.com. Types: ["Person", "Webpage"] Nodes: 
    ["alice", "Person", {"age": 25, "occupation": "lawyer", "name":"Alice"}], ["bob", "Person", {"occupation": 
    "journalist", "name": "Bob"}], ["alice.com", "Webpage", {"url": "www.alice.com"}], ["bob.com", "Webpage", 
    {"url": "www.bob.com"}] Relationships: ["alice", "roommate", "bob", {"start": 2021}], ["alice", "owns", 
    "alice.com", {}], ["bob", "owns", "bob.com", {}]"""

    @staticmethod
    def generate_system_message_with_schema() -> str:
        return """You are a data scientist working for a company that is building a graph database. Your task is to 
        extract information from data and convert it into a graph database. Provide a set of Nodes in the form [
        ENTITY, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY1, RELATIONSHIP, ENTITY2, 
        PROPERTIES]. Pay attention to the type of the properties, if you can't find data for a property set it to 
        null. Don't make anything up and don't add any extra data. If you can't find any data for a node or 
        relationship don't add it. Only add nodes and relationships that are part of the schema. If you don't get any 
        relationships in the schema only add nodes.

    Example:
    Schema: Nodes: [Person {age: integer, name: string}] Relationships: [Person, roommate, Person]
    Alice is 25 years old and Bob is her roommate.
    Nodes: [["Alice", "Person", {"age": 25, "name": "Alice}], ["Bob", "Person", {"name": "Bob"}]]
    Relationships: [["Alice", "roommate", "Bob"]]
    """

    @staticmethod
    def get_system_message_for_questions(database=None) -> str:
        if database is None:
            return "No database provided"

        try:
            schema = database.schema
        except Exception as e:
            schema = "Error accessing schema: " + str(e)

        system = f''' Your task is to come up with questions someone might as about the content of a Neo4j database. 
            Try to make the questions as different as possible. The questions should be separated by a new line and each 
            line should only contain one question. To do this, you need to understand the schema of the database. 
            Therefore it's very important that you read the schema carefully. You can find the schema below. Schema: 
    {schema}
            '''

        return system


class PromptGenerator:
    @staticmethod
    def generate(data, schema=None, labels=None) -> str:
        if schema:
            return f"Schema: {schema}\nData: {data}"
        elif labels:
            return f"Data: {data}\nTypes: {labels}"
        else:
            return f"Data: {data}"

    @staticmethod
    def generate_prompt(data) -> str:
        return f""" Here is the data:
    {data} """
