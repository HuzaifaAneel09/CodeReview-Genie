from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import TokenCountingHandler
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

def ask_query(index, query: str, token_counter: TokenCountingHandler):
    logger.info(f"Asking question: {query}")
    try:
        llm = OpenAI(model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
        query_engine = index.as_query_engine(similarity_top_k=5, llm=llm)
        
        # Attach the token counter to the engine
        query_engine.callback_manager.add_handler(token_counter)

        response = query_engine.query(query)

        prompt_tokens = token_counter.prompt_llm_token_count
        completion_tokens = token_counter.completion_llm_token_count
        total_tokens = token_counter.total_llm_token_count

        cost_usd = (prompt_tokens * 0.0001 + completion_tokens * 0.0004)

        logger.info(f"Tokens used -> prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}")
        return str(response), total_tokens, cost_usd
    except Exception as e:
        logger.error(f"Error while querying GPT: {e}", exc_info=True)
        raise
