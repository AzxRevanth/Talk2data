# Talk2Data (v3)

Talk2Data is an enterprise-style AI assistant that allows users to query internal company knowledge using natural language. 
It combines Retrieval Augmented Generation (RAG), SQL-based analytics, and visualization in a ChatGPT-like interface.

This project is designed to reflect how real-world internal AI assistants are architected in organizations.

The system is built with a modular architecture, separating ingestion, retrieval, reasoning, analytics, and the user interface to ensure reliability, scalability, and grounded responses. It combines document retrieval, structured data querying, and analytics in a single ChatGPT-like interface, reflecting how real internal AI assistants are designed in production environments.

---

## What’s New in v3
Version 3 introduces a natural language analytics module that allows users to ask analytical questions and generate visual insights directly from structured enterprise data.

New additions include:

- Natural Language Queries (NLQ) over PostgreSQL data
- Automated analytics using PandasAI on Pandas DataFrames
- On-demand visualizations rendered directly in the Streamlit UI
- Intelligent schema based routing between document retrieval, SQL analytics, and plotting
- Improved stability and error handling for long-running analytical tasks
- Bug fixes across ingestion, retrieval, and UI layers
- Featuring both a hosted (OpenAI) mode and Local (Ollama) Mode.

## Key Features

- ChatGPT-style conversational interface built with Streamlit
- Retrieval Augmented Generation (RAG) pipeline for enterprise knowledge access
- Semantic search over internal documents using ChromaDB
- Metadata-aware retrieval with source tracking
- Hallucination control through strict prompt and routing rules
- Intelligent query routing between document retrieval and analytics workflows
- Natural Language Queries (NLQ) over structured PostgreSQL data
- Automated analytics using PandasAI on Pandas DataFrames
- On-demand data visualizations rendered directly in the UI
- Support for both local (Ollama) and hosted (OpenAI) LLMs
- Modular architecture separating ingestion, retrieval, reasoning, analytics, and UI
- Safe, read-only data access for analytical queries
- Robust error handling and graceful fallbacks when data is unavailable

---

## Architecture Overview & App Images

![Designs](https://github.com/user-attachments/assets/e668d1f1-09d7-49cf-8687-a8d06a3a31ab)

<img width="1600" height="899" alt="image" src="https://github.com/user-attachments/assets/f93484ab-b4c6-4368-b7fd-38156b322b1c" />

<img width="1600" height="899" alt="image" src="https://github.com/user-attachments/assets/0866ce2c-5a2e-48ec-b2f3-4290d20ed880" />

<img width="1600" height="899" alt="image" src="https://github.com/user-attachments/assets/c11cf459-aebf-4160-b0b7-958a225fc366" />

---

## Tech Stack

- **Language**: Python  
- **LLMs**: OpenAI (ChatOpenAI), Local LLMs via Ollama  
- **Agent Framework**: LangChain   
- **Vector Database**: ChromaDB 
- **Embeddings**: Sentence Transformers  
- **Frontend**: Streamlit  
- **Document Parsing**: PyPDF  
- **Analytics & NLQ**: PandasAI   
- **Data Visualization**: Plotly  
- **Database**: PostgreSQL  
- **Database Access**: SQLAlchemy 
- **Configuration Management**: Python-dotenv  
- **Local Model Serving**: Ollama

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

1. User submits a natural language query through the chat interface  
2. A query router classifies the intent (document lookup, analytics, or visualization)  
3. The appropriate execution path is selected:
   - Retrieval pipeline for policies and unstructured documents  
   - SQL and analytics pipeline for structured data queries  
   - Visualization pipeline for plot and trend requests  
4. For document queries, relevant chunks are retrieved from ChromaDB using semantic similarity  
5. For analytical queries, structured data is fetched from PostgreSQL and processed as a Pandas DataFrame  
6. Natural language analytics and aggregations are performed when required  
7. Visualizations are generated and rendered directly in the UI for plot requests  
8. Retrieved or computed results are passed to the LLM for summarization when needed  
9. The system returns a grounded response with source attribution or visual output as applicable  

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

## Disclaimer
This project uses sample and synthetic enterprise data for demonstration purposes.
It is intended for educational and portfolio use.
