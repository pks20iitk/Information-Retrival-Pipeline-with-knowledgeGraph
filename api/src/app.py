import os
from flask import Flask, request, jsonify
from flask_cors import CORS
# from api.src.components.company_report import CompanyReport
from api.src.components.ConcreteDataDisambiguation import DataDisambiguation
from api.src.components.question_generator import QuestionProposalGenerator
# from api.src.components.summarize_cypher_result import SummarizeCypherResult
# from api.src.components.text2cypher import Text2Cypher
from api.src.components.unstructured_data_extractor import DataExtractor, DataExtractorWithSchema
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.openai import OpenAIChat

app = Flask(__name__)
CORS(app)

HARD_LIMIT_CONTEXT_RECORDS = 10

neo4j_connection = Neo4jDatabase(
    host=os.environ.get("NEO4J_URL", "neo4j+s://demo.neo4jlabs.com"),
    user=os.environ.get("NEO4J_USER", "companies"),
    password=os.environ.get("NEO4J_PASS", "companies"),
    database=os.environ.get("NEO4J_DATABASE", "companies"),
)

openai_api_key = os.environ.get("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", None)

@app.route("/questionProposalsForCurrentDb", methods=["POST"])
def question_proposals_for_current_db():
    payload = request.json
    if not openai_api_key and not payload.get("api_key"):
        return jsonify({"error": "Please set OPENAI_API_KEY environment variable or send it as api_key in the request body"}), 422

    api_key = openai_api_key if openai_api_key else payload.get("api_key")
    questionProposalGenerator = QuestionProposalGenerator(
        database=neo4j_connection,
        llm=OpenAIChat(
            openai_api_key=api_key,
            model_name="gpt-3.5-turbo-0613",
            max_tokens=512,
            temperature=0.8,
        ),
    )

    return jsonify(questionProposalGenerator.run())

@app.route("/hasapikey", methods=["GET"])
def has_api_key():
    return jsonify({"output": openai_api_key is not None})

@app.route("/text2text", methods=["WEBSOCKET"])
def websocket_endpoint():
    # WebSocket functionality goes here...
    pass

@app.route("/data2cypher", methods=["POST"])
def data_to_cypher():
    payload = request.json
    if not openai_api_key and not payload.get("api_key"):
        return jsonify({"error": "Please set OPENAI_API_KEY environment variable or send it as api_key in the request body"}), 422

    api_key = openai_api_key if openai_api_key else payload.get("api_key")

    try:
        result = ""
        llm = OpenAIChat(
            openai_api_key=api_key, model_name="gpt-3.5-turbo-16k", max_tokens=4000
        )

        if not payload.get("neo4j_schema"):
            extractor = DataExtractor(llm=llm)
            result = extractor.run(data=payload.get("input"))
        else:
            extractor = DataExtractorWithSchema(llm=llm)
            result = extractor.run(schema=payload.get("neo4j_schema"), data=payload.get("input"))

        print("Extracted result: " + str(result))

        disambiguation = DataDisambiguation(llm=llm)
        disambiguation_result = disambiguation.run(result)

        print("Disambiguation result " + str(disambiguation_result))

        return jsonify({"data": disambiguation_result})

    except Exception as e:
        print(e)
        return jsonify({"error": f"Error: {e}"}), 500

@app.route("/companyReport", methods=["POST"])
def company_report():
    payload = request.json
    if not openai_api_key and not payload.get("api_key"):
        return jsonify({"error": "Please set OPENAI_API_KEY environment variable or send it as api_key in the request body"}), 422

    api_key = openai_api_key if openai_api_key else payload.get("api_key")

    llm = OpenAIChat(
        openai_api_key=api_key,
        model_name="gpt-3.5-turbo-16k-0613",
        max_tokens=512,
    )
    print("Running company report for " + payload.get("company"))
    company_report = CompanyReport(neo4j_connection, payload.get("company"), llm)
    result = company_report.run()

    return jsonify({"output": result})

@app.route("/companyReport/list", methods=["POST"])
def company_report_list():
    company_data = neo4j_connection.query(
        "MATCH (n:Organization) WITH n WHERE rand() < 0.01 return n.name LIMIT 5",
    )

    return jsonify({"output": [x["n.name"] for x in company_data]})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/ready", methods=["GET"])
def readiness_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 7860)), host="0.0.0.0")
