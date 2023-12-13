from typing import List

from api.src.components.base_components import BaseComponent


class SystemMessageGenerator:
    @staticmethod
    def generate_system_message() -> str:
        return """
You will be given a dataset of nodes and relationships. Your task is to convert this data into a CSV format.
Return only the data in the CSV format and nothing else. Return a CSV file for every type of node and relationship.
The data you will be given is in the form [ENTITY, TYPE, PROPERTIES] and a set of relationships in the form [ENTITY1, RELATIONSHIP, ENTITY2, PROPERTIES].
Important: If you don't get any data or data that does not follow the previously mentioned format return "No data" and nothing else. This is very important. If you don't follow this instruction you will get a 0.
"""


class PromptGenerator:
    @staticmethod
    def generate_prompt(data) -> str:
        return f""" Here is the data:
{data}
"""


class DataToCSV(BaseComponent):
    def __init__(self, llm) -> None:
        self.llm = llm

    def run(self, data: List[str]) -> str:
        system_message = SystemMessageGenerator.generate_system_message()
        prompt = PromptGenerator.generate_prompt(data)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        output = self.llm.generate(messages)
        return output
