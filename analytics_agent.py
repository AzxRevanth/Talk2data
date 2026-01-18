import os
import pandas as pd
from sqlalchemy import create_engine, text
from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM
from pandasai.llm import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import glob

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"

if USE_LOCAL_LLM:
    llm = LocalLLM(
        api_base="http://localhost:11434/v1",
        model="qwen3:4b"
    )
else:
    llm = OpenAI(
        api_token=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

# SQLAlchemy engine 
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DB')}",
    pool_pre_ping=True,
    pool_recycle=300
)

def load_df():
    try:
        query = "SELECT * FROM employee_attrition"
        with engine.connect() as connection:
            return pd.read_sql(text(query), connection)
    except Exception as e:
        print(f"Database error: {e}")
        raise

def analytics_agent(user_query: str, response_parser: bool):
    try:
        df = load_df()

        config = {
            "llm": llm,
            "enable_cache": False,
            "verbose": False,
            "save_charts": True,      
            "open_charts": False,
        }
        sdf = SmartDataframe(df, config=config)
        result = sdf.chat(user_query)

        if not response_parser:
            return {
                "type": "text",
                "content": result
            }
        
        if isinstance(result, go.Figure):
            return {
                "type": "plot",
                "figure": result,
            }

        if isinstance(result, str) and result.endswith(".png"):
            return {
                "type": "image",
                "path": result,
            }

        return {
            "type": "text",
            "content": result
        }
    except Exception as e:
        print(f"Analytics agent error: {e}")
        raise
