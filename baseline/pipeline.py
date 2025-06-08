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
        index = build_index_from_github(owner, repo)

        logger.info(f"Asking question: {input.question}")
        answer = ask_query(index, input.question)

        logger.info(f"Query successful")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error while handling query: {str(e)}", exc_info=True)
        return {"error": str(e)}
