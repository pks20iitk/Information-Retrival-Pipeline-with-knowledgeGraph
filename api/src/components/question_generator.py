from typing import Any, Dict, List
from api.src.components.message_generator import SystemMessageGenerator
from api.src.components.base_components import BaseComponent
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.basellm import BaseLLM
import re


def generate_questions(questions_string: str) -> List[str]:
    return [
        # remove number and dot from the beginning of the question
        re.sub(r"\A\d\.?\s*", "", question)
        for question in questions_string.split("\n")
    ]


class QuestionProposalGenerator(BaseComponent):
    def __init__(self, llm: BaseLLM, database: Neo4jDatabase,
                 system_message_generator: SystemMessageGenerator.get_system_message_for_questions(), runner) -> None:
        super().__init__(runner)
        self.llm = llm
        self.database = database
        self.system_message_generator = system_message_generator

    def get_system_message(self) -> str:
        return self.system_message_generator.generate(self.database.schema)

    def get_database_sample(self) -> List[Dict[str, Any]]:
        return self.database.query(
            """MATCH (n)
                WITH n
                WHERE rand() < 0.3
                RETURN apoc.map.removeKey(n, 'embedding') AS properties, LABELS(n) as labels
                LIMIT 5"""
        )

    def run(self, **kwargs) -> Dict[str, List[str]]:
        messages = [
            {"role": "system", "content": self.get_system_message()},
            {
                "role": "user",
                "content": f"""Please generate 5 questions about the content of the database. 
                Here is a sample of the database you can use when generating questions: {self.get_database_sample()}""",
            },
        ]

        questions_string = self.llm.generate(messages)
        questions = generate_questions(questions_string)

        return {"output": questions}