from fastapi import FastAPI
from pydantic import BaseModel
from urllib.parse import urlparse
from baseline.retriever.retriever import build_index_from_github
from baseline.generator.generator import ask_query

app = FastAPI()

class QueryInput(BaseModel):
    repo_url: str
    question: str

def extract_owner_repo(repo_url: str):
    try:
        path = urlparse(repo_url).path.strip("/")
        owner, repo = path.split("/", 1)
        return owner, repo
    except ValueError:
        raise ValueError("Invalid GitHub URL. Format must be: https://github.com/owner/repo")

@app.post("/query")
def query(input: QueryInput):
    try:
        owner, repo = extract_owner_repo(input.repo_url)
        index = build_index_from_github(owner, repo)
        answer = ask_query(index, input.question)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
