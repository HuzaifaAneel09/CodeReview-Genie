from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
import chromadb
import os
from dotenv import load_dotenv
from specialization.github_client import fetch_and_format
from utils.logger import logger

load_dotenv()

def build_index_from_github(owner: str, repo: str):
    logger.info(f"Fetching and building index for GitHub repo: {owner}/{repo}")

    texts = fetch_and_format(owner, repo)

    if not texts:
        logger.warning(f"No PR data found for {owner}/{repo}")
        raise ValueError(f"No pull request data found for repo: {owner}/{repo}")

    documents = [Document(text=t) for t in texts]
    logger.info(f"Converting {len(documents)} PR entries to documents")

    try:
        token_counter = TokenCountingHandler()
        callback_manager = CallbackManager([token_counter])

        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_or_create_collection("code_review_chunks")
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model,
            callback_manager=callback_manager
        )

        logger.info(f"Index built successfully for {owner}/{repo}")
        return index, token_counter
    except Exception as e:
        logger.error(f"Error building vector index for {owner}/{repo}: {e}", exc_info=True)
        raise
