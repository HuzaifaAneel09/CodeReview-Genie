# CodeReview Genie <img src="https://www.animatedimages.org/data/media/111/animated-genie-image-0027.gif" width="40" />

CodeReview Genie is a powerful tool that leverages Large Language Models (LLMs) to analyze and answer questions about GitHub repositories. It provides a web-based interface to interact with your codebase, offering insights and understanding of public and private repositories.

---

## ✨ Features

-   **🤖 Q&A on GitHub Repositories**: Ask questions in natural language about a repository's code and get intelligent answers.
-   **🔒 Support for Private Repositories**: Authenticate with GitHub to analyze your private codebases securely.
-   **🧠 Retrieval-Augmented Generation (RAG)**: Utilizes a RAG pipeline with `llama-index` and ChromaDB to retrieve relevant code context before generating answers, ensuring high accuracy.
-   **⚡ Efficient Caching**: Employs Redis to cache repository data, speeding up subsequent analyses.
-   **🔄 Webhook Integration**: Automatically invalidates caches and indexes when a repository is updated, ensuring the data is always fresh.
-   **📊 Built-in Evaluation**: Includes a testing framework to evaluate the performance and accuracy of the Q&A system.
-   **💻 Modern Tech Stack**: Built with a FastAPI backend and a React/Vite frontend.

---

## 📂 Folder Structure

Here is an overview of the project's directory structure:

```
.
├── 📁 baseline/         # Core backend logic
│   ├── 📄 pipeline.py   # FastAPI application and main endpoints
│   ├── 📁 generator/    # LLM-based answer generation
│   └── 📁 retriever/    # Data retrieval and indexing from GitHub
├── 📁 frontend/         # React frontend application
│   ├── 📁 src/          # Frontend source code
│   │   ├── 📄 App.jsx
│   │   └── 📄 QueryPage.jsx
│   ├── 📄 package.json  # Frontend dependencies
│   └── 📄 vite.config.js# Vite configuration
├── 📁 evaluation/       # Test sets and utilities for evaluation
├── 📁 specialization/   # Specialized clients (e.g., GitHub API client)
├── 📁 utils/            # Shared utility modules (caching, logging)
├── 📁 chroma_db/        # Local storage for ChromaDB vector store
├── 📄 requirements.txt  # Python dependencies for the backend
└── 📄 README.md         # This file
```

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### ✅ Prerequisites

-   Python 3.8+
-   Node.js v18+ and npm
-   Git
-   Redis server (running on the default port)

### ⚙️ Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory. You'll need to create a [GitHub OAuth App](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) to get your client ID and secret.
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

### 🖥️ Frontend Setup

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

---

## 💻 Usage

1.  Open your browser and navigate to `http://localhost:5173`.
2.  Enter the URL of a public GitHub repository you want to analyze.
3.  To analyze a private repository, click the "Login with GitHub" button to authenticate.
4.  Once the repository is loaded, ask a question in the input box and get your answer!

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-4B0082?style=for-the-badge&logoColor=white)
![ChromaDB](https://img.shields.io/badge/Chroma-6E44FF?style=for-the-badge&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)

---