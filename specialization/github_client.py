import requests
import os
from dotenv import load_dotenv
from utils.cache import get_cached_repo, set_cached_repo
from utils.logger import logger

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def build_headers(access_token=None):
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    elif GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def fetch_pull_requests(owner: str, repo: str, state="open", per_page=10, access_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {"state": state, "per_page": per_page}
    headers = build_headers(access_token)
    logger.info(f"Fetching pull requests for {owner}/{repo} with state='{state}'")

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        prs = response.json()
        logger.info(f"Fetched {len(prs)} PRs from {owner}/{repo}")
        return prs
    except Exception as e:
        logger.error(f"Failed to fetch PRs: {e}", exc_info=True)
        raise

def fetch_comments(owner: str, repo: str, pr_number: int, access_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = build_headers(access_token)
    logger.info(f"Fetching comments for PR #{pr_number} in {owner}/{repo}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        comments = response.json()
        logger.info(f"Fetched {len(comments)} comments for PR #{pr_number}")
        return comments
    except Exception as e:
        logger.error(f"Failed to fetch comments for PR #{pr_number}: {e}", exc_info=True)
        raise

def fetch_commits(owner: str, repo: str, pr_number: int, access_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    headers = build_headers(access_token)
    logger.info(f"Fetching commits for PR #{pr_number} in {owner}/{repo}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        logger.info(f"Fetched {len(commits)} commits for PR #{pr_number}")
        return commits
    except Exception as e:
        logger.error(f"Failed to fetch commits for PR #{pr_number}: {e}", exc_info=True)
        raise

def fetch_and_format(owner: str, repo: str, access_token=None):
    logger.info(f"Starting to fetch and format PR data for {owner}/{repo}")

    # Check cache
    cached = get_cached_repo(owner, repo)
    if cached:
        return cached

    data = []
    prs = fetch_pull_requests(owner, repo, access_token=access_token)

    if not prs:
        logger.warning(f"No PRs found for {owner}/{repo}")
        return data

    for pr in prs:
        pr_number = pr["number"]
        title = pr["title"]
        author = pr["user"]["login"]
        body = pr.get("body", "")
        comments = fetch_comments(owner, repo, pr_number, access_token=access_token)
        commits = fetch_commits(owner, repo, pr_number, access_token=access_token)

        text = f"PR #{pr_number}: {title}\nAuthor: {author}\n{body}\n"

        text += f"Commits ({len(commits)}):\n"
        for commit in commits:
            msg = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            text += f"- {msg} (by {author})\n"

        for comment in comments:
            commenter = comment["user"]["login"]
            text += f"Comment by {commenter}: {comment['body']}\n"

        data.append(text)
    
    logger.info(f"Formatted {len(data)} PR documents for {owner}/{repo}")

    # Cache the result
    set_cached_repo(owner, repo, data)

    return data

