from chromadb import PersistentClient
from fastapi import Body, FastAPI, Query, Request
from pydantic import BaseModel, HttpUrl
from urllib.parse import urlparse
from llama_index.core.callbacks import TokenCountingHandler
from baseline.retriever.retriever import build_index_from_github
from baseline.generator.generator import ask_query
from evaluation.testutils import load_test_entry, save_test_entry
from specialization.github_client import fetch_commits, fetch_pull_requests
from utils.cache import check_redis_connection, invalidate_repo_cache
from utils.logger import logger
from utils.metrics import log_metrics

import time
import uuid

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
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(f"[{request_id}] Received query for repo: {input.repo_url}")
    try:
        owner, repo = extract_owner_repo(input.repo_url)
        logger.info(f"[{request_id}] Building index for {owner}/{repo}")
        index, token_counter = build_index_from_github(owner, repo)

        logger.info(f"[{request_id}] Asking question: {input.question}")
        answer, token_count, cost_usd = ask_query(index, input.question, token_counter)
        embedding_tokens = token_counter.total_embedding_token_count

        duration = round(time.time() - start_time, 2)
        logger.info(f"[{request_id}] Query successful, tokens used: {token_count}, cost: ${cost_usd:.6f}, duration: {duration}s")

        log_metrics({
            "request_id": request_id,
            "repo_url": input.repo_url,
            "question": input.question,
            "embedding_tokens": embedding_tokens,
            "llm_tokens": token_count,
            "tokens_total": token_count + embedding_tokens,
            "cost_usd": round(cost_usd, 6),
            "latency_seconds": duration,
            "error": ""
        })

        return {
            "answer": answer,
            "llm_tokens": token_count,
            "embedding_tokens": embedding_tokens,
            "tokens_total": token_count + embedding_tokens,
            "estimated_cost_usd": round(cost_usd, 6),
        }

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        error_msg = str(e)
        logger.error(f"[{request_id}] Error while handling query: {error_msg}", exc_info=True)

        log_metrics({
            "request_id": request_id,
            "repo_url": input.repo_url,
            "question": input.question,
            "tokens_total": 0,
            "llm_tokens": 0,
            "embedding_tokens": 0,
            "cost_usd": 0,
            "latency_seconds": duration,
            "error": error_msg
        })

        return {"error": error_msg}
    
@app.post("/webhook")
async def github_webhook(request: Request):
    if not check_redis_connection():
        logger.error("Webhook blocked: Redis is not available.")
        return {"status": "error", "message": "Redis is not available."}

    payload = await request.json()

    try:
        repo = payload.get("repository", {})
        owner = repo.get("owner", {}).get("login")
        name = repo.get("name")

        if not owner or not name:
            logger.warning("Webhook received but owner/repo missing in payload")
            return {"status": "ignored"}

        logger.info(f"Webhook received. Invalidating cache and index for: {owner}/{name}")

        # Invalidate Redis cache
        invalidate_repo_cache(owner, name)

        # Delete Chroma collection for this repo
        chroma_client = PersistentClient(path="./chroma_db")
        collection_name = f"code_review_chunks_{owner}_{name}"
        try:
            chroma_client.delete_collection(collection_name)
            logger.info(f"Deleted Chroma collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Chroma collection '{collection_name}' may not exist or failed to delete: {e}")

        return {"status": "cache and index invalidated", "repo": f"{owner}/{name}"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    

@app.post("/generate-test")
def generate_test_case(repo_url: HttpUrl = Body(..., embed=True)):
    parsed = urlparse(str(repo_url))
    try:
        owner, repo = parsed.path.strip("/").split("/", 1)
    except ValueError:
        raise ValueError("Invalid GitHub URL format")

    prs = fetch_pull_requests(owner, repo, state="open", per_page=20)
    if not prs:
        return {"status": "skipped", "reason": "No open PRs found."}

    all_commits = []
    for pr in prs:
        pr_commits = fetch_commits(owner, repo, pr["number"])
        for commit in pr_commits:
            all_commits.append({
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"]
            })

    test_entry = {
        "repo": f"{owner}/{repo}",
        "total_commits": len(all_commits),
        "commits": all_commits
    }

    save_test_entry(test_entry)

    return {
        "status": "success",
        "repo": test_entry["repo"],
        "commits_collected": len(all_commits)
    }

@app.get("/run-test")
def run_single_test(repo: str = Query(...)):
    # Loading test data
    test_entry = load_test_entry(repo)
    if not test_entry:
        return {"status": "error", "message": f"Test data not found for repo '{repo}'"}

    owner, name = repo.split("/")
    token_counter = TokenCountingHandler()
    index, _ = build_index_from_github(owner, name)

    # Asking the model
    question = "List all commit messages from all PRs."
    response_text, _, _ = ask_query(index, question, token_counter)

    # Compairing here
    expected = [c["message"].strip().lower() for c in test_entry["commits"]]
    predicted = response_text.strip().lower().splitlines()

    unmatched = []
    matched_count = 0
    for msg in expected:
        found = any(msg in line for line in predicted)
        if found:
            matched_count += 1
        unmatched.append({
            "expected": msg,
            "found": found
        })

    return {
        "repo": repo,
        "total_commits_expected": len(expected),
        "total_commits_predicted": len(predicted),
        "commits_matched": matched_count,
        "match_ratio": round(matched_count / len(expected), 2),
        "unmatched_commits": unmatched,
    }



