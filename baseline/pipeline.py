from fastapi import FastAPI, Request
from pydantic import BaseModel
from urllib.parse import urlparse
from baseline.retriever.retriever import build_index_from_github
from baseline.generator.generator import ask_query
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

        duration = round(time.time() - start_time, 2)
        logger.info(f"[{request_id}] Query successful, tokens used: {token_count}, cost: ${cost_usd:.6f}, duration: {duration}s")

        log_metrics({
            "request_id": request_id,
            "repo_url": input.repo_url,
            "question": input.question,
            "tokens_total": token_count,
            "cost_usd": round(cost_usd, 6),
            "latency_seconds": duration,
            "error": ""
        })

        return {
            "answer": answer,
            "tokens_used": token_count,
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

        logger.info(f"Webhook received. Invalidating cache for: {owner}/{name}")
        invalidate_repo_cache(owner, name)

        return {"status": "cache invalidated", "repo": f"{owner}/{name}"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


