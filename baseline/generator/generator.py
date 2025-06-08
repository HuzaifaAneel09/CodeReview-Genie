from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

def ask_query(index, query: str):
    logger.info(f"Asking question: {query}")
    try:
        llm = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
        query_engine = index.as_query_engine(similarity_top_k=5, llm=llm)
        response = query_engine.query(query)
        logger.info("Query answered successfully.")
        return str(response)
    except Exception as e:
        logger.error(f"Error while querying GPT: {e}", exc_info=True)
        raise
