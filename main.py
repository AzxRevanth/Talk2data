from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import chromadb
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os
load_dotenv()

# LLM
USE_LOCAL_LLM = True

if USE_LOCAL_LLM:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="mistral", temperature=0.2)
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4.1-nano")

# PROMPTS

RETRIEVAL_PROMPT = ChatPromptTemplate.from_template(
    """
You are an enterprise knowledge assistant.

Answer the question using ONLY the retrieved enterprise content below.
Do NOT use outside knowledge or assumptions.

- You must use the retrieval tool whenever the answer depends on company data or policies.
- You must NOT use outside knowledge or make assumptions.
- Do NOT guess or assume.
- If the required information is not found using the tools, say so clearly.
- Do not mention internal tools, embeddings, or databases in your final answer.
- Your final answer must be a concise, well structured summary written for a business user.

If the content does not contain the answer, respond with:
"No relevant information found in enterprise data."

Retrieved Content:
{context}

Question:
{question}
"""
)

SQL_GENERATION_PROMPT = ChatPromptTemplate.from_template(
    """
You are an enterprise data analyst.

Generate a READ ONLY SQL query to answer the question.
Rules:
- SELECT statements only
- No data modification
- Use existing tables only
- Do not add explanations
- NEVER modify data.
- NEVER use INSERT, UPDATE, DELETE, DROP, or ALTER.

Question:
{question}
"""
)

SQL_ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """
You are an enterprise knowledge assistant.

Answer the question using ONLY the SQL results below.
Do not infer or guess anything beyond the data.

SQL Result:
{result}

Question:
{question}
"""
)

# Router
def is_sql_question(query: str) -> bool:
    sql_keywords = [
        "count", "how many", "average", "avg",
        "total", "sum", "percentage", "number of"
    ]
    return any(k in query.lower() for k in sql_keywords)


# Load SQL
host=os.getenv("PG_HOST")
database=os.getenv("PG_DB")
user=os.getenv("PG_USER")
password=os.getenv("PG_PASSWORD")
port=5432

db_uri = (
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:"
    f"{os.getenv('PG_PASSWORD')}@"
    f"{os.getenv('PG_HOST')}:5432/"
    f"{os.getenv('PG_DB')}"
)

db = SQLDatabase.from_uri(db_uri)
sql_tool = QuerySQLDataBaseTool(db=db)

client = chromadb.PersistentClient(path="./ingestion/chroma_db")
collection = client.get_collection("employee_data")


def retrieval_tool(query: str) -> str:
    results = collection.query(query_texts=[query], n_results=5)
    documents = results["documents"][0]

    if not documents:
        return ""

    metadatas = results["metadatas"][0]
    sources = set()

    for metadata in metadatas:
        if metadata.get("source") == "pdf":
            sources.add("Employee Handbook (PDF)")
        elif metadata.get("source") == "postgresql":
            sources.add("Employee Attrition Database (PostgreSQL)")

    retrieved_text = "\n".join(documents)
    if not retrieved_text:
        return ""

    citations = "\n".join(f"- {s}" for s in sources)

    return f"""{retrieved_text}

Sources:
{citations}
"""


# Final Answer

def answer_query(query):
    # ---------- SQL PATH ----------
    if is_sql_question(query):

        sql_query = llm.invoke(
            SQL_GENERATION_PROMPT.format_messages(question=query)
        ).content.strip()

        if not sql_query.lower().startswith("select"):
            return "Unable to retrieve numerical data for this query."

        sql_result = sql_tool.invoke(sql_query)

        return llm.invoke(
            SQL_ANSWER_PROMPT.format_messages(
                result=sql_result,
                question=query
            )
        ).content

    # ---------- RETRIEVAL PATH ----------
    context = retrieval_tool(query)

    if not context:
        return "No relevant information found in enterprise data."

    return llm.invoke(
        RETRIEVAL_PROMPT.format_messages(
            context=context,
            question=query
        )
    ).content




