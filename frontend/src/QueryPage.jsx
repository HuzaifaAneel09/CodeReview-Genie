import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function QueryPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [isVisible] = useState(true);
  const [selectedRepo, setSelectedRepo] = useState("");
  const [retrievedChunks, setRetrievedChunks] = useState(null);
  const [showChunks, setShowChunks] = useState(false);

  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    user: null,
    accessToken: null,
    userRepos: [],
  });
  const [inputMethod, setInputMethod] = useState("github"); // 'github' | 'manual'
  const [loadingAuth, setLoadingAuth] = useState(false);
  const [loadingRepos, setLoadingRepos] = useState(false);

  const navigate = useNavigate();

  const handleGitHubAuth = () => {
    setLoadingAuth(true);
    const popup = window.open(
      "http://localhost:8000/auth/github",
      "github-auth",
      "width=600,height=700,scrollbars=yes,resizable=yes"
    );

    // Listen for messages from popup
    const handleMessage = (event) => {
      if (event.data.type === "GITHUB_AUTH_SUCCESS") {
        const authData = event.data.data;

        // Save to localStorage
        localStorage.setItem("github_auth", JSON.stringify(authData));

        // Update state
        setAuthState({
          isAuthenticated: true,
          user: authData.user,
          accessToken: authData.access_token,
          userRepos: [],
        });

        // Fetch repos
        fetchUserRepos(authData.access_token);

        // Clean up
        window.removeEventListener("message", handleMessage);
        setLoadingAuth(false);
        popup.close();
      }
    };

    // Add message listener
    window.addEventListener("message", handleMessage);

    // Fallback: check if popup was closed manually
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        window.removeEventListener("message", handleMessage);
        setLoadingAuth(false);
      }
    }, 1000);
  };

  const fetchUserRepos = async (accessToken) => {
    setLoadingRepos(true);
    try {
      const response = await fetch(
        "https://api.github.com/user/repos?per_page=100",
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            Accept: "application/vnd.github.v3+json",
          },
        }
      );
      const repos = await response.json();
      setAuthState((prev) => ({
        ...prev,
        userRepos: repos.filter((repo) => !repo.fork), // Filter out forked repos
      }));
    } catch (error) {
      console.error("Failed to fetch repos:", error);
    } finally {
      setLoadingRepos(false);
    }
  };

  const handleRepoSelect = (repoFullName) => {
    setSelectedRepo(repoFullName);
    setRepoUrl(`https://github.com/${repoFullName}`);
  };

  const handleLogout = () => {
    localStorage.removeItem("github_auth");
    setAuthState({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      userRepos: [],
    });
    setInputMethod("manual");
    setRepoUrl("");
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setResponse(null);
    setRetrievedChunks(null); // Reset chunks
    setShowChunks(false); // Hide chunks panel

    try {
      let res;

      // Use authenticated endpoint if user is logged in via GitHub
      if (
        authState.isAuthenticated &&
        inputMethod === "github" &&
        selectedRepo
      ) {
        // Use selectedRepo directly instead of parsing URL
        const [owner, repo] = selectedRepo.split("/");

        res = await fetch("http://localhost:8000/query/auth", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            owner: owner,
            repo: repo,
            question: question,
            access_token: authState.accessToken,
          }),
        });
      } else {
        // Use regular endpoint for manual URL input
        res = await fetch("http://localhost:8000/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ repo_url: repoUrl, question }),
        });
      }

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResponse(data.answer);
        setRetrievedChunks(data.retrieved_chunks); // Store chunks
      }
    } catch (err) {
      setError("Something went wrong: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const savedAuth = localStorage.getItem("github_auth");
    if (savedAuth) {
      try {
        const authData = JSON.parse(savedAuth);
        setAuthState({
          isAuthenticated: true,
          user: authData.user,
          accessToken: authData.access_token,
          userRepos: [],
        });
        fetchUserRepos(authData.access_token);
      } catch (error) {
        console.error("Failed to parse saved auth:", error);
        localStorage.removeItem("github_auth");
      }
    }
  }, []);

  const exampleQuestions = [
    "How many total PRs are there and what are the statuses of it?",
    "How many total commits are there?",
    "When was PR # 2 opened? Tell me the date exactly?",
    "Give me all comments along with total count from my second PR.",
    "Give me all comments along with total count from my second PR. Also tell what comments were done my me if any and what comments other Authors did?"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#21262d] text-white relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/5 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-purple-500/5 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-32 left-1/4 w-40 h-40 bg-green-500/5 rounded-full blur-xl animate-pulse delay-2000"></div>

        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-5">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0)",
              backgroundSize: "20px 20px",
            }}
          ></div>
        </div>
      </div>

      {/* Header */}
      <header className="relative z-10 p-6 border-b border-gray-700/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-lg font-bold">🤖</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                CodeReview Genie
              </h1>
              <p className="text-sm text-gray-400">
                AI-Powered Repository Analysis
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-600 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Title Section */}
          <div
            className={`text-center mb-8 transform transition-all duration-1000 ${
              isVisible
                ? "translate-y-0 opacity-100"
                : "translate-y-10 opacity-0"
            }`}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-blue-600 bg-clip-text text-transparent">
              Ask the Genie
            </h2>
            <p className="text-gray-300 text-lg">
              Enter a GitHub repository URL and ask any question about its code,
              commits, or structure
            </p>
          </div>

          {/* Query Form */}
          <div
            className={`space-y-6 mb-8 transform transition-all duration-1000 delay-300 ${
              isVisible
                ? "translate-y-0 opacity-100"
                : "translate-y-10 opacity-0"
            }`}
          >
            {/* Input Method Toggle */}
            <div className="flex space-x-4 mb-6">
              <button
                onClick={() => setInputMethod("github")}
                className={`px-4 py-2 rounded-lg transition-all duration-300 ${
                  inputMethod === "github"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800/50 text-gray-400 hover:text-white"
                }`}
              >
                🔐 GitHub Auth
              </button>
              <button
                onClick={() => setInputMethod("manual")}
                className={`px-4 py-2 rounded-lg transition-all duration-300 ${
                  inputMethod === "manual"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-800/50 text-gray-400 hover:text-white"
                }`}
              >
                🔗 Manual URL
              </button>
            </div>

            {/* GitHub Authentication Section */}
            {inputMethod === "github" && (
              <div className="space-y-4">
                {!authState.isAuthenticated ? (
                  <div className="text-center p-8 rounded-xl bg-gray-900/50 border border-gray-700/50">
                    <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <svg
                        className="w-8 h-8"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">
                      Connect with GitHub
                    </h3>
                    <p className="text-gray-400 mb-6">
                      Access your repositories and get personalized insights
                    </p>
                    <button
                      onClick={handleGitHubAuth}
                      disabled={loadingAuth}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 disabled:opacity-50"
                    >
                      {loadingAuth ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2 inline-block"></div>
                          Connecting...
                        </>
                      ) : (
                        "🚀 Authorize with GitHub"
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* User Info */}
                    <div className="flex items-center justify-between p-4 rounded-xl bg-green-900/20 border border-green-500/30">
                      <div className="flex items-center space-x-3">
                        <img
                          src={authState.user?.avatar_url}
                          alt="Avatar"
                          className="w-10 h-10 rounded-full"
                        />
                        <div>
                          <p className="font-semibold text-green-400">
                            Connected as @{authState.user?.login}
                          </p>
                          <p className="text-sm text-gray-400">
                            {authState.user?.name}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={handleLogout}
                        className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                      >
                        Logout
                      </button>
                    </div>

                    {/* Repository Selection */}
                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-300 mb-2 mt-2 flex items-center">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                        Select Repository
                      </label>
                      {loadingRepos ? (
                        <div className="p-4 text-center text-gray-400">
                          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                          Loading your repositories...
                        </div>
                      ) : (
                        <select
                          value={selectedRepo}
                          onChange={(e) => handleRepoSelect(e.target.value)}
                          className="w-full px-4 py-4 rounded-xl bg-gray-900/50 border border-gray-700/50 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 backdrop-blur-sm transition-all duration-300"
                        >
                          <option
                            value=""
                            className="bg-gray-900 text-gray-400"
                          >
                            Choose a repository...
                          </option>
                          {authState.userRepos.map((repo) => (
                            <option
                              key={repo.id}
                              value={repo.full_name}
                              className="bg-gray-900 text-white"
                            >
                              {repo.name} {repo.private ? "🔒" : "📂"} (
                              {repo.language || "Unknown"})
                            </option>
                          ))}
                        </select>
                      )}
                      {authState.userRepos.length === 0 && !loadingRepos && (
                        <p className="mt-2 text-sm text-gray-400">
                          No repositories found
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Manual URL Input */}
            {inputMethod === "manual" && (
              <div className="relative">
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center">
                  <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                  GitHub Repository URL
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="https://github.com/username/repository"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="w-full px-4 py-4 pl-12 rounded-xl bg-gray-900/50 border border-gray-700/50 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 backdrop-blur-sm transition-all duration-300"
                  />
                  <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <svg
                      className="w-5 h-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            )}

            {/* Question Input - Same for both methods */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center">
                <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
                Your Question
              </label>
              <textarea
                rows={4}
                placeholder="What would you like to know about this repository?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full px-4 py-4 rounded-xl bg-gray-900/50 border border-gray-700/50 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 backdrop-blur-sm transition-all duration-300 resize-none"
              ></textarea>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={
                loading ||
                !question.trim() ||
                (inputMethod === "github" ? !selectedRepo : !repoUrl.trim())
              }
              className="group relative w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 font-semibold transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-blue-500/25"
            >
              <span className="relative z-10 flex items-center justify-center">
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Analyzing Repository...
                  </>
                ) : (
                  <>
                    <span>✨ Ask the Genie</span>
                    <span className="ml-2 group-hover:translate-x-1 transition-transform duration-300">
                      →
                    </span>
                  </>
                )}
              </span>
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 blur opacity-30 group-hover:opacity-50 transition-opacity duration-300"></div>
            </button>
          </div>

          {/* Example Questions */}
          {!response && !error && (
            <div
              className={`mb-8 transform transition-all duration-1000 delay-500 ${
                isVisible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-10 opacity-0"
              }`}
            >
              <h3 className="text-lg font-semibold mb-4 text-gray-300 flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                Example Questions
              </h3>
              <div className="grid md:grid-cols-2 gap-3">
                {exampleQuestions.map((q, index) => (
                  <button
                    key={index}
                    onClick={() => setQuestion(q)}
                    className="text-left p-3 rounded-lg bg-gray-800/30 border border-gray-700/30 hover:border-gray-600/50 hover:bg-gray-800/50 transition-all duration-300 text-sm text-gray-300 hover:text-white group"
                  >
                    <span className="text-blue-400 mr-2 group-hover:text-blue-300">
                      💡
                    </span>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-900/20 border border-red-500/30 backdrop-blur-sm animate-fadeIn">
              <div className="flex items-center">
                <span className="text-red-400 text-xl mr-3">⚠️</span>
                <div>
                  <h4 className="font-semibold text-red-400 mb-1">Error</h4>
                  <p className="text-red-300 font-mono text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Response */}
          {response && (
            <div
              className={`transition-all duration-300 ${
                showChunks
                  ? "grid grid-cols-5 gap-6" // 5-column grid: 2 for response, 3 for chunks
                  : "grid grid-cols-1"
              }`}
            >
              {/* Response Panel */}
              <div
                className={`${
                  showChunks ? "col-span-2" : "col-span-1"
                } p-6 rounded-xl bg-gradient-to-r from-gray-900/50 to-gray-800/50 border border-gray-700/50 backdrop-blur-sm animate-fadeIn`}
              >
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center mr-3">
                    <span className="text-sm">🧞</span>
                  </div>
                  <h3 className="text-xl font-semibold text-green-400">
                    Genie's Response
                  </h3>
                  <div className="ml-auto flex space-x-2">
                    {retrievedChunks && (
                      <button
                        onClick={() => setShowChunks(!showChunks)}
                        className={`px-3 py-1 text-sm rounded-lg transition-all duration-300 ${
                          showChunks
                            ? "bg-blue-600 text-white"
                            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                      >
                        {showChunks ? "Hide Chunks" : "Show Chunks"}
                      </button>
                    )}
                    <button className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700/50">
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
                <div className="bg-[#0d1117] rounded-lg p-4 border border-gray-700/30">
                  <pre className="whitespace-pre-wrap break-words text-gray-200 leading-relaxed font-mono text-sm">
                    {response}
                  </pre>
                </div>
              </div>

              {/* Chunks Panel - Wider and Taller */}
              {showChunks && retrievedChunks && (
                <div className="col-span-3 p-6 rounded-xl bg-gradient-to-r from-gray-900/50 to-gray-800/50 border border-gray-700/50 backdrop-blur-sm animate-fadeIn">
                  <div className="flex items-center mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-sm">📋</span>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-400">
                      Retrieved Chunks ({retrievedChunks.length})
                    </h3>
                    <div className="ml-auto flex space-x-2">
                      <button
                        onClick={() =>
                          navigator.clipboard.writeText(
                            JSON.stringify(retrievedChunks, null, 2)
                          )
                        }
                        className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700/50"
                        title="Copy JSON"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={() => setShowChunks(false)}
                        className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-700/50"
                        title="Close Chunks"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  {/* Better formatted chunks display */}
                  <div className="bg-[#0d1117] rounded-lg border border-gray-700/30 h-[70vh] overflow-y-auto">
                    <div className="p-4 space-y-6">
                      {retrievedChunks.map((chunk, index) => (
                        <div
                          key={index}
                          className="border-b border-gray-700/30 pb-4 last:border-b-0"
                        >
                          <div className="flex items-center mb-2">
                            <span className="text-purple-400 font-semibold text-sm">
                              Chunk #{chunk.chunk_number}
                            </span>
                            {chunk.score && (
                              <span className="ml-2 text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded">
                                Score: {chunk.score?.toFixed(3)}
                              </span>
                            )}
                          </div>
                          <div className="bg-gray-800/30 rounded p-4 border border-gray-600/30">
                            <pre className="whitespace-pre-wrap break-words text-gray-200 text-sm leading-relaxed font-mono">
                              {chunk.content}
                            </pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Raw JSON toggle */}
                  <div className="mt-4">
                    <details className="group">
                      <summary className="cursor-pointer text-sm text-gray-400 hover:text-gray-300 transition-colors">
                        <span className="group-open:rotate-90 inline-block transition-transform mr-1">
                          ▶
                        </span>
                        View Raw JSON
                      </summary>
                      <div className="mt-2 bg-gray-800/50 rounded p-3 border border-gray-600/30">
                        <pre className="text-xs text-gray-300 leading-relaxed max-h-40 overflow-y-auto">
                          {JSON.stringify(retrievedChunks, null, 2)}
                        </pre>
                      </div>
                    </details>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-gray-900 p-8 rounded-2xl border border-gray-700 text-center max-w-md mx-4">
            <div className="w-16 h-16 mx-auto mb-4 relative">
              <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <h3 className="text-xl font-semibold mb-2">
              🧞‍♂️ Genie is thinking...
            </h3>
            <p className="text-gray-400">
              Analyzing repository and preparing your answer
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default QueryPage;
