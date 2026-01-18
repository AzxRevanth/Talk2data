from langchain_core.prompts import ChatPromptTemplate
import chromadb

from analytics_agent import analytics_agent
from dotenv import load_dotenv
import os
load_dotenv()

# LLM
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"

if USE_LOCAL_LLM:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="mistral", temperature=0.2)
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini")

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

In the end, mention the citations and metadata used to answer the question. If no citation or metadata is present, DONT mention anything, leave the answer as is. 
"""
)

# Router
DB_COLUMNS = {
    "age",
    "attrition",
    "businesstravel",
    "dailyrate",
    "department",
    "distancefromhome",
    "education",
    "educationfield",
    "employeecount",
    "employeenumber",
    "environmentsatisfaction",
    "gender",
    "hourlyrate",
    "jobinvolvement",
    "joblevel",
    "jobrole",
    "jobsatisfaction",
    "maritalstatus",
    "monthlyincome",
    "monthlyrate",
    "numcompaniesworked",
    "over18",
    "overtime",
    "percentsalaryhike",
    "performancerating",
    "relationshipsatisfaction",
    "standardhours",
    "stockoptionlevel",
    "totalworkingyears",
    "trainingtimeslastyear",
    "worklifebalance",
    "yearsatcompany",
    "yearsincurrentrole",
    "yearssincelastpromotion",
    "yearswithcurrmanager",
}

COLUMN_SYNONYMS = {
    "departments": "department",
    "dept": "department",
    "salary": "monthlyincome",
    "income": "monthlyincome",
    "role": "jobrole",
    "gender": "gender",
    "age": "age",
    "experience": "totalworkingyears",
    "years of experience": "totalworkingyears",
    "attrition rate": "attrition",
}

PLOT_KEYWORDS = {
    "plot",
    "graph",
    "chart",
    "visualize",
    "visualisation",
    "visualization",
    "draw",
    "show trend",
    "line chart",
    "bar chart",
    "pie chart",
}

def route_query(query: str) -> str:
    q = query.lower()
    
    # plot match
    if any(k in q for k in PLOT_KEYWORDS):
        return "analytics_plot"

    # direct column match
    for col in DB_COLUMNS:
        if col in q:
            return "analytics"

    # synonym match
    for syn in COLUMN_SYNONYMS:
        if syn in q:
            return "analytics"

    # explicit analytics intent
    if any(k in q for k in [
        "count", "average", "mean", "total",
        "distribution", "list", "unique",
        "how many", "percentage", "breakdown"
    ]):
        return "analytics"

    

    return "rag"



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
def answer_query(query: str):
    route = route_query(query)

    # 1. Analytics path (PandasAI / PostgreSQL)
    if route == "analytics":
        try:
            result = analytics_agent(query, False)
            return result["content"]
        except Exception as e:
            print(f"Analytics error: {e}")
            return "Unable to compute analytics from enterprise data."

    # 2. Plot Response
    if route == "analytics_plot":
        try:
            plot_result = analytics_agent(query, True)
            return plot_result
        except Exception as e:
            print(f"Plot error: {e}")
            return "Unable to generate plot from enterprise data."
    
    # 3. RAG path (policies / handbook)
    context = retrieval_tool(query)

    if not context:
        return "No relevant information found in enterprise data."

    response = llm.invoke(
        RETRIEVAL_PROMPT.format_messages(
            context=context,
            question=query
        )
    )

    return response.content





