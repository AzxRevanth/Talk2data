import psycopg2
import pandas as pd
import numpy as np
import os 
import chromadb

from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DB"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    port=5432
)

query = "SELECT employeenumber, department, educationfield, gender, jobrole, performancerating FROM employee_attrition"
df = pd.read_sql(query, conn)

conn.close()

# print(df.head())

sql_data = df.apply(
    lambda row: (
        f"Employee ID no. {row['employeenumber']} works in the {row['department']} department. "
        f"Education field is {row['educationfield']}. "
        f"Gender is {row['gender']}. "
        f"Job role is {row['jobrole']}. "
        f"Performance rating is {row['performancerating']}."
    ),
    axis=1
).tolist()

metadatas = df[['employeenumber']].to_dict(orient='records')
for i in metadatas:
    i["source"] = "postgresql"
    i["database"] = "talk2data"
    i["table"] = "employee_attrition"

ids = df["employeenumber"].astype(str).tolist()

# CHROMADB FOR SQL DATA
client = chromadb.PersistentClient(path="./chroma_db") 
collection = client.get_or_create_collection("employee_data")

collection.upsert(
    documents=sql_data,
    metadatas=metadatas,
    ids=ids
)

# ----------------------------------------------------------------------------------------------------
# This is for PDF ingestion, it converts the pdf to txt for chromadb ingestion, you can use the txt directly if you want. i am using a .txt file so i dont have it keep running the code.
 
# from pypdf import PdfReader

# reader = PdfReader("data\Employee-Handbook.pdf")
# txt_path = "data\employee_handbook.txt"

# full_text = ""

# for page in reader.pages[2:]:
#     text = page.extract_text()
#     if text:
#         full_text += text + "\n"

# with open(txt_path, "w", encoding="utf-8") as f:
#     f.write(full_text)

# CHROMADB FOR PDFs
from langchain_text_splitters import RecursiveCharacterTextSplitter
with open("data/employee_handbook.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)
processed_text = text_splitter.split_text(full_text)

metadatas_pdf = [{"source": "pdf"} for _ in processed_text]
ids_pdf = [f"employee_handbook_{i}" for i in range(len(processed_text))]

collection.upsert(
    documents=processed_text,
    metadatas=metadatas_pdf,
    ids=ids_pdf
)