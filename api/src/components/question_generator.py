from typing import Any, Dict, List, Optional
from api.src.components.message_generator import SystemMessageGenerator
from api.src.components.base_components import BaseComponent
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat
import re


def generate_questions(questions_string: Optional[str]) -> List[str]:
    """
    Generate a list of questions from a string.

    Args:
        questions_string: The string containing the questions.

    Returns:
        A list of questions with the number and dot removed from the beginning.

    """
    if questions_string is None or not isinstance(questions_string, str):
        return []

    pattern = re.compile(r"\A\d\.?\s*")
    return [
        pattern.sub("", question)
        for question in questions_string.splitlines()
        if question.strip() != "" and re.match(r"\A\d\.", question)
    ]


class QuestionProposalGenerator(BaseComponent):
    def __init__(self, llm: BaseLLM, database: Neo4jDatabase,
                 system_message_generator: SystemMessageGenerator.get_system_message_for_questions(), runner: None) -> None:

        super().__init__(runner)
        self.llm = llm
        self.database = database
        self.system_message_generator = system_message_generator

    def get_system_message(self) -> str:
        return SystemMessageGenerator.get_system_message_for_questions(self.database)

    def get_database_sample(self) -> List[Dict[str, Any]]:
        query = """
            MATCH (n)
            WITH n
            WHERE rand() < $random_value
            RETURN apoc.map.removeKey(n, 'embedding') AS properties, LABELS(n) as labels
            LIMIT $limit_value
        """
        params = {"random_value": 0.3, "limit_value": 5}
        return self.database.query(query, params)

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


if __name__ == "__main__":
    # Example llm, database, and system_message_generator (replace with your actual implementations)

    example_llm = OpenAIChat(openai_api_key='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')
    example_database = Neo4jDatabase()
    example_system_message_generator = SystemMessageGenerator.get_system_message_for_questions(database=example_database)

    # Example QuestionProposalGenerator usage
    question_proposal_generator = QuestionProposalGenerator(
        llm=example_llm,
        database=example_database,
        system_message_generator=example_system_message_generator,
        runner=None
    )
    result = question_proposal_generator.run()

    # Print the result
    print("Generated Questions:")
    print(result["output"])
