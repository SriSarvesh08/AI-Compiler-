"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useGoogleLogin } from "@react-oauth/google";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError("Please fill in all fields."); return; }
    setIsLoading(true);
    setError("");
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || "Login failed");
        setIsLoading(false);
        return;
      }
      localStorage.setItem("auth_token", data.access_token);
      localStorage.setItem("mock_user", JSON.stringify(data.user)); // Still used by UI for avatar
      router.push("/travel");
    } catch (err) {
      setError("Failed to connect to server");
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = useGoogleLogin({
    flow: "implicit",
    onSuccess: async (tokenResponse) => {
      setIsLoading(true);
      setError("");
      try {
        // Exchange Google access token for an ID token by calling userinfo and then our backend
        const userInfoRes = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });
        const userInfo = await userInfoRes.json();
        
        // Send the access_token to our backend /auth/google endpoint
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: tokenResponse.access_token }),
        });
        const data = await res.json();
        if (!res.ok) {
          setError(data.detail || "Google login failed");
          setIsLoading(false);
          return;
        }
        localStorage.setItem("auth_token", data.access_token);
        localStorage.setItem("mock_user", JSON.stringify(data.user));
        router.push("/travel");
      } catch (err) {
        setError("Failed to connect to server");
        setIsLoading(false);
      }
    },
    onError: () => {
      setError("Google login was cancelled or failed.");
    },
  });

  return (
    <div style={{
      minHeight: "calc(100vh - 64px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "40px 24px",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Background blobs */}
      <div aria-hidden style={{ position: "absolute", top: "10%", left: "15%", width: 500, height: 500, background: "radial-gradient(ellipse, rgba(99,102,241,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />
      <div aria-hidden style={{ position: "absolute", bottom: "10%", right: "10%", width: 400, height: 400, background: "radial-gradient(ellipse, rgba(168,85,247,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />

      <div style={{ width: "100%", maxWidth: 420, position: "relative" }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <Link href="/" style={{ display: "inline-flex", alignItems: "center", gap: 10, textDecoration: "none", marginBottom: 24 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg,#6366f1,#a855f7)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 800, fontSize: "1rem", boxShadow: "0 4px 16px rgba(99,102,241,0.4)" }}>AI</div>
            <span style={{ fontWeight: 800, fontSize: "1.15rem", letterSpacing: "-0.02em" }}>AI Compiler</span>
          </Link>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 6 }}>Welcome back</h1>
          <p style={{ color: "var(--color-text-secondary)", fontSize: "0.9rem" }}>Sign in to access your projects</p>
        </div>

        <div className="glass-card" style={{ padding: 32 }}>
          {/* Google button */}
          <button
            type="button"
            suppressHydrationWarning
            onClick={() => handleGoogleLogin()}
            disabled={isLoading}
            style={{
              width: "100%", padding: "11px 16px", borderRadius: 10,
              border: "1.5px solid var(--color-border)", background: "transparent",
              cursor: "pointer", fontSize: "0.92rem", fontWeight: 600,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              marginBottom: 20, transition: "all 0.2s",
            }}
            className="dark:border-[var(--color-dark-border)]"
          >
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
            <div style={{ flex: 1, height: 1, backgroundColor: "var(--color-border)" }} />
            <span style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", fontWeight: 500 }}>or continue with email</span>
            <div style={{ flex: 1, height: 1, backgroundColor: "var(--color-border)" }} />
          </div>

          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 600, marginBottom: 6 }}>Email address</label>
              <input
                suppressHydrationWarning
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                style={{
                  width: "100%", padding: "11px 14px", borderRadius: 9,
                  border: "1.5px solid var(--color-border)",
                  background: "var(--color-bg-input)",
                  fontSize: "0.92rem", color: "var(--color-text-primary)",
                  outline: "none", boxSizing: "border-box", transition: "all 0.2s",
                }}
                className="dark:border-[var(--color-dark-border)] dark:bg-[var(--color-dark-bg-input)]"
              />
            </div>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <label style={{ fontSize: "0.82rem", fontWeight: 600 }}>Password</label>
                <button type="button" style={{ fontSize: "0.78rem", color: "var(--color-accent)", background: "none", border: "none", cursor: "pointer", fontWeight: 600 }}>Forgot password?</button>
              </div>
              <div style={{ position: "relative" }}>
                <input
                  suppressHydrationWarning
                  type={showPw ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  style={{
                    width: "100%", padding: "11px 44px 11px 14px", borderRadius: 9,
                    border: "1.5px solid var(--color-border)",
                    background: "var(--color-bg-input)",
                    fontSize: "0.92rem", color: "var(--color-text-primary)",
                    outline: "none", boxSizing: "border-box", transition: "all 0.2s",
                  }}
                  className="dark:border-[var(--color-dark-border)] dark:bg-[var(--color-dark-bg-input)]"
                />
                <button suppressHydrationWarning type="button" onClick={() => setShowPw(!showPw)} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--color-text-muted)" }}>
                  {showPw ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div style={{ padding: "10px 14px", backgroundColor: "var(--color-error-bg)", border: "1px solid var(--color-error)", borderRadius: 8, color: "var(--color-error)", fontSize: "0.85rem" }}>
                {error}
              </div>
            )}

            <button
              suppressHydrationWarning
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ width: "100%", padding: "13px", fontSize: "0.95rem", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginTop: 4 }}
            >
              {isLoading ? (
                <><span style={{ width: 17, height: 17, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.8s linear infinite", display: "inline-block" }} />Signing in...</>
              ) : "Sign in"}
            </button>
          </form>

          <p style={{ textAlign: "center", marginTop: 20, fontSize: "0.85rem", color: "var(--color-text-secondary)" }}>
            Don't have an account?{" "}
            <Link href="/register" style={{ color: "var(--color-accent)", fontWeight: 700, textDecoration: "none" }}>Create one</Link>
          </p>
        </div>

        <p style={{ textAlign: "center", marginTop: 20, fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
          🔒 Secured with JWT. Google OAuth via Google Cloud Console.
        </p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
