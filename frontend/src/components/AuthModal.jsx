import React, { useState } from "react";
import { loginUser, signupUser } from "../lib/api";

export default function AuthModal({ onClose, onSuccess }) {
  const [authMode, setAuthMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (authMode === "login") {
        await loginUser(email, password);
        onSuccess();
      } else {
        await signupUser(email, password);
        setAuthMode("login");
        setPassword("");
        alert("Account created successfully! Please log in.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex flex-col justify-center items-center z-50 p-4 font-sans backdrop-blur-sm">
      <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-slate-200 relative animate-in fade-in zoom-in duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-2 rounded-full hover:bg-slate-100 transition-colors"
        >
          ✕
        </button>
        <h2 className="text-2xl font-bold text-indigo-600 mb-6 text-center">
          Resume Matcher
        </h2>
        <div className="flex mb-6 border-b border-slate-200">
          <button
            type="button"
            onClick={() => {
              setAuthMode("login");
              setError(null);
            }}
            className={`flex-1 py-2 text-sm font-medium ${
              authMode === "login"
                ? "text-indigo-600 border-b-2 border-indigo-600"
                : "text-slate-500"
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => {
              setAuthMode("signup");
              setError(null);
            }}
            className={`flex-1 py-2 text-sm font-medium ${
              authMode === "signup"
                ? "text-indigo-600 border-b-2 border-indigo-600"
                : "text-slate-500"
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          {error && (
            <div className="text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded">
              {error}
            </div>
          )}
          <button
            disabled={loading}
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {loading
              ? "Please wait..."
              : authMode === "login"
                ? "Login to Account"
                : "Create Account"}
          </button>
        </form>
      </div>
    </div>
  );
}
