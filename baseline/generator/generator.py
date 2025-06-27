from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import TokenCountingHandler
from llama_index.core.prompts import RichPromptTemplate
from llama_index.core import get_response_synthesizer
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

EXPANSIVE_QUERY_TRIGGERS = [
    "all comments",
    "list all",
    "summarize all",
    "show everything",
    "give full history",
    "every pr",
    "all prs",
    "full discussion",
    "all commits",
    "give me all commits",
    "every commit",
    "commits from all",
    "full commit history",
    "show commits for all prs"
]

prompt_template_str = """You are CodeReview Genie, an expert code reviewer.

Based on the following PR documents:

{{ context_str }}

Answer the question:
{{ query_str }}

Respond in a structured manner.
If something isn't applicable, write 'Sorry I am unaware of this information.'.
"""

custom_prompt = RichPromptTemplate(prompt_template_str)

def ask_query(index, query: str, token_counter: TokenCountingHandler):
    logger.info(f"Asking question: {query}")
    try:
        llm = OpenAI(model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)

        is_expansive = any(phrase in query.lower() for phrase in EXPANSIVE_QUERY_TRIGGERS)
        top_k = 50 if is_expansive else 5

        response_synthesizer = get_response_synthesizer(text_qa_template=custom_prompt)

        query_engine = index.as_query_engine(similarity_top_k=top_k, response_synthesizer=response_synthesizer, llm=llm)
        query_engine.callback_manager.add_handler(token_counter)

        logger.info(f"Using similarity_top_k={top_k} for this query.")

        retrieved_nodes = query_engine.retriever.retrieve(query)
        print("\n=== Retrieved Chunks for Query ===")
        for i, node in enumerate(retrieved_nodes):
            print(f"\n--- Chunk #{i+1} ---\n{node.text}\n")

        # Run the actual query
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
