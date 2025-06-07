from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def ask_query(index, query: str):
    llm = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    query_engine = index.as_query_engine(similarity_top_k=5, llm=llm)
    response = query_engine.query(query)
    return str(response)
