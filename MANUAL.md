# CodeReview Genie Manual

## 1. Introduction

Welcome to the CodeReview Genie! This manual is designed to help you understand and test the capabilities of this powerful tool. CodeReview Genie uses Large Language Models (LLMs) to analyze and answer questions about GitHub repositories, providing a web-based interface to interact with your codebase.

This guide will walk you through the system's architecture, setup, and, most importantly, how to test its features effectively.

## 2. System Architecture

The system is composed of two main parts:

*   **Frontend**: A user-friendly React application (built with Vite) that allows you to interact with the system. You'll use this to enter repository URLs and ask questions.
*   **Backend**: A robust FastAPI application that powers the analysis. It uses a Retrieval-Augmented Generation (RAG) pipeline with `llama-index` and ChromaDB to retrieve relevant code context and generate accurate answers. It also uses Redis for caching to speed up subsequent analyses.

## 3. Getting Started

To get the system up and running for testing, please follow these steps:

### Prerequisites

Make sure you have the following installed on your system:

*   Python 3.8+
*   Node.js v18+ and npm
*   Git
*   A Redis server running on its default port (6379).

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/HuzaifaAneel09/CodeReview-Genie
    cd CodeReview-Genie
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory of the project. You will need to create a [GitHub OAuth App](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) to get your client ID and secret.
    ```ini
    # .env
    GITHUB_CLIENT_ID="your_github_oauth_client_id"
    GITHUB_CLIENT_SECRET="your_github_oauth_client_secret"
    OPENAI_API_KEY="your_openai_api_key"
    ```
    *The callback URL for your GitHub OAuth app should be `http://localhost:8000/auth/github/callback`.*

4.  **Run the backend server:**
    ```bash
    uvicorn baseline.pipeline:app --reload
    ```
    The backend API will be available at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory and install dependencies:**
    ```bash
    cd frontend
    npm install
    ```

2.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend application will be available at `http://localhost:5173`.

## 4. How to Test the System

Now that the system is running, you can start testing its features. Here’s how you can test the core functionalities:

### Testing with a Public Repository

1.  Open your browser and navigate to `http://localhost:5173`.
2.  Find a public GitHub repository you want to analyze (e.g., `https://github.com/facebook/react`).
3.  Enter the URL of the repository in the input box and click the "Load Repository" button.
4.  Once the repository is loaded, you can ask questions about the code. Here are some examples of questions you can ask:
    *   "What is the main purpose of this repository?"
    *   "Explain the folder structure."
    *   "What are the main dependencies of this project?"
    *   "Where is the main entry point of the application?"

### Testing with a Private Repository

1.  To analyze a private repository, you first need to authenticate with GitHub.
2.  Click the "Login with GitHub" button on the top right of the page.
3.  You will be redirected to GitHub to authorize the application. Once you authorize, you will be redirected back to the application.
4.  Now you can enter the URL of your private repository and ask questions just like with a public repository.

### Testing the Evaluation Framework

The system includes a built-in evaluation framework to test the performance and accuracy of the Q&A system. Here’s how to use it:

1.  **Generate a test case:**
    You can generate a test case for a repository by sending a `POST` request to the `/generate-test` endpoint. This will fetch the open pull requests and their commit messages and save them to a test file.

    You can use a tool like `curl` or Postman to send the request:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"repo_url": "https://github.com/owner/repo"}' http://localhost:8000/generate-test
    ```

2.  **Run a test case:**
    Once you have generated a test case, you can run it by sending a `GET` request to the `/run-test` endpoint with the repository name as a query parameter.

    ```bash
    curl -X GET "http://localhost:8000/run-test?repo=owner/repo"
    ```
    This will run a test against the repository and return a set of metrics, including precision, recall, and F1-score.

## 5. API Endpoints for Testers

Here is a more detailed description of the API endpoints that you can use for testing:

*   `POST /query`
    *   **Description**: Ask a question about a public repository.
    *   **Request Body**:
        ```json
        {
            "repo_url": "https://github.com/owner/repo",
            "question": "Your question here"
        }
        ```
    *   **Response**: The answer to your question, along with some metrics.

*   `POST /query/auth`
    *   **Description**: Ask a question about a private repository.
    *   **Request Body**:
        ```json
        {
            "owner": "owner",
            "repo": "repo",
            "question": "Your question here",
            "access_token": "your_github_access_token"
        }
        ```
    *   **Response**: Same as `/query`.

*   `GET /auth/github`
    *   **Description**: Redirects the user to GitHub to authenticate.

*   `GET /auth/github/callback`
    *   **Description**: The callback URL for GitHub OAuth.

*   `POST /webhook`
    *   **Description**: A webhook that invalidates the cache and index for a repository when it's updated. You can test this by setting up a webhook in your GitHub repository to point to this endpoint.

*   `POST /generate-test`
    *   **Description**: Generates a test case for a repository.

*   `GET /run-test`
    *   **Description**: Runs a single test case and returns the results.