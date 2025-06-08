import requests
import os
from dotenv import load_dotenv
from utils.logger import logger  # <-- import the logger

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def fetch_pull_requests(owner: str, repo: str, state="open", per_page=10):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {"state": state, "per_page": per_page}
    logger.info(f"Fetching pull requests for {owner}/{repo} with state='{state}'")

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        prs = response.json()
        logger.info(f"Fetched {len(prs)} PRs from {owner}/{repo}")
        return prs
    except Exception as e:
        logger.error(f"Failed to fetch PRs: {e}", exc_info=True)
        raise

def fetch_comments(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    logger.info(f"Fetching comments for PR #{pr_number} in {owner}/{repo}")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        comments = response.json()
        logger.info(f"Fetched {len(comments)} comments for PR #{pr_number}")
        return comments
    except Exception as e:
        logger.error(f"Failed to fetch comments for PR #{pr_number}: {e}", exc_info=True)
        raise

def fetch_commits(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    logger.info(f"Fetching commits for PR #{pr_number} in {owner}/{repo}")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        commits = response.json()
        logger.info(f"Fetched {len(commits)} commits for PR #{pr_number}")
        return commits
    except Exception as e:
        logger.error(f"Failed to fetch commits for PR #{pr_number}: {e}", exc_info=True)
        raise

def fetch_and_format(owner: str, repo: str):
    logger.info(f"Starting to fetch and format PR data for {owner}/{repo}")
    data = []
    prs = fetch_pull_requests(owner, repo)

    if not prs:
        logger.warning(f"No PRs found for {owner}/{repo}")
        return data

    for pr in prs:
        pr_number = pr["number"]
        title = pr["title"]
        author = pr["user"]["login"]
        body = pr.get("body", "")
        comments = fetch_comments(owner, repo, pr_number)
        commits = fetch_commits(owner, repo, pr_number)

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
    return data
