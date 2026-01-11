# Talk2Data (v2)

Talk2Data is an enterprise-style AI assistant that allows users to query internal company knowledge using natural language.  
Version 1 focuses on Retrieval Augmented Generation (RAG) over unstructured and semi-structured enterprise data, delivered through a ChatGPT-like interface.

The project is designed to reflect how real internal knowledge assistants are built in organizations, with clear separation between ingestion, retrieval, reasoning, and user interaction.

---

## About the Project

**Version 2 builds on v1** and adds support for querying structured enterprise data while maintaining strict grounding and safety guarantees.

- Company policies
- Employee handbook
- Enterprise documentation
- Context grounded answers using RAG

---

## What’s New in v2

- SQL-based querying over structured enterprise data
- Multi-tool ReAct agent that decides between RAG and SQL tools
- Read-only SQL enforcement through prompt and tooling
- Improved error handling and environment configuration
- Stable database connectivity using environment variables
- Bug fixes across ingestion, retrieval, and UI layers

## Key Features

- ChatGPT-style conversational interface built with Streamlit
- Retrieval Augmented Generation (RAG) pipeline
- Semantic search over enterprise documents using ChromaDB
- Persistent vector storage for fast repeated queries
- Metadata-aware retrieval
- Grounded responses with clear source attribution
- Hallucination control through strict prompt rules

---

## Architecture Overview
  
![Designs(1)](https://github.com/user-attachments/assets/a4b46bbe-f90a-44cd-ae83-29dd6a2f8d3a)

- Raw documents remain the source of truth
- ChromaDB stores embeddings and metadata only
- The LLM never directly accesses documents or files
- Retrieval and SQL queries happen before generation
- Structured data and unstructured data are handled separately
- Fail safely when information is unavailable

---

## Tech Stack

- **Language**: Python
- **LLM**: OpenAI (ChatOpenAI)
- **Framework**: LangChain
- **Vector Database**: ChromaDB
- **Frontend**: Streamlit
- **Document Parsing**: PyPDF
- **Embeddings**: Sentence Transformers (via Chroma defaults)
- **Database**: PostgreSQL
- **ORM / DB Access**: SQLAlchemy

---

## Data Ingestion

### Unstructured Documents
- Employee Handbook PDF is converted to text
- Text is chunked for semantic search
- Chunks are embedded and stored in ChromaDB
- Metadata is attached for traceability

### Structured Data
- Employee data is stored in PostgreSQL
- Selected semantic fields are used for querying
- SQL remains the system of record

### Vector Storage
- ChromaDB is used in persistent mode
- Embeddings are reused across application restarts
- Ingestion is run once unless documents change

---

## How Retrieval Works

1. User submits a natural language question
2. The agent classifies the intent
3. The appropriate tool is selected:
   - Retrieval tool for policies and documents
   - SQL tools for numeric or analytical queries
4. Retrieved data is passed to the LLM
5. The LLM generates a concise, grounded response
6. Source information is included when applicable

---

## Running the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables 
Create a .env file in the project root:
```bash
PG_HOST=localhost
PG_DB=talk2data
PG_USER=postgres
PG_PASSWORD=your_password
PG_PORT=5432
```

### 3. Run ingestion 

```bash
python ingestion/ingestion.py
```
This step builds the vector database.

### 4. Run Application

```bash
streamlit run app.py
```
Open the local URL shown in the terminal.

---

## Limitations (v2) -> Future Improvements

- SQL results are returned as text (analytics and charts planned)
- No role-based access control yet
- No long-term conversational memory

---

## Disclaimer
This project uses sample and synthetic enterprise data for demonstration purposes.
It is intended for educational and portfolio use.
