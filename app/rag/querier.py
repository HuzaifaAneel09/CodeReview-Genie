from llama_index.llms.openai import OpenAI
from app.config import OPENAI_API_KEY

def ask_query(index, query: str):
    llm = OpenAI(model="gpt-4.1-nano", api_key=OPENAI_API_KEY, temperature=0)
    query_engine = index.as_query_engine(similarity_top_k=5, llm=llm)
    response = query_engine.query(query)
    return str(response)
