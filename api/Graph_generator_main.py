from langchain.document_loaders import PyPDFLoader
from api.KnowledgeGraph_Generation.neo4j_graph_connector import graph
from langchain.text_splitter import TokenTextSplitter
from langchain.chains import GraphCypherQAChain
from tqdm import tqdm
from api.KnowledgeGraph_Generation.knowledge_graph_processing_pipeline import extract_and_store_graph
from api.KnowledgeGraph_Generation.chat_openai_initializer import ChatOpenAIInitializer
# Assume `graph` and `ChatOpenAI` are initialized before this point
# For example, you might have something like:
# graph = initialize_graph()  # Your function to initialize the graph
# chat_openai = initialize_chat_openai()  # Your function to initialize ChatOpenAI

# Your provided code
loader = PyPDFLoader("sample_data/contract.pdf")
pages = loader.load_and_split()

# Read the wikipedia article
raw_documents = pages
# Define chunking strategy
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)

# Only take the first the raw_documents
documents = text_splitter.split_documents(raw_documents[115:])


for i, d in tqdm(enumerate(documents), total=len(documents)):
    extract_and_store_graph(d)

# Specify which node labels should be extracted by the LLM
allowed_nodes = ["Interest Rate", "Spread", "Benchmark", "LIBOR", "Index Floor"]

for i, d in tqdm(enumerate(documents), total=len(documents)):
    extract_and_store_graph(d, allowed_nodes)

# Query the knowledge graph in a RAG application
graph.refresh_schema()

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm= ChatOpenAIInitializer(openai_key="OPENAI_API_KEY").chat_openai,
    qa_llm=ChatOpenAIInitializer(openai_key="OPENAI_API_KEY").chat_openai,
    validate_cypher=True,  # Validate relationship directions
    verbose=True
)
cypher_chain.run("#Locate Tom Hanks for me?")
