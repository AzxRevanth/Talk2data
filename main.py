from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import chromadb
from langchain.agents import create_agent
from langchain.tools import tool

# LLM
llm = ChatOpenAI(model="gpt-4.1-nano")

# LLM Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
    """You are an enterprise knowledge assistant.
    Your job is to answer user questions using ONLY the information retrieved from the enterprise knowledge base.

    Rules:
    - You must use the retrieval tool whenever the answer depends on company data or policies.
    - You must not use outside knowledge or make assumptions.
    - If the retrieved context does not contain the answer, say clearly that the information is not available.
    - Do not mention internal tools, embeddings, or databases in your final answer.
    - Your final answer must be a concise, well structured summary written for a business user.
    """ ),

    ("system", 
    """You should reason step by step before answering.

    When needed, decide to call the retrieval tool to gather relevant information.

    After observing retrieved information:
    - Combine related points
    - Remove redundancy
    - Resolve conflicts if any
    - Produce a single coherent answer

    Only include information supported by the retrieved context.
    """ ),

    ("user", "{input}"),
    
    ("system",
    """
    Final answer rules:
    - Do not show reasoning steps
    - Do not quote large text blocks
    - Be clear and direct
    - If no relevant information is found, state that explicitly
    """
    )
])

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
system_prompt = prompt.format(input="{input}")

agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=[retrieval_tool, tools]
)

def answer_query(query):
    results = agent.invoke({"input": query})
    return results["output"]




