import logging
from api.src.components.base_components import BaseComponent
from api.src.components.summarize_cypher_result import SummarizeCypherResult
from api.src.driver.Neo4j import Neo4jDatabase
from api.src.llm.basellm import BaseLLM
from api.src.llm.openai import OpenAIChat
from api.src.components.message_generator import SystemMessageGenerator

HARD_LIMIT_CONTEXT_RECORDS = 10


class CompanyReport(BaseComponent):
    def __init__(self, database: Neo4jDatabase, company: str, llm: BaseLLM, runner: None) -> None:
        super().__init__(runner)
        self.database = database
        self.validate_company(company)
        self.company = company
        self.llm = llm
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def validate_company(company: str) -> None:
        if not company:
            raise ValueError("Invalid company name")

    def run(self):
        summarize_results = SummarizeCypherResult(
            llm=self.llm,
            System=SystemMessageGenerator.system()
        )
        self.logger.info("CompanyReport")
        company_data = self.database.query(
            "MATCH (n {name:$companyName}) return n.summary, n.isDissolved, n.nbrEmployees, n.name, n.motto, "
            "n.isPublic, n.revenue",
            {"companyName": self.company},
        )
        self.logger.info(company_data)
        relation_data = self.database.query(
            "MATCH (n {name:$companyName})-[r]->(m) WHERE NOT m:Article OPTIONAL MATCH (m)-[:IN_COUNTRY]->("
            "c:Country)"
            "WITH r,m,c return r,m,c",
            {"companyName": self.company},
        )
        self.logger.info(relation_data)
        if company_data and company_data[0]:
            company_data_output = {
                "name": company_data[0].get("n.name", None),
                "motto": company_data[0].get("n.motto", None),
                "summary": company_data[0].get("n.summary", None),
                "isDissolved": company_data[0].get("n.isDissolved", None),
                "nbrEmployees": company_data[0].get("n.nbrEmployees", None),
                "isPublic": company_data[0].get("n.isPublic", None),
                "revenue": company_data[0].get("n.revenue", None),
            }

            # or set default values or take appropriate action

            self.logger.info("all data fetched")
            offices = []
            suppliers = []
            subsidiaries = []
            for relation in relation_data:
                self.logger.info(relation)
                relation_type = relation["r"][1]
                if relation_type == "IN_CITY":
                    offices.append(
                        {
                            "city": relation["m"].get("name", None),
                            "country": relation.get("c")
                                       and relation["c"].get("name", None),
                        }
                    )
                elif relation_type == "HAS_CATEGORY":
                    company_data_output["industry"] = relation["m"]["name"]
                elif relation_type == "HAS_SUPPLIER":
                    category_result = self.database.query(
                        "MATCH (n {name:$companyName})-[HAS_CATEGORY]-(c:IndustryCategory) return c.name LIMIT 1",
                        {"companyName": relation["m"].get("name", None)},
                    )
                    category = None
                    if len(category_result) > 0:
                        category = category_result[0]["c.name"]

                    suppliers.append(
                        {
                            "summary": relation["m"].get("summary", None),
                            "revenue": relation["m"].get("revenue", None),
                            "isDissolved": relation["m"].get("isDissolved", None),
                            "name": relation["m"].get("name", None),
                            "isPublic": relation["m"].get("isPublic", None),
                            "category": category,
                        }
                    )
                elif relation_type == "HAS_SUBSIDIARY":
                    category_result = self.database.query(
                        "MATCH (n {name:$companyName})-[HAS_CATEGORY]-(c:IndustryCategory) return c.name LIMIT 1",
                        {"companyName": relation["m"].get("name", None)},
                    )
                    category = None
                    if len(category_result) > 0:
                        category = category_result[0]["c.name"]
                    article_data = self.database.query(
                        "MATCH p=(n {name:$companyName})<-[:MENTIONS]-(a:Article)-[:HAS_CHUNK]->(c:Chunk) return  "
                        "c.text,"
                        "a.title, a.siteName",
                        {"companyName": relation["m"].get("name", None)},
                    )
                    self.logger.info("Article data: " + str(article_data))

                    output = "There is not articles about this company."
                    if len(article_data) > 0:
                        output = summarize_results.run(
                            "Can you summarize the following articles in 50 words about "
                            + relation["m"].get("name", None)
                            + " ?",
                            article_data[:HARD_LIMIT_CONTEXT_RECORDS],
                        )
                    subsidiaries.append(
                        {
                            "summary": relation["m"].get("summary", None),
                            "revenue": relation["m"].get("revenue", None),
                            "isDissolved": relation["m"].get("isDissolved", None),
                            "name": relation["m"].get("name", None),
                            "isPublic": relation["m"].get("isPublic", None),
                            "category": category,
                            "articleSummary": output,
                        }
                    )
                elif relation_type == "HAS_CEO":
                    company_data_output["ceo"] = relation["m"]["name"]
            company_data_output["offices"] = offices
            article_data = self.database.query(
                "MATCH p=(n {name:$companyName})<-[:MENTIONS]-(a:Article)-[:HAS_CHUNK]->(c:Chunk) return  c.text, "
                "a.title, a.siteName",
                {"companyName": self.company},
            )

            output = summarize_results.run(
                "Can you summarize the following articles about " + self.company + " ?",
                article_data[:HARD_LIMIT_CONTEXT_RECORDS],
            )
            self.logger.info("output: " + output)
            return {
                "company": company_data_output,
                "subsidiaries": subsidiaries,
                "suppliers": suppliers,
                "articleSummary": output,
            }

        else:
            company_data_output = None
        return company_data_output


if __name__ == "__main__":
    neo4j_connection = Neo4jDatabase()
    # openai_api_key = "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"  # Replace with your actual OpenAI API key
    llm = BaseLLM  # You might need to adjust the initialization based on your BaseLLM class

    # Example input for testing
    input_data = {"company": "YourCompany"}

    # Instantiate the CompanyReport class
    company_report = CompanyReport(
        database=neo4j_connection,
        company=input_data["company"],
        llm=llm,
        runner=None
    )

    # Execute the run method
    result = company_report.run()

    # Print the result for debugging

