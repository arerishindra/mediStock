"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, Lock, Mail, ArrowRight, AlertCircle, CheckCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@medistock.local");
  const [password, setPassword] = useState("Admin@123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (res?.data) {
        login(res.data.access_token, res.data);
        router.push("/");
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (userEmail: string, userPass: string) => {
    setEmail(userEmail);
    setPassword(userPass);
    setError(null);
  };

  return (
    <div className="min-h-screen flex items-center justify-center -m-8 bg-gradient-to-br from-slate-900 via-slate-850 to-slate-950 p-6 text-slate-100">
      <div className="w-full max-w-md">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-brand-600 to-teal-400 flex items-center justify-center text-white shadow-xl shadow-brand-500/20 mb-4 ring-4 ring-brand-500/20">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white">MediStock</h1>
          <p className="text-sm text-slate-400 mt-1">Pharmacy Inventory & Operations Platform</p>
        </div>

        {/* Card */}
        <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
          <h2 className="text-lg font-bold text-white mb-2">Sign in to your account</h2>
          <p className="text-xs text-slate-400 mb-6">Enter your credentials to access inventory and sales.</p>

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@medistock.local"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-900/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-teal-600 text-white font-semibold text-sm hover:from-brand-500 hover:to-teal-500 active:scale-[0.99] transition duration-150 flex items-center justify-center gap-2 shadow-lg shadow-brand-600/25 disabled:opacity-50"
            >
              {loading ? (
                <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials */}
          <div className="mt-8 pt-6 border-t border-slate-700/60">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-3">
              One-Click Demo Credentials
            </span>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <button
                type="button"
                onClick={() => fillCredentials("admin@medistock.local", "Admin@123")}
                className="p-2 rounded-lg bg-slate-900/60 border border-slate-700/50 hover:border-brand-500/60 text-left transition"
              >
                <div className="font-semibold text-brand-300 text-[11px]">Admin (.local)</div>
                <div className="text-[10px] text-slate-500">System Admin</div>
              </button>
              <button
                type="button"
                onClick={() => fillCredentials("admin@medistock.com", "Admin@123")}
                className="p-2 rounded-lg bg-slate-900/60 border border-slate-700/50 hover:border-brand-500/60 text-left transition"
              >
                <div className="font-semibold text-brand-300 text-[11px]">Admin (.com)</div>
                <div className="text-[10px] text-slate-500">System Admin</div>
              </button>
              <button
                type="button"
                onClick={() => fillCredentials("admin@test.com", "Admin@123")}
                className="p-2 rounded-lg bg-slate-900/60 border border-slate-700/50 hover:border-brand-500/60 text-left transition"
              >
                <div className="font-semibold text-brand-300 text-[11px]">Test Admin</div>
                <div className="text-[10px] text-slate-500">Test Suite</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
