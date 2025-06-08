import requests
import os
from dotenv import load_dotenv

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
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def fetch_comments(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_commits(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_and_format(owner: str, repo: str):
    data = []
    prs = fetch_pull_requests(owner, repo)

    for pr in prs:
        pr_number = pr["number"]
        title = pr["title"]
        author = pr["user"]["login"]
        body = pr.get("body", "")
        comments = fetch_comments(owner, repo, pr_number)
        commits = fetch_commits(owner, repo, pr_number)

        text = f"PR #{pr_number}: {title}\nAuthor: {author}\n{body}\n"

        # Add commits
        text += f"Commits ({len(commits)}):\n"
        for commit in commits:
            msg = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            text += f"- {msg} (by {author})\n"

        # Add comments
        for comment in comments:
            commenter = comment["user"]["login"]
            text += f"Comment by {commenter}: {comment['body']}\n"

        data.append(text)
    
    return data

