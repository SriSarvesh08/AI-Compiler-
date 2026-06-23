"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const SECTION = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="glass-card" style={{ padding: 28, marginBottom: 20 }}>
    <h2 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 20, paddingBottom: 14, borderBottom: "1px solid var(--color-border)" }}
      className="dark:border-[var(--color-dark-border)]">{title}</h2>
    {children}
  </div>
);

const ROW = ({ label, desc, children }: { label: string; desc?: string; children: React.ReactNode }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 20, marginBottom: 20 }}>
    <div>
      <div style={{ fontSize: "0.9rem", fontWeight: 600 }}>{label}</div>
      {desc && <div style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", marginTop: 2 }}>{desc}</div>}
    </div>
    {children}
  </div>
);

const SELECT = ({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    style={{
      padding: "8px 12px", borderRadius: 9,
      border: "1.5px solid var(--color-border)",
      background: "var(--color-bg-input)",
      fontSize: "0.88rem", fontWeight: 500,
      color: "var(--color-text-primary)",
      cursor: "pointer", outline: "none",
      minWidth: 160,
    }}
    className="dark:border-[var(--color-dark-border)] dark:bg-[var(--color-dark-bg-input)]"
  >
    {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

const TOGGLE = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <button
    onClick={() => onChange(!checked)}
    style={{
      width: 44, height: 24, borderRadius: 12,
      background: checked ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "var(--color-border)",
      border: "none", cursor: "pointer", position: "relative", transition: "all 0.3s",
      flexShrink: 0,
    }}
  >
    <div style={{
      width: 18, height: 18, borderRadius: "50%", background: "white",
      position: "absolute", top: 3, left: checked ? 23 : 3,
      transition: "left 0.3s", boxShadow: "0 1px 4px rgba(0,0,0,0.2)",
    }} />
  </button>
);

export default function SettingsPage() {
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const [saved, setSaved] = useState(false);

  // Settings state
  const [model, setModel] = useState("gemini");
  const [runtimeMode, setRuntimeMode] = useState("simulation");
  const [exportJson, setExportJson] = useState(true);
  const [exportValidation, setExportValidation] = useState(true);
  const [exportEvaluation, setExportEvaluation] = useState(false);
  const [autoRepair, setAutoRepair] = useState(true);
  const [showPipelineAnimations, setShowPipelineAnimations] = useState(true);
  const [defaultTab, setDefaultTab] = useState("overview");

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    async function fetchUser() {
      const token = localStorage.getItem("auth_token");
      if (!token) return;
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUser({ name: data.name, email: data.email });
          if (data.settings) {
            setModel(data.settings.model || "gemini");
            setRuntimeMode(data.settings.runtimeMode || "simulation");
            setExportJson(data.settings.exportJson ?? true);
            setExportValidation(data.settings.exportValidation ?? true);
            setExportEvaluation(data.settings.exportEvaluation ?? false);
            setAutoRepair(data.settings.autoRepair ?? true);
            setShowPipelineAnimations(data.settings.showPipelineAnimations ?? true);
            setDefaultTab(data.settings.defaultTab || "overview");
          }
        } else {
          localStorage.removeItem("auth_token");
        }
      } catch (err) {}
    }
    fetchUser();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const token = localStorage.getItem("auth_token");
      if (token) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/user/settings`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            model, runtimeMode, exportJson, exportValidation, exportEvaluation, autoRepair, showPipelineAnimations, defaultTab
          })
        });
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("mock_user");
    setUser(null);
  };

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: "40px 24px 80px" }}>
      {/* Header */}
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: "clamp(1.5rem, 4vw, 2rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 8 }}>
          Settings
        </h1>
        <p style={{ color: "var(--color-text-secondary)", fontSize: "0.92rem" }}>
          Configure your preferences. UI-only — does not affect the Gemini backend integration.
        </p>
      </div>

      {/* Profile Section */}
      <SECTION title="Profile">
        {user ? (
          <div style={{ display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap" }}>
            <div style={{
              width: 64, height: 64, borderRadius: "50%",
              background: "linear-gradient(135deg,#6366f1,#a855f7)",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "white", fontWeight: 800, fontSize: "1.4rem",
              flexShrink: 0, boxShadow: "0 4px 16px rgba(99,102,241,0.35)",
            }}>
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: "1.1rem", marginBottom: 2 }}>{user.name}</div>
              <div style={{ fontSize: "0.88rem", color: "var(--color-text-secondary)" }}>{user.email}</div>
              <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ fontSize: "0.72rem", padding: "2px 10px", background: "var(--color-success-bg)", color: "var(--color-success)", borderRadius: 999, fontWeight: 700 }}>Real Account</span>
                <span style={{ fontSize: "0.72rem", color: "var(--color-text-muted)" }}>· Logged in via backend auth</span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              style={{
                padding: "8px 18px", borderRadius: 9,
                border: "1.5px solid var(--color-border)",
                background: "transparent", cursor: "pointer",
                fontSize: "0.85rem", fontWeight: 600,
                color: "var(--color-error)", transition: "all 0.2s",
              }}
            >
              Sign out
            </button>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <div style={{ fontSize: "0.9rem", color: "var(--color-text-muted)", marginBottom: 16 }}>You are not signed in.</div>
            <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
              <Link href="/login" style={{ padding: "9px 20px", borderRadius: 9, border: "1.5px solid var(--color-border)", textDecoration: "none", fontSize: "0.88rem", fontWeight: 600, color: "var(--color-text-primary)" }}>Log in</Link>
              <Link href="/register" style={{ padding: "9px 20px", borderRadius: 9, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", textDecoration: "none", fontSize: "0.88rem", fontWeight: 600, color: "white" }}>Sign up</Link>
            </div>
          </div>
        )}
      </SECTION>

      {/* Model Preferences */}
      <SECTION title="AI Model Preference">
        <div style={{ padding: "10px 0" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginBottom: 16, padding: "10px 14px", background: "var(--color-accent-glow)", borderRadius: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <span style={{ color: "var(--color-accent)", fontWeight: 500 }}>Now connected to backend. Ensure you have the respective API keys in the backend .env file.</span>
          </div>
          <ROW label="Default Model" desc="Which AI model to use for the compiler pipeline">
            <SELECT
              value={model}
              onChange={setModel}
              options={[
                { value: "gemini", label: "Gemini (Active)" },
                { value: "openai", label: "OpenAI GPT-4" },
                { value: "claude", label: "Claude 3.5 Sonnet" },
              ]}
            />
          </ROW>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 8 }}>
            {[
              { id: "gemini", name: "Gemini", provider: "Google DeepMind", badge: "Active", badgeColor: "var(--color-success)" },
              { id: "openai", name: "GPT-4o", provider: "OpenAI", badge: "Active", badgeColor: "var(--color-success)" },
              { id: "claude", name: "Claude 3.5", provider: "Anthropic", badge: "Active", badgeColor: "var(--color-success)" },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => setModel(m.id)}
                style={{
                  padding: "16px", borderRadius: 12,
                  border: `2px solid ${model === m.id ? "var(--color-accent)" : "var(--color-border)"}`,
                  background: model === m.id ? "var(--color-accent-glow)" : "transparent",
                  cursor: "pointer", textAlign: "left", transition: "all 0.2s",
                }}
              >
                <div style={{ fontWeight: 700, fontSize: "0.9rem", marginBottom: 4 }}>{m.name}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: 8 }}>{m.provider}</div>
                <span style={{ fontSize: "0.68rem", padding: "2px 8px", backgroundColor: `${m.badgeColor}20`, color: m.badgeColor, borderRadius: 999, fontWeight: 700 }}>{m.badge}</span>
              </button>
            ))}
          </div>
        </div>
      </SECTION>

      {/* Runtime Settings */}
      <SECTION title="Runtime & Compiler">
        <ROW label="Runtime Mode" desc="How the compiled app is simulated after validation">
          <SELECT
            value={runtimeMode}
            onChange={setRuntimeMode}
            options={[
              { value: "simulation", label: "Simulation" },
              { value: "visual", label: "Visual Preview" },
            ]}
          />
        </ROW>
        <ROW label="Auto-Repair" desc="Automatically attempt to fix validation errors">
          <TOGGLE checked={autoRepair} onChange={setAutoRepair} />
        </ROW>
        <ROW label="Pipeline Animations" desc="Show animated transitions in the pipeline visualizer">
          <TOGGLE checked={showPipelineAnimations} onChange={setShowPipelineAnimations} />
        </ROW>
        <ROW label="Default Output Tab" desc="Which tab to open after a successful pipeline run">
          <SELECT
            value={defaultTab}
            onChange={setDefaultTab}
            options={[
              { value: "overview", label: "Overview" },
              { value: "runtime", label: "Runtime Preview" },
              { value: "json_output", label: "JSON Output" },
              { value: "validation", label: "Validation" },
            ]}
          />
        </ROW>
      </SECTION>

      {/* Export Preferences */}
      <SECTION title="Export Preferences">
        <p style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", marginBottom: 20 }}>
          Choose what to include when exporting pipeline results.
        </p>
        <ROW label="Export JSON Output" desc="Full pipeline output: UI, API, DB, Auth schemas">
          <TOGGLE checked={exportJson} onChange={setExportJson} />
        </ROW>
        <ROW label="Export Validation Report" desc="Error and warning details from the validation stage">
          <TOGGLE checked={exportValidation} onChange={setExportValidation} />
        </ROW>
        <ROW label="Export Evaluation Metrics" desc="Success rates, latency, and repair statistics">
          <TOGGLE checked={exportEvaluation} onChange={setExportEvaluation} />
        </ROW>
      </SECTION>

      {/* About */}
      <SECTION title="About">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          {[
            { label: "Version", value: "v0.2.0" },
            { label: "Pipeline Stages", value: "6" },
            { label: "Supported Schemas", value: "UI, API, DB, Auth" },
            { label: "Evaluation Cases", value: "10+ test prompts" },
          ].map((item) => (
            <div key={item.label} style={{ padding: "14px 16px", backgroundColor: "var(--color-bg-secondary)", borderRadius: 10 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
              <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", fontWeight: 500, marginBottom: 4 }}>{item.label}</div>
              <div style={{ fontSize: "0.92rem", fontWeight: 700 }}>{item.value}</div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 20, padding: "14px 16px", backgroundColor: "var(--color-bg-secondary)", borderRadius: 10 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
          <div style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", marginBottom: 6, fontWeight: 500 }}>Important Notice</div>
          <p style={{ fontSize: "0.82rem", color: "var(--color-text-secondary)", margin: 0, lineHeight: 1.6 }}>
            This system generates structured app specifications from natural language. It does not generate production code, real databases, real authentication, or real payment systems. The runtime preview is a simulation generated from the validated configuration schema.
          </p>
        </div>
      </SECTION>

      {/* Save button */}
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 8 }}>
        {saved && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 18px", backgroundColor: "var(--color-success-bg)", border: "1px solid var(--color-success)", borderRadius: 10, color: "var(--color-success)", fontWeight: 600, fontSize: "0.88rem" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Settings saved
          </div>
        )}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary"
          style={{ padding: "11px 28px", fontSize: "0.92rem", opacity: isSaving ? 0.7 : 1 }}
        >
          {isSaving ? "Saving..." : "Save preferences"}
        </button>
      </div>
    </div>
  );
}
