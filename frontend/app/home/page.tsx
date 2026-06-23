"use client";

import Link from "next/link";

const features = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
      </svg>
    ),
    title: "Multi-Stage Compiler Pipeline",
    desc: "6-stage deterministic pipeline: Intent → Design → Schemas → Validation → Repair → Runtime. Every stage is logged and inspectable.",
    color: "#6366f1",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
    title: "Validation Engine",
    desc: "Catches schema inconsistencies, orphaned references, missing auth rules, and structural errors before any runtime stage.",
    color: "#10b981",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
      </svg>
    ),
    title: "Repair Engine",
    desc: "Auto-detects and corrects repairable validation errors. Iterative repair loop with diff summaries showing before/after changes.",
    color: "#f59e0b",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
    title: "Runtime Verification",
    desc: "Simulates app runtime from the validated configuration. Renders an interactive page preview with real component types.",
    color: "#8b5cf6",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
      </svg>
    ),
    title: "Evaluation Metrics",
    desc: "Run automated test suites across normal and edge-case prompts. Tracks success rate, repair rate, latency, and failure types.",
    color: "#ec4899",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="3" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" />
      </svg>
    ),
    title: "Patch Mode",
    desc: "Modify existing generated configs without rebuilding. Classifies changes and surgically re-runs only affected pipeline stages.",
    color: "#06b6d4",
  },
];

const pipeline = [
  { num: "01", label: "Intent Extraction", desc: "Parse roles, features, permissions from natural language" },
  { num: "02", label: "System Design", desc: "Generate pages, entities, API routes, DB tables" },
  { num: "03", label: "Schema Generation", desc: "Produce UI, API, DB, and Auth schemas" },
  { num: "04", label: "Validation", desc: "Check consistency, references, and rules" },
  { num: "05", label: "Repair Engine", desc: "Auto-fix repairable errors iteratively" },
  { num: "06", label: "Runtime Simulation", desc: "Verify and render interactive preview" },
];

