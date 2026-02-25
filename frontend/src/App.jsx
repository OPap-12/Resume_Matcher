import { useState, useEffect } from "react";
import {
  reviewResume,
  matchResume,
  fetchHistory,
  fetchMatchHistory,
  searchResumes,
  loginUser,
  signupUser,
  logoutUser,
} from "./lib/api";

import * as jspdfModule from "jspdf";
import html2canvas from "html2canvas-pro";
import AuthModal from "./components/AuthModal";

function App() {
  const [activeTab, setActiveTab] = useState("review"); // "review" | "match"
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [matchHistory, setMatchHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem("token"),
  );
  const [showAuthModal, setShowAuthModal] = useState(false);

  const downloadPDF = async () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    try {
      const element = document.getElementById("analysis-result");
      if (!element) throw new Error("Result element not found");
      const canvas = await html2canvas(element, { scale: 2 });
      if (canvas.width === 0 || canvas.height === 0) {
        throw new Error("Canvas generated with 0 size");
      }
      const imgData = canvas.toDataURL("image/png");
      const JsPDFConstructor =
        jspdfModule.jsPDF || jspdfModule.default || window.jsPDF;
      const pdf = new JsPDFConstructor("p", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
      pdf.save("Resume_AI_Report.pdf");
    } catch (err) {
      console.error("PDF generation failed:", err);
      alert(`Failed to generate PDF. Error details: ${err.message || err}`);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      refreshHistory();
    }
  }, [isAuthenticated]);

  const refreshHistory = () => {
    fetchHistory()
      .then(setHistory)
      .catch((e) => {
        if (e.message.includes("fetch")) {
          handleLogout();
        }
      });
    fetchMatchHistory().then(setMatchHistory).catch(console.error);
    setSearchResults(null);
    setSearchQuery("");
  };

  const handleLogout = () => {
    logoutUser();
    setIsAuthenticated(false);
    setHistory([]);
    setMatchHistory([]);
    setAnalysis(null);
    setMatchResult(null);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) return setShowAuthModal(true);
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setIsSearching(true);
    try {
      const results = await searchResumes(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error(err);
      alert("Search failed or is disabled.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleReview = async () => {
    if (!isAuthenticated) return setShowAuthModal(true);
    if (!file) return setError("Please select a PDF file first!");
    setLoading(true);
    setError(null);
    setMatchResult(null);
    try {
      const data = await reviewResume(file);
      setAnalysis(data.analysis);
      setMatchResult(null);
      refreshHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!isAuthenticated) return setShowAuthModal(true);
    if (!file) return setError("Please select a PDF file first!");
    if (!jobDesc.trim()) return setError("Please enter a job description!");
    setLoading(true);
    setError(null);
    setAnalysis(null);
    try {
      const data = await matchResume(file, jobDesc.trim());
      setMatchResult(data);
      setAnalysis(null);
      refreshHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (item) => {
    setAnalysis(item.analysis);
    setMatchResult(null);
  };

  const handleMatchHistoryClick = (item) => {
    setMatchResult({
      match_score: item.match_score,
      skill_gaps: item.skill_gaps,
      improvement_suggestions: item.improvement_suggestions,
      parsed_resume: item.parsed_resume,
    });
    setAnalysis(null);
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className="w-80 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <h1 className="text-xl font-bold text-indigo-600">Resume Matcher</h1>
          <div className="flex items-center justify-between mt-1">
            <p className="text-sm text-slate-500">
              AI-powered analysis & job matching
            </p>
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="text-xs text-rose-600 hover:text-rose-800 font-medium px-2 py-1 bg-rose-50 rounded"
              >
                Logout
              </button>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium px-2 py-1 bg-indigo-50 rounded"
              >
                Login
              </button>
            )}
          </div>
        </div>
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab("review")}
            className={`flex-1 py-3 text-sm font-medium ${activeTab === "review" ? "text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50" : "text-slate-600 hover:bg-slate-50"}`}
          >
            Review
          </button>
          <button
            onClick={() => setActiveTab("match")}
            className={`flex-1 py-3 text-sm font-medium ${activeTab === "match" ? "text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50" : "text-slate-600 hover:bg-slate-50"}`}
          >
            Match Job
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-3">
            {activeTab === "review" ? "Past Reviews" : "Match History"}
          </h2>

          {activeTab === "review" && (
            <form onSubmit={handleSearch} className="mb-4 flex gap-2">
              <input
                type="text"
                placeholder="Search (e.g. 'React expert')"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 rounded border border-slate-200 px-3 py-1.5 text-sm focus:ring-1 focus:ring-indigo-500 outline-none"
              />
              <button
                type="submit"
                disabled={isSearching}
                className="bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded text-sm font-medium hover:bg-indigo-200"
              >
                {isSearching ? "..." : "Go"}
              </button>
              {searchResults && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery("");
                    setSearchResults(null);
                  }}
                  className="text-slate-400 hover:text-slate-600 px-2"
                >
                  ✕
                </button>
              )}
            </form>
          )}

          <div className="space-y-2">
            {(activeTab === "review" ? searchResults || history : matchHistory)
              .length === 0 && (
              <p className="text-sm text-slate-400 italic">No history yet</p>
            )}
            {activeTab === "review"
              ? (searchResults || history).map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleHistoryClick(item)}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:border-indigo-300 hover:bg-indigo-50/50 transition-all"
                  >
                    <p className="text-sm font-medium truncate text-slate-700">
                      {item.filename}
                    </p>
                    {item.score && (
                      <p className="text-xs text-indigo-600 font-medium">
                        Score: {item.score}
                      </p>
                    )}
                    <p className="text-xs text-slate-400">
                      {item.timestamp
                        ? new Date(item.timestamp).toLocaleDateString()
                        : "N/A"}
                    </p>
                  </div>
                ))
              : matchHistory.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleMatchHistoryClick(item)}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:border-indigo-300 hover:bg-indigo-50/50 transition-all"
                  >
                    <p className="text-sm font-medium truncate text-slate-700">
                      {item.filename}
                    </p>
                    <p className="text-xs text-indigo-600 font-medium">
                      {item.match_score}% match
                    </p>
                    <p className="text-xs text-slate-400">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                ))}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-3xl mx-auto">
          <header className="mb-8">
            <h2 className="text-2xl font-bold text-slate-800">
              {activeTab === "review" ? "Resume Review" : "Resume–Job Match"}
            </h2>
            <p className="text-slate-500 mt-1">
              {activeTab === "review"
                ? "Upload your resume for AI feedback on strengths and areas to improve"
                : "Upload your resume and paste a job description to get a match score and skill gap analysis"}
            </p>
          </header>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
            <div className="space-y-4">
              <div className="flex flex-col">
                <label className="text-sm font-medium text-slate-700 mb-2">
                  Resume (PDF)
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200"
                />
              </div>

              {activeTab === "match" && (
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-2">
                    Job Description
                  </label>
                  <textarea
                    value={jobDesc}
                    onChange={(e) => setJobDesc(e.target.value)}
                    placeholder="Paste the full job description here..."
                    rows={6}
                    className="w-full rounded-lg border border-slate-200 px-4 py-3 text-slate-700 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={activeTab === "review" ? handleReview : handleMatch}
                disabled={
                  loading || !file || (activeTab === "match" && !jobDesc.trim())
                }
                className="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all shadow-lg"
              >
                {loading
                  ? "Analyzing..."
                  : activeTab === "review"
                    ? "Review Resume"
                    : "Match with Job"}
              </button>
            </div>
          </div>

          {/* Results */}
          {(analysis || matchResult) && (
            <div className="mt-8 flex justify-end">
              <button
                onClick={downloadPDF}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg shadow transition-colors flex items-center gap-2"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
                Download PDF
              </button>
            </div>
          )}

          <div id="analysis-result">
            {analysis && (
              <div className="mt-6 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <h3 className="text-xl font-bold text-slate-800">
                  Analysis Results
                </h3>
                <div className="grid gap-4">
                  <div className="p-5 bg-emerald-50 rounded-xl border border-emerald-100">
                    <h4 className="font-bold text-emerald-700">✅ Strengths</h4>
                    <ul className="mt-2 space-y-1 text-emerald-900 list-disc ml-5">
                      {(analysis.strengths || []).map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5 bg-rose-50 rounded-xl border border-rose-100">
                    <h4 className="font-bold text-rose-700">
                      ❌ Areas for Improvement
                    </h4>
                    <ul className="mt-2 space-y-1 text-rose-900 list-disc ml-5">
                      {(analysis.weaknesses || []).map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5 bg-indigo-50 rounded-xl border border-indigo-100">
                    <h4 className="font-bold text-indigo-700">
                      💡 Suggestions
                    </h4>
                    <ul className="mt-2 space-y-1 text-indigo-900 list-disc ml-5">
                      {(analysis.suggestions || []).map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {matchResult && (
              <div className="mt-8 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-4">
                  <h3 className="text-xl font-bold text-slate-800">
                    Match Results
                  </h3>
                  <span
                    className={`px-4 py-1.5 rounded-full text-lg font-bold ${
                      matchResult.match_score >= 70
                        ? "bg-emerald-100 text-emerald-700"
                        : matchResult.match_score >= 50
                          ? "bg-amber-100 text-amber-700"
                          : "bg-rose-100 text-rose-700"
                    }`}
                  >
                    {matchResult.match_score}% Match
                  </span>
                </div>

                {matchResult.parsed_resume?.skills?.length > 0 && (
                  <div className="p-5 bg-slate-50 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700">Your Skills</h4>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {(matchResult.parsed_resume.skills || []).map((s, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-white rounded border border-slate-200 text-sm"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="p-5 bg-amber-50 rounded-xl border border-amber-100">
                  <h4 className="font-bold text-amber-700">🔍 Skill Gaps</h4>
                  <p className="text-sm text-amber-800 mt-1">
                    Skills the job needs that you may want to develop
                  </p>
                  <ul className="mt-2 space-y-1 text-amber-900 list-disc ml-5">
                    {(matchResult.skill_gaps || []).map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-5 bg-indigo-50 rounded-xl border border-indigo-100">
                  <h4 className="font-bold text-indigo-700">
                    💡 Improvement Suggestions
                  </h4>
                  <ul className="mt-2 space-y-1 text-indigo-900 list-disc ml-5">
                    {(matchResult.improvement_suggestions || []).map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onSuccess={() => {
            setIsAuthenticated(true);
            setShowAuthModal(false);
          }}
        />
      )}
    </div>
  );
}

export default App;
