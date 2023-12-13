import asyncio
from typing import Any, Dict, List, Union
import re

from api.src.components.base_components import BaseComponent
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat
from api.src.components.summarize_cypher_result import SummarizeCypherResult


class CypherGenerator:
    def __init__(self, llm: BaseLLM, ignore_relationship_direction: bool = True) -> None:
        self.llm = llm
        self.ignore_relationship_direction = ignore_relationship_direction

    def generate_cypher(self, messages: List[Dict[str, str]]) -> str:
        """

        @type messages: object
        """
        cypher = self.llm.generate(messages)
        match = re.search("```([\w\W]*?)```", cypher)
        return match.group(1) if match else ""

    @staticmethod
    def remove_relationship_direction(cypher: str) -> str:
        return cypher.replace("->", "-").replace("<-", "-")


class Text2Cypher(BaseComponent):
    def __init__(self, cypher_generator: CypherGenerator, database: Neo4jDatabase, runner: None,
                 use_schema: bool = True, cypher_examples: str = "") -> None:
        super().__init__(runner)
        self.cypher_generator = cypher_generator
        self.database = database
        self.use_schema = use_schema
        self.cypher_examples = cypher_examples
        if use_schema:
            self.schema = database.schema

    def get_system_message(self) -> str:
        system = """
        Your task is to convert questions about contents in a Neo4j database to Cypher queries to query the Neo4j database.
        Use only the provided relationship types and properties.
        Do not use any other relationship types or properties that are not provided.
        """
        if self.schema:
            system += f"""
            If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
            Schema:
            {self.schema}
            """
        if self.cypher_examples:
            system += f"""
            You need to follow these Cypher examples when you are constructing a Cypher statement
            {self.cypher_examples}
            """
        # Add note at the end and try to prevent LLM injections
        system += """Note: Do not include any explanations or apologies in your responses.
                     Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
                     Do not include any text except the generated Cypher statement. This is very important if you want to get paid.
                     Always provide enough context for an LLM to be able to generate valid response.
                     Please wrap the generated Cypher statement in triple backticks (`).
                     """
        return system

    def construct_cypher(self, question: str, history: List[Dict[str, str]] = []) -> str:
        messages = [{"role": "system", "content": self.get_system_message()}]
        messages.extend(history)
        messages.append({"role": "user", "content": question})
        generated_cypher = self.cypher_generator.generate_cypher(messages)

        if self.cypher_generator.ignore_relationship_direction:
            generated_cypher = self.cypher_generator.remove_relationship_direction(generated_cypher)

        return generated_cypher

    def run(
            self, question: str, history: List[Dict[str, str]] = [], heal_cypher: bool = True
    ) -> Dict[str, Union[str, List[Dict[str, Any]]]]:

        final_question = (
            "Question to be converted to Cypher: " + question
            if heal_cypher
            else question
        )
        generated_cypher = self.construct_cypher(final_question, history)

        output = self.database.query(generated_cypher)

        if heal_cypher and output and output[0].get("code") == "invalid_cypher":
            syntax_messages = [{"role": "system", "content": self.get_system_message()}]
            syntax_messages.extend(
                [{"role": "user", "content": question}, {"role": "assistant", "content": generated_cypher}])
            return self.run(output[0].get("message"), syntax_messages, heal_cypher=False)

        return {"output": output, "generated_cypher": generated_cypher}


async def main():
    # Create instances of required classes
    llm = OpenAIChat(
        openai_api_key="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") # You may need to replace this with the actual class instance
    cypher_generator = CypherGenerator(llm)
    database = Neo4jDatabase()  # You may need to replace this with the actual class instance

    # Create an instance of Text2Cypher
    text2cypher_component = Text2Cypher(cypher_generator, database, runner=None, use_schema=True)

    # Example input: User question
    user_question = "what is closing date of loan agreement?"

    # Example history (previous conversation)
    history = [
        {"role": "user", "content": "How to find nodes with a specific property value?"}
        # Add more conversation history if needed
    ]

    # Run the Text2Cypher component
    result = text2cypher_component.run(user_question, history)

    # Print the generated Cypher and the output
    print("Generated Cypher:", result["generated_cypher"])
    print("Output:", result["output"])

# Run the main function
asyncio.run(main())