export default function LandingPage() {
  return (
    <div style={{ overflowX: "hidden" }}>
      {/* ── Hero ── */}
      <section
        style={{
          minHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "80px 24px 60px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Background gradient blobs */}
        <div
          aria-hidden
          style={{
            position: "absolute",
            top: "-10%",
            left: "50%",
            transform: "translateX(-50%)",
            width: 900,
            height: 600,
            background:
              "radial-gradient(ellipse at center, rgba(99,102,241,0.12) 0%, rgba(168,85,247,0.06) 50%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
        <div
          aria-hidden
          style={{
            position: "absolute",
            bottom: "-5%",
            left: "10%",
            width: 400,
            height: 400,
            background: "radial-gradient(ellipse at center, rgba(16,185,129,0.07) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
        <div
          aria-hidden
          style={{
            position: "absolute",
            top: "20%",
            right: "5%",
            width: 300,
            height: 300,
            background: "radial-gradient(ellipse at center, rgba(236,72,153,0.06) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />

        {/* Badge */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 16px",
            borderRadius: 999,
            border: "1px solid rgba(99,102,241,0.3)",
            background: "rgba(99,102,241,0.08)",
            fontSize: "0.82rem",
            fontWeight: 600,
            color: "#6366f1",
            marginBottom: 28,
          }}
        >
          <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#6366f1", display: "inline-block", animation: "pulse-badge 2s ease-in-out infinite" }} />
          AI-Powered Application Compiler — v0.2
        </div>

        {/* Heading */}
        <h1
          style={{
            fontSize: "clamp(2.4rem, 6vw, 4rem)",
            fontWeight: 900,
            lineHeight: 1.1,
            letterSpacing: "-0.04em",
            marginBottom: 24,
            maxWidth: 820,
          }}
        >
          Natural Language to{" "}
          <span className="gradient-text">Structured App Specs</span>
          <br />in Seconds
        </h1>

        {/* Subheading */}
        <p
          style={{
            fontSize: "clamp(1rem, 2vw, 1.2rem)",
            color: "var(--color-text-secondary)",
            maxWidth: 620,
            lineHeight: 1.7,
            marginBottom: 40,
          }}
        >
          A deterministic 6-stage compiler pipeline that converts your requirements
          into validated UI, API, DB, and Auth schemas with automatic error repair
          and runtime verification.
        </p>

        {/* CTAs */}
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "center" }}>
          <Link
            href="/compiler"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              padding: "14px 32px",
              borderRadius: 12,
              background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
              color: "white",
              textDecoration: "none",
              fontWeight: 700,
              fontSize: "1rem",
              boxShadow: "0 4px 20px rgba(99,102,241,0.4)",
              transition: "all 0.25s",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            Start Building
          </Link>
          <Link
            href="/evaluation"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              padding: "14px 32px",
              borderRadius: 12,
              border: "1.5px solid var(--color-border)",
              color: "var(--color-text-primary)",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: "1rem",
              background: "transparent",
              transition: "all 0.25s",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            View Evaluation
          </Link>
        </div>

        {/* Stat row */}
        <div
          style={{
            display: "flex",
            gap: 40,
            marginTop: 60,
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {[
            { label: "Pipeline Stages", value: "6" },
            { label: "Schema Types", value: "4" },
            { label: "Auto-Repair Loops", value: "3" },
            { label: "Eval Test Cases", value: "10+" },
          ].map((s) => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div
                style={{ fontSize: "2rem", fontWeight: 800, letterSpacing: "-0.03em" }}
                className="gradient-text"
              >
                {s.value}
              </div>
              <div style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", fontWeight: 500, marginTop: 2 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pipeline Visual ── */}
      <section style={{ padding: "80px 24px", maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--color-accent)", marginBottom: 10 }}>
            How it works
          </div>
          <h2 style={{ fontSize: "clamp(1.6rem, 4vw, 2.4rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 12 }}>
            The Compiler Pipeline
          </h2>
          <p style={{ color: "var(--color-text-secondary)", maxWidth: 500, margin: "0 auto", lineHeight: 1.6 }}>
            Every prompt goes through a structured sequence of AI stages with deterministic validation at each step.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 20,
          }}
        >
          {pipeline.map((step, i) => (
            <div
              key={step.num}
              className="glass-card"
              style={{
                padding: "24px 28px",
                display: "flex",
                gap: 16,
                alignItems: "flex-start",
                position: "relative",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  fontSize: "2.5rem",
                  fontWeight: 900,
                  lineHeight: 1,
                  color: "var(--color-accent)",
                  opacity: 0.15,
                  fontVariantNumeric: "tabular-nums",
                  flexShrink: 0,
                  letterSpacing: "-0.04em",
                }}
              >
                {step.num}
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: "1rem", marginBottom: 6 }}>{step.label}</div>
                <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>{step.desc}</div>
              </div>
              {i < pipeline.length - 1 && (
                <div
                  style={{
                    position: "absolute",
                    right: -10,
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "var(--color-accent)",
                    opacity: 0.4,
                    fontSize: "1.2rem",
                  }}
                >
                  →
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── Feature Cards ── */}
      <section
        style={{
          padding: "80px 24px",
          background: "linear-gradient(180deg, transparent 0%, rgba(99,102,241,0.04) 50%, transparent 100%)",
        }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--color-accent)", marginBottom: 10 }}>
              Core Capabilities
            </div>
            <h2 style={{ fontSize: "clamp(1.6rem, 4vw, 2.4rem)", fontWeight: 800, letterSpacing: "-0.03em" }}>
              Everything you need
            </h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: 20,
            }}
          >
            {features.map((f) => (
              <div
                key={f.title}
                className="card"
                style={{ padding: "28px 28px", transition: "all 0.3s" }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: `${f.color}18`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: f.color,
                    marginBottom: 16,
                  }}
                >
                  {f.icon}
                </div>
                <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 8 }}>{f.title}</h3>
                <p style={{ fontSize: "0.88rem", color: "var(--color-text-secondary)", lineHeight: 1.65, margin: 0 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section style={{ padding: "80px 24px 100px" }}>
        <div
          style={{
            maxWidth: 700,
            margin: "0 auto",
            textAlign: "center",
            padding: "60px 40px",
            borderRadius: 24,
            background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 60%, #a855f7 100%)",
            color: "white",
            boxShadow: "0 20px 60px rgba(99,102,241,0.35)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            aria-hidden
            style={{
              position: "absolute",
              top: "-50%",
              left: "-20%",
              width: "140%",
              height: "200%",
              background: "radial-gradient(ellipse at center, rgba(255,255,255,0.08) 0%, transparent 60%)",
              pointerEvents: "none",
            }}
          />
          <h2 style={{ fontSize: "clamp(1.4rem, 4vw, 2rem)", fontWeight: 800, marginBottom: 14, letterSpacing: "-0.03em" }}>
            Ready to compile your first app?
          </h2>
          <p style={{ fontSize: "1rem", opacity: 0.85, marginBottom: 32, lineHeight: 1.6 }}>
            Describe any application in plain English and watch the compiler pipeline produce complete, validated schemas in seconds.
          </p>
          <Link
            href="/compiler"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              padding: "14px 36px",
              borderRadius: 12,
              background: "white",
              color: "#6366f1",
              textDecoration: "none",
              fontWeight: 700,
              fontSize: "1rem",
              boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            Open the Compiler
          </Link>
        </div>
      </section>

      <style>{`
        @keyframes pulse-badge {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(0.85); }
        }
      `}</style>
    </div>
  );
}
