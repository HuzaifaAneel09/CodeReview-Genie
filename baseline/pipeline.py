import json
from chromadb import PersistentClient
from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
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
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

import time
import uuid

app = FastAPI()

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_CALLBACK_URL = "http://localhost:8000/auth/github/callback"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or I can just do this if security issues ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    test_entry = load_test_entry(repo)
    if not test_entry:
        return {"status": "error", "message": f"Test data not found for repo '{repo}'"}

    owner, name = repo.split("/")
    token_counter = TokenCountingHandler()
    index, _ = build_index_from_github(owner, name)

    question = "List all commit messages from all PRs."
    response_text, _, _ = ask_query(index, question, token_counter)

    expected = [c["message"].strip().lower() for c in test_entry["commits"]]
    predicted = [line.strip().lower() for line in response_text.strip().splitlines() if line.strip()]

    matched_count = 0
    unmatched = []

    for msg in expected:
        found = any(msg in line for line in predicted)
        if found:
            matched_count += 1
        unmatched.append({
            "expected": msg,
            "found": found
        })

    total_expected = len(expected)
    total_predicted = len(predicted)

    precision = matched_count / total_predicted if total_predicted else 0.0
    recall = matched_count / total_expected if total_expected else 0.0
    f1_score = (
        2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0
    )

    return {
        "repo": repo,
        "total_commits_expected": total_expected,
        "total_commits_predicted": total_predicted,
        "commits_matched": matched_count,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1_score, 3),
        "unmatched_commits": unmatched,
    }

# 1. Redirect user to GitHub login
@app.get("/auth/github")
def github_login():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_CALLBACK_URL}&scope=repo"
    )
    return RedirectResponse(github_auth_url)

# 2. GitHub redirects back here with a code
@app.get("/auth/github/callback")
async def github_callback(code: str):
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_CALLBACK_URL
            }
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub login failed")

        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_response.json()

    # Use postMessage to send data to parent window
    auth_data = {
        "access_token": access_token,
        "user": {
            "login": user_data.get("login"),
            "name": user_data.get("name"),
            "avatar_url": user_data.get("avatar_url")
        }
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authorization Success</title></head>
    <body>
        <script>
            const authData = {json.dumps(auth_data)};
            
            // Send message to parent window
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'GITHUB_AUTH_SUCCESS',
                    data: authData
                }}, '*');
            }}
            
            // Close the popup
            setTimeout(() => {{
                window.close();
            }}, 1000);
        </script>
        <div style="text-align: center; font-family: Arial, sans-serif; padding: 50px;">
            <h2>✅ Authorization Successful!</h2>
            <p>This window will close automatically...</p>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

class AuthQueryInput(BaseModel):
    owner: str
    repo: str
    question: str
    access_token: str

@app.post("/query/auth")
def query_with_auth(input: AuthQueryInput):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info(f"[{request_id}] Received AUTH query for {input.owner}/{input.repo}")
        
        index, token_counter = build_index_from_github(
            owner=input.owner,
            repo=input.repo,
            access_token=input.access_token
        )
        
        answer, token_count, cost_usd = ask_query(index, input.question, token_counter)
        embedding_tokens = token_counter.total_embedding_token_count

        duration = round(time.time() - start_time, 2)
        logger.info(f"[{request_id}] AUTH query successful: tokens={token_count}, cost=${cost_usd:.6f}, duration={duration}s")

        log_metrics({
            "request_id": request_id,
            "repo_url": f"{input.owner}/{input.repo}",
            "question": input.question,
            "embedding_tokens": embedding_tokens,
            "llm_tokens": token_count,
            "tokens_total": token_count + embedding_tokens,
            "cost_usd": round(cost_usd, 6),
            "latency_seconds": duration,
            "auth_used": True,
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
        logger.error(f"[{request_id}] AUTH query failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "latency_seconds": duration,
            "request_id": request_id
        }

