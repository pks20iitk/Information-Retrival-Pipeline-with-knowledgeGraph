from typing import List, Union
from api.src.components.base_components import BaseComponent
from api.src.components.message_generator import SystemMessageGenerator, PromptGenerator
from api.src.llm.openai import OpenAIChat


class DataToCSV(BaseComponent):
    def __init__(self, csv_generator, runner: None) -> None:
        super().__init__(runner)
        self.csv_generator = csv_generator

    def execute(self, input_data: Union[str, List[float]]) -> str:
        try:
            if not input_data or not isinstance(input_data, list):
                return "No data"
            system_message = SystemMessageGenerator.system_message()
            prompt = PromptGenerator.generate_prompt(input_data)

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]

            csv_data = self.csv_generator.generate(messages)
            return csv_data
        except Exception as e:
            return "No data"


if __name__ == "__main__":
    # Example input data (replace with your actual data)
    example_input_data = ["item1", "item2", "item3"]

    # Example CSV generator (replace with your actual implementation)

    example_csv_generator = OpenAIChat(openai_api_key='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')

    # Example DataToCSV usage
    data_to_csv = DataToCSV(csv_generator=example_csv_generator, runner=None)
    result_csv_data = data_to_csv.execute(example_input_data)

    # Print the result
    print("Input Data:")
    print(example_input_data)
    print("\nResult CSV Data:")
    print(result_csv_data)
