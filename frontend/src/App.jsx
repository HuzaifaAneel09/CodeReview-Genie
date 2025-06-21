import { useState, useEffect } from 'react';

function App() {
  const handleStartQuerying = () => {
    console.log('Navigate to /query');
  };

  const [isVisible, setIsVisible] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const quotes = [
    "Code is poetry written for machines.",
    "The best code is no code at all.",
    "Clean code always looks like it was written by someone who cares.",
    "First, solve the problem. Then, write the code.",
    "Code never lies, comments sometimes do.",
    "Programs must be written for people to read.",
    "Debugging is twice as hard as writing code.",
    "Good code is its own best documentation.",
    "The most important property: does it work?",
    "Simplicity is the ultimate sophistication."
    ];

    const [currentQuote, setCurrentQuote] = useState(() => {
        return quotes[Math.floor(Math.random() * quotes.length)];
    });

  useEffect(() => {
    setIsVisible(true);
    
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    { icon: "🔍", title: "Smart Analysis", desc: "Deep code review insights" },
    { icon: "⚡", title: "Lightning Fast", desc: "Instant responses" },
    { icon: "🎯", title: "Precise Feedback", desc: "Targeted suggestions" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#161b22] to-[#21262d] text-white overflow-hidden relative">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Floating orbs */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-purple-500/10 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-32 left-1/4 w-40 h-40 bg-green-500/10 rounded-full blur-xl animate-pulse delay-2000"></div>
        
        {/* Animated grid pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0)',
            backgroundSize: '20px 20px'
          }}></div>
        </div>
      </div>

      {/* Mouse follower */}
      <div 
        className="fixed w-6 h-6 bg-blue-500/20 rounded-full blur-sm pointer-events-none transition-all duration-300 ease-out z-50"
        style={{
          left: mousePosition.x - 12,
          top: mousePosition.y - 12,
          transform: `scale(${mousePosition.x > 0 ? 1 : 0})`
        }}
      ></div>

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-6 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-sm font-bold">CG</span>
            </div>
            <span className="font-semibold">CodeReview Genie</span>
          </div>
          <nav className="hidden md:flex space-x-6">
            <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
            <a href="#about" className="text-gray-300 hover:text-white transition-colors">About</a>
            <a href="#contact" className="text-gray-300 hover:text-white transition-colors">Contact</a>
          </nav>
        </header>

        {/* Hero Section */}
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-4xl mx-auto text-center">
            {/* Main heading with stagger animation */}
            <div className={`transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-blue-600 bg-clip-text text-transparent leading-tight">
                🤖 CodeReview
                <br />
                <span className="inline-block animate-bounce">Genie</span>
              </h1>
            </div>

            {/* Subtitle */}
            <div className={`transform transition-all duration-1000 delay-300 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <p className="mb-8 text-gray-300 text-xl md:text-2xl max-w-2xl mx-auto">
                Your AI-powered assistant for 
                <span className="text-blue-400 font-semibold"> intelligent </span>
                Pull Request insights and code analysis
              </p>
            </div>

            {/* CTA Button */}
            <div className={`transform transition-all duration-1000 delay-500 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <button
                onClick={handleStartQuerying}
                className="group relative px-8 py-4 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 hover:shadow-blue-500/25"
              >
                <span className="relative z-10 flex items-center">
                  Start Querying 
                  <span className="ml-2 group-hover:translate-x-1 transition-transform duration-300">→</span>
                </span>
                <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 blur opacity-30 group-hover:opacity-50 transition-opacity duration-300"></div>
              </button>
            </div>

            {/* Features Grid */}
            <div className={`mt-16 transform transition-all duration-1000 delay-700 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
                {features.map((feature, index) => (
                  <div 
                    key={index}
                    className="group p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-blue-500/50 hover:bg-white/10 transition-all duration-300 transform hover:scale-105"
                    style={{ animationDelay: `${index * 200}ms` }}
                  >
                    <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
                      {feature.icon}
                    </div>
                    <h3 className="font-semibold mb-2 text-white">{feature.title}</h3>
                    <p className="text-gray-400 text-sm">{feature.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Code snippet showcase */}
            <div className={`mt-16 transform transition-all duration-1000 delay-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
                <div className="max-w-2xl mx-auto">
                    <div className="relative p-6 rounded-2xl bg-[#0d1117] border border-gray-700/50 shadow-2xl">
                    <div className="flex items-center mb-4">
                        <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        </div>
                        <span className="ml-4 text-sm text-gray-400">CodeReview Genie Terminal</span>
                    </div>
                    <div className="font-mono text-sm text-left">
                        <div className="text-green-400">$ ask-genie "What are the top commits in this PR?"</div>
                        <div className="mt-2 text-blue-400">✨ Analyzing PR #247...</div>
                        <div className="mt-1 text-white">📊 Found 12 total commits</div>
                        <div className="mt-1 text-purple-400">🏆 Top commits: feat/auth, fix/validation, docs/readme</div>
                        <div className="mt-1 text-yellow-400">📈 +2,847 lines, -1,203 lines</div>
                        <div className="mt-2 flex items-center">
                        <span className="text-green-400">✓ </span>
                        <div className="ml-1 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse" style={{ width: '75%' }}></div>
                        </div>
                    </div>
                    </div>
                </div>
            </div>
          </div>
        </main>

        {/* Quote of the Day - Bottom Left */}
        <div className="fixed bottom-8 left-8 max-w-xs z-20">
            <div className={`transform transition-all duration-1000 delay-1200 ${isVisible ? 'translate-x-0 opacity-100' : '-translate-x-10 opacity-0'}`}>
                <div className="relative p-4 rounded-lg bg-gray-900/80 backdrop-blur border border-cyan-500/30 shadow-lg">
                <div className="flex items-center mb-2">
                    <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse mr-2"></div>
                    <span className="text-cyan-400 text-xs font-mono tracking-wider">Quote of the Day</span>
                    <button 
                    onClick={() => {
                        setCurrentQuote(quotes[Math.floor(Math.random() * quotes.length)]);
                    }}
                    className="ml-auto text-cyan-400 hover:text-cyan-300 transition-colors text-xs"
                    >
                    🔄
                    </button>
                </div>
                <blockquote>
                    <p className="text-sm font-mono text-white/90 leading-relaxed" style={{ fontFamily: 'Courier New, monospace' }}>
                    "{currentQuote}"
                    </p>
                    <footer className="mt-2 text-cyan-300/50 text-xs font-mono text-right">
                    <span className="inline-block w-4 h-px bg-cyan-400/50 mr-1"></span>
                    SYS.v2.1
                    </footer>
                </blockquote>
                </div>
            </div>
        </div>

        {/* Footer */}
        <footer className="p-6 text-center text-gray-400 text-sm">
          <div className="flex justify-center items-center space-x-4">
            <span>Built with ❤️ for developers</span>
            <div className="w-px h-4 bg-gray-600"></div>
            <span>Powered by Nueral Nets</span>
          </div>
        </footer>
      </div>

      {/* Floating action elements */}
      <div className="fixed bottom-8 right-8 flex space-x-4">
        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform cursor-pointer">
          <span className="text-xl">💬</span>
        </div>
      </div>
    </div>
  );
}

export default App;