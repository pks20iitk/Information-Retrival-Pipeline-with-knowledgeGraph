# Extraction with KnowledgeGraph 
This repository is created to extract information  using Knowledge graph and using LLM GPT-3, GPT-3.5, GPT-4 and LangChain 

Repository Structure
Our repository is designed with an efficient and logical structure for ease of navigation:

Backend Code: The backend code is found in the api folder in the main.py file you can find all endpoints and their corresponding functions. All LLM functionality is split into different components which have thier own purpose.


Running the Demos
To simplify the process of running the demos, we have incorporated scripts that generate Docker images. To use these, you'll need to:

Navigate into the root directory.
Create an env file. You can use the env.example file as a template.


backend: localhost:7860/5000



Demo database
There is a demo databasing running on demo.neo4jlabs.com. This database Contains information about movies, actors,actress, directors and other related to movies.

Bring your own database
To run the project on your own database, follow these two steps:

Set appropriate database credentials in .env file
Remove or set appropriate Cypher examples in api/fewshot_examples.py file
Contributing
We welcome contributions and feedback to improve our project and demonstrations. Please feel free to raise issues or submit pull requests.

## Work is still in progress.......
