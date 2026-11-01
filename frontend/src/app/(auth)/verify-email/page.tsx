"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "../../../services/apiClient";

export default function VerifyEmailPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const resp = await apiClient<{ message: string }>("/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      setMessage(resp.data?.message || "Email successfully verified! Redirecting...");
      setTimeout(() => router.push("/profile"), 2000);
    } catch (err: any) {
      setError(err.message || "Email verification failed. Token may be expired or invalid.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center py-12 px-4 sm:px-6 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-300/30 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-sky-200/40 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-md w-full neo-box rounded-3xl p-8 sm:p-10 relative backdrop-blur-md">
        <div className="text-center mb-7">
          <Link href="/" className="inline-block group">
            <div className="w-16 h-16 mx-auto rounded-2xl neo-pill flex items-center justify-center text-3xl mb-4 group-hover:scale-105 transition-transform duration-200 shadow-sm">
              ✉️
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-800">
              Verify Your Email
            </h1>
          </Link>
          <p className="text-xs sm:text-sm text-slate-500 font-medium mt-1.5">
            Enter the 6-character or security token sent to your email.
          </p>
        </div>

        {message && (
          <div className="mb-5 p-4 bg-emerald-50/90 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-800 flex items-start gap-2.5 shadow-sm animate-fade-in">
            <svg className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="mb-5 p-3.5 bg-red-50/90 border border-red-200 rounded-xl text-xs font-semibold text-red-700 flex items-start gap-2.5 shadow-sm animate-fade-in">
            <svg className="w-4 h-4 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Verification Code / Token
            </label>
            <input
              type="text"
              required
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste token here"
              className="w-full px-4 py-3 neo-inset rounded-xl text-slate-800 placeholder-slate-400 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-400/40 transition-all font-mono text-center tracking-widest text-base"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl font-bold text-sm tracking-wide text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 shadow-lg shadow-indigo-500/25 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Validating Token...</span>
              </>
            ) : (
              <>
                <span>Confirm Email Address</span>
                <span className="text-indigo-200">→</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-300/60 text-center">
          <Link
            href="/profile"
            className="text-xs sm:text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors"
          >
            Skip for now (Go to Profile)
          </Link>
        </div>
      </div>
    </div>
  );
}
