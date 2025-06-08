from fastapi import FastAPI
from pydantic import BaseModel
from urllib.parse import urlparse
from baseline.retriever.retriever import build_index_from_github
from baseline.generator.generator import ask_query
from utils.logger import logger

app = FastAPI()

class QueryInput(BaseModel):
    repo_url: str
    question: str

def extract_owner_repo(repo_url: str):
    try:
        path = urlparse(repo_url).path.strip("/")
        owner, repo = path.split("/", 1)
        logger.info(f"Extracted owner: {owner}, repo: {repo} from URL: {repo_url}")
        return owner, repo
    except ValueError:
        logger.error(f"Invalid GitHub URL format: {repo_url}", exc_info=True)
        raise ValueError("Invalid GitHub URL. Format must be: https://github.com/owner/repo")

@app.post("/query")
def query(input: QueryInput):
    logger.info(f"Received query for repo: {input.repo_url}")
    try:
        owner, repo = extract_owner_repo(input.repo_url)
        logger.info(f"Building index for {owner}/{repo}")
        index, token_counter = build_index_from_github(owner, repo)  # ✅ now returns 2 values

        logger.info(f"Asking question: {input.question}")
        answer, token_count = ask_query(index, input.question, token_counter)

        logger.info(f"Query successful, tokens used: {token_count}")
        return {"answer": answer, "tokens_used": token_count}
    except Exception as e:
        logger.error(f"Error while handling query: {str(e)}", exc_info=True)
        return {"error": str(e)}

