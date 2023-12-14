from abc import ABC, abstractmethod
from typing import List, Union
from asyncio import create_task, gather, run  # Import the 'run' function


class Runner(ABC):
    @abstractmethod
    def run(self, input_data: Union[str, List[float]]) -> str:
        """
        Run the specified task with the given input data.

        Args:
            input_data (Union[str, List[float]]): The input data for the task.

        Returns:
            str: The result of the task execution.
        """
        pass


class SynchronousRunner(Runner):
    """
    A class that runs tasks synchronously.

    This class provides a synchronous implementation of the Runner interface.
    It executes tasks one at a time, waiting for each task to complete before
    moving on to the next one.

    Args:
        Runner (ABC): The abstract base class for runners.

    Methods:
        run: Run the specified task with the given input data.

    Attributes:
        None
    """

    def run(self, input_data: Union[str, List[float]]) -> str:
        # Synchronous implementation here
        pass


class AsynchronousRunner(Runner):
    """
    A class for running tasks asynchronously.
    """

    async def run(self, input_data: Union[str, List[float]]) -> str:
        # Asynchronous implementation here
        pass


class BaseComponent(ABC):
    def __init__(self, runner):
        self.runner = runner

    def execute(self, input_data: Union[str, List[float]]) -> str:
        try:
            return self.runner.run(input_data)
        except Exception as e:
            return str(e)


class DataConverter(ABC):
    @abstractmethod
    def text_to_list_of_dict(self, text: str) -> List[dict]:
        """
        Convert text to a list of dictionaries.

        Args:
            text (str): The input text to be converted.

        Returns:
            List[dict]: The converted list of dictionaries.
        """
        pass


# Example usage:
if __name__ == "__main__":
    synchronous_runner = SynchronousRunner()
    synchronous_component = BaseComponent(synchronous_runner)
    result_sync = synchronous_component.execute([1.3, 4.5, 6.7])

    asynchronous_runner = AsynchronousRunner()
    asynchronous_component = BaseComponent(asynchronous_runner)
    result_async = asynchronous_component.execute("My name is Prince K singh")


    # For running multiple asynchronous components concurrently
    async def run_async_components(components: List[BaseComponent], input_data: Union[str, List[float]]):
        tasks = [create_task(component.runner.run(input_data)) for component in components]
        results = await gather(*tasks)
        return results


    # Example usage for running multiple asynchronous components concurrently
    async def main():
        results = await run_async_components([asynchronous_component], "input data")
        print(results)


    # Run the asynchronous main function
    run(main())
