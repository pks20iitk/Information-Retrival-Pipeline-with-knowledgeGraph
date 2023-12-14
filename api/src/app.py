from http.client import HTTPException

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from typing import Dict, Union, Optional
import logging
import traceback
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.src.components.company_report import CompanyReport
from api.src.components.ConcreteDataDisambiguation import DataDisambiguation
from api.src.components.question_generator import QuestionProposalGenerator
from api.src.components.summarize_cypher_result import SummarizeCypherResult
from api.src.components.text2cypher import Text2Cypher, CypherGenerator
from api.src.components.unstructured_data_extractor import DataExtractor, DataExtractorWithSchema
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat
from api.src.utils.unstructured_data_utils import NodesTextConverter, RelationshipsTextConverter
from pydantic import BaseModel
from api.src.components.message_generator import SystemMessageGenerator
from api.src.fewshot_examples import get_fewshot_examples

database = Neo4jDatabase()
llm = OpenAIChat(openai_api_key='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')
openai_api_key = None



app = Flask(__name__)
CORS(app)


class Payload(BaseModel):
    question: str
    api_key: Optional[str]
    model_name: Optional[str]


class ImportPayload(BaseModel):
    input: str
    neo4j_schema: Optional[str]
    api_key: Optional[str]


class QuestionProposalPayload(BaseModel):
    api_key: Optional[str]


# Maximum number of records used in the context
HARD_LIMIT_CONTEXT_RECORDS = 10


@app.route("/questionProposalsForCurrentDb", methods=["POST"])
def question_proposals_for_current_db():
    data = request.json

    if not openai_api_key and not data.get('api_key'):
        return jsonify(
            {"error": "Please set OPENAI_API_KEY environment variable or send it as api_key in the request body"}), 422

    api_key = openai_api_key if openai_api_key else data.get('api_key')

    # Assuming QuestionProposalGenerator and OpenAIChat classes are defined elsewhere
    question_proposal_generator = QuestionProposalGenerator(
        database=database,
        llm=llm,
        system_message_generator=SystemMessageGenerator.get_system_message_for_questions(database))

    result = question_proposal_generator.run()
    return jsonify(result)


@app.route("/text2text", methods=["POST"])
def text2text():
    try:
        data = request.json
        if not openai_api_key and not data.get("api_key"):
            return jsonify({"error": "Please set OPENAI_API_KEY or provide api_key"}), 422

        api_key = openai_api_key if openai_api_key else data.get("api_key")

        default_llm = llm

        summarize_results = SummarizeCypherResult(
            llm=default_llm,
            exclude_embeddings=False,
            System=SystemMessageGenerator.system()
        )

        text2cypher = Text2Cypher(database=database, cypher_generator=CypherGenerator(llm=llm),
                                  cypher_examples=get_fewshot_examples(api_key), runner=None)

        if "type" not in data:
            return jsonify({"error": "Missing type"}), 400

        if data["type"] == "question":
            question = data["question"]
            chatHistory = [{"role": "user", "content": question}]
            # chatHistory = data['chat_history']
            results = None

            try:
                results = text2cypher.run(question, chatHistory)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

            if results is None:
                return jsonify({"error": "Could not generate Cypher statement"}), 500

            output = summarize_results.run(
                question, results["output"][:HARD_LIMIT_CONTEXT_RECORDS]
            )

            chatHistory.append({"role": "system", "content": output})

            return jsonify(
                {
                    "type": "end",
                    "output": output,
                    "generated_cypher": results["generated_cypher"],
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/data2cypher")
def root(payload: ImportPayload):
    """
    Takes an input and created a Cypher query
    """
    if not openai_api_key and not payload.api_key:
        raise HTTPException()
    api_key = openai_api_key if openai_api_key else payload.api_key

    try:
        result = ""

        llm = OpenAIChat(
            openai_api_key=api_key, model_name="gpt-3.5-turbo-16k", max_tokens=4000
        )

        if not payload.neo4j_schema:
            extractor = DataExtractor(llm=llm)
            result = extractor.run(data=payload.input)
        else:
            extractor = DataExtractorWithSchema(llm=llm)
            result = extractor.run(schema=payload.neo4j_schema, data=payload.input)

        print("Extracted result: " + str(result))

        disambiguation = DataDisambiguation(llm=llm)
        disambiguation_result = disambiguation.run(result)

        print("Disambiguation result " + str(disambiguation_result))

        return {"data": disambiguation_result}

    except Exception as e:
        print(e)
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(debug=True)
