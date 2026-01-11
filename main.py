from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import chromadb
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os
load_dotenv()

# LLM
llm = ChatOpenAI(model="gpt-4.1-nano")

# LLM Prompt Template
system_prompt = """
    You are an enterprise knowledge assistant.
    Your job is to answer user questions using ONLY the information retrieved from the enterprise knowledge base.

    Rules:
    - You must use the retrieval tool whenever the answer depends on company data or policies.
    - You must NOT use outside knowledge or make assumptions.
    - Do NOT guess or assume.
    - If the required information is not found using the tools, say so clearly.
    - Do not mention internal tools, embeddings, or databases in your final answer.
    - Your final answer must be a concise, well structured summary written for a business user.
 
    You have access to multiple tools. You must choose the correct tool based on the user question.

    TOOLS AND WHEN TO USE THEM:

    1. Retrieval Tool (enterprise knowledge base)
    - Use this tool for:
    - Company policies
    - Employee handbook questions
    - Rules, procedures, benefits, conduct
    - Any question that requires understanding text documents
    - This tool performs semantic search over internal documents.
    - Your answers MUST be grounded only in retrieved content.

    2. SQL Database Tools
    - Use SQL tools ONLY for:
    - Counts, averages, totals
    - Grouped statistics (by department, role, etc.)
    - Simple factual queries over structured employee data
    - Use READ-ONLY SQL queries only.
    - NEVER modify data.
    - NEVER use INSERT, UPDATE, DELETE, DROP, or ALTER.
    - Prefer simple SELECT queries.
    - If a question requires numbers or aggregations, use SQL instead of the retrieval tool.

    Final answer rules:
    - Do not show reasoning steps
    - Do not quote large text blocks
    - Be clear and direct
    - If no relevant information is found, state that explicitly

    DECISION GUIDANCE:
    - Textual policy question → use Retrieval Tool
    - Numerical or analytical question → use SQL tools
    - Greeting or generic question → answer directly
    """

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("employee_data")

@tool
def retrieval_tool(query: str) -> str:
    """
    Search the enterprise knowledge base and return relevant information
    from company documents and databases.
    """
    results = collection.query(query_texts=[query], n_results=5)
    documents = results["documents"][0]
    if not documents:
        return "No relevant information found."
    metadatas = results["metadatas"][0]
    sources = set()
    for metadata in metadatas:
        if metadata.get("source") == "pdf":
            sources.add("Employee Handbook (PDF)")
        elif metadata.get("source") == "postgresql":
            sources.add("Employee Attrition Database (PostgreSQL)")

    citations = "\n".join([f"- {source}" for source in sources])
    
    retrieved_text = "\n".join(documents)
    if not retrieved_text:
        return "No relevant information found."
    return f"""{retrieved_text}

                Sources:
                {citations}
                """

# SQL Tool
host=os.getenv("PG_HOST")
database=os.getenv("PG_DB")
user=os.getenv("PG_USER")
password=os.getenv("PG_PASSWORD")
port=5432

db_uri = (
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
)

db = SQLDatabase.from_uri(db_uri)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = toolkit.get_tools()
all_tools = [retrieval_tool] + sql_tools

agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=all_tools
)

def answer_query(query):
    results = agent.invoke({"input": query})
    return results["output"]




