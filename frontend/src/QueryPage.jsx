import { useState } from 'react';

function QueryPage() {
  const [repoUrl, setRepoUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResponse(null);

    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, question })
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResponse(data.answer);
      }
    } catch (err) {
      setError('Something went wrong.', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-white flex flex-col items-center justify-center px-4">
      <h1 className="text-4xl font-bold mb-6">Query GitHub Repo</h1>

      <div className="w-full max-w-2xl space-y-4">
        <input
          type="text"
          placeholder="Enter GitHub Repo URL"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-[#161b22] border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <textarea
          rows={4}
          placeholder="Ask a question about the repo..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-[#161b22] border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        ></textarea>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 font-semibold transition duration-300 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Submit Query'}
        </button>
      </div>

      {error && (
        <div className="mt-6 text-red-500 font-mono">{error}</div>
      )}

      {response && (
        <div className="mt-6 bg-[#161b22] border border-gray-700 p-4 rounded-lg w-full max-w-2xl">
          <h2 className="text-lg font-semibold mb-2 text-purple-400">Genie’s Response:</h2>
          <pre className="whitespace-pre-wrap break-words text-gray-300">{response}</pre>
        </div>
      )}
    </div>
  );
}

export default QueryPage;
