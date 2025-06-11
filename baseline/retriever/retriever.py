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

CHROMA_PATH = "./chroma_db"

def build_index_from_github(owner: str, repo: str):
    logger.info(f"Checking for existing index for GitHub repo: {owner}/{repo}")
    collection_name = f"code_review_chunks_{owner}_{repo}"

    token_counter = TokenCountingHandler()
    callback_manager = CallbackManager([token_counter])

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    all_collections = [c.name for c in chroma_client.list_collections()]

    if collection_name in all_collections:
        logger.info(f"Found existing collection '{collection_name}'. Reusing index.")
        collection = chroma_client.get_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
        return index, token_counter

    logger.info(f"No existing index. Building new index for {owner}/{repo}")
    texts = fetch_and_format(owner, repo)

    if not texts:
        logger.warning(f"No PR data found for {owner}/{repo}")
        raise ValueError(f"No pull request data found for repo: {owner}/{repo}")

    documents = [Document(text=t) for t in texts]

    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
        callback_manager=callback_manager
    )

    collection = chroma_client.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        callback_manager=callback_manager
    )

    embedding_tokens = token_counter.total_embedding_token_count
    logger.info(f"Embedding tokens used: {embedding_tokens}")

    logger.info(f"Index built and stored for {owner}/{repo}")
    return index, token_counter
