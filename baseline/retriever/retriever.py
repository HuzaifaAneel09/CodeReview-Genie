from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
import os
from dotenv import load_dotenv
from specialization.github_client import fetch_and_format

load_dotenv()

def build_index_from_github(owner: str, repo: str):
    texts = fetch_and_format(owner, repo)

    if not texts:
        raise ValueError(f"No pull request data found for repo: {owner}/{repo}")

    documents = [Document(text=t) for t in texts]

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
        embed_model=embed_model
    )

    return index
