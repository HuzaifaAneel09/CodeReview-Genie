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
    
    # Fetch PRs (both open and closed)
    open_prs = fetch_pull_requests(owner, repo, state="open", per_page=50, access_token=access_token)
    closed_prs = fetch_pull_requests(owner, repo, state="closed", per_page=50, access_token=access_token)
    all_prs = open_prs + closed_prs

    if not all_prs:
        logger.warning(f"No PRs found for {owner}/{repo}")
        return data

    for pr in all_prs:
        pr_number = pr["number"]
        title = pr["title"]
        author = pr["user"]["login"]
        body = pr.get("body", "")
        state = pr["state"]
        merged = pr.get("merged", False)
        created_at = pr["created_at"]
        updated_at = pr["updated_at"]
        
        if state == "open":
            status = "OPEN"
        elif merged:
            status = "MERGED"
        else:
            status = "CLOSED"
        
        comments = fetch_comments(owner, repo, pr_number, access_token=access_token)
        commits = fetch_commits(owner, repo, pr_number, access_token=access_token)

        text = f"PR #{pr_number}: {title}\n"
        text += f"Author: {author}\n"
        text += f"Status: {status}\n"
        text += f"Created: {created_at}\n"
        text += f"Updated: {updated_at}\n"
        if merged:
            text += f"Merged: Yes\n"
        text += f"Description: {body}\n"

        # Show ALL commits in this PR (regardless of author)
        text += f"Commits ({len(commits)}):\n"
        for commit in commits:
            msg = commit["commit"]["message"]
            commit_author = commit["commit"]["author"]["name"]
            commit_date = commit["commit"]["author"]["date"]
            sha = commit["sha"][:7]
            text += f"- {msg} (by {commit_author} on {commit_date}) [{sha}]\n"

        # Show ALL comments in this PR
        if comments:
            text += f"Comments ({len(comments)}):\n"
            for comment in comments:
                commenter = comment["user"]["login"]
                comment_date = comment["created_at"]
                text += f"Comment by {commenter} on {comment_date}: {comment['body']}\n"
        else:
            text += "Comments: None\n"

        data.append(text)
    
    logger.info(f"Formatted {len(data)} PR documents for {owner}/{repo}")

    # Cache the result
    set_cached_repo(owner, repo, data)

    return data

