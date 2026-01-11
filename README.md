# Talk2Data (v1)

Talk2Data is an enterprise-style AI assistant that allows users to query internal company knowledge using natural language.  
Version 1 focuses on Retrieval Augmented Generation (RAG) over unstructured and semi-structured enterprise data, delivered through a ChatGPT-like interface.

The project is designed to reflect how real internal knowledge assistants are built in organizations, with clear separation between ingestion, retrieval, reasoning, and user interaction.

---

## About the Project

**Version 1 intentionally focuses only on knowledge retrieval.**

- Company policies
- Employee handbook
- Enterprise documentation
- Context grounded answers using RAG

---

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
  
![Designs](https://github.com/user-attachments/assets/ef1d65ce-be52-40f1-8111-b970034f8c25)

- Raw documents remain the source of truth
- ChromaDB stores embeddings and metadata only
- The LLM never directly accesses documents or files

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


---

## Data Ingestion

### Unstructured Documents
- Employee Handbook PDF is converted to text
- Text is chunked for semantic search
- Chunks are embedded and stored in ChromaDB
- Metadata is attached for traceability

### Vector Storage
- ChromaDB is used in persistent mode
- Embeddings are reused across application restarts
- Ingestion is run once unless documents change

---

## How Retrieval Works

1. User submits a question
2. The agent determines if retrieval is required
3. Relevant document chunks are fetched using semantic similarity
4. Retrieved content is passed to the LLM
5. The LLM generates a grounded answer
6. Source information is included in the response

---

## Running the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run ingestion 

```bash
python ingestion/ingestion.py
```
This step builds the vector database.

### 3. Run Application

```bash
streamlit run app.py
```
Open the local URL shown in the terminal.

---

## Disclaimer
This project uses sample and synthetic enterprise data for demonstration purposes.
It is intended for educational and portfolio use.
