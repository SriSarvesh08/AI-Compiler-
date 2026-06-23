import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Results — AI Application Compiler",
  description: "View and export generated application specifications.",
};

/**
 * Results page — placeholder for viewing/exporting generated specifications.
 * Will be implemented in future iterations.
 */
export default function ResultsPage() {
  return (
    <div
      style={{
        maxWidth: 800,
        margin: "0 auto",
        padding: "60px 24px",
        textAlign: "center",
      }}
    >
      <div
        style={{
          width: 64,
          height: 64,
          borderRadius: 16,
          background: "linear-gradient(135deg, #10b981 0%, #06b6d4 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 24px",
          fontSize: "1.8rem",
        }}
      >
        📋
      </div>

      <h1
        style={{
          fontSize: "2rem",
          fontWeight: 700,
          marginBottom: 12,
        }}
      >
        Compilation <span className="gradient-text">Results</span>
      </h1>

      <p
        style={{
          fontSize: "1.05rem",
          lineHeight: 1.6,
          maxWidth: 500,
          margin: "0 auto 32px",
        }}
        className="text-secondary"
      >
        View, compare, and export your generated application specifications.
        This page will display results from all pipeline stages.
      </p>

      <div
        className="card"
        style={{
          padding: 24,
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: "50%",
            background: "var(--color-warning)",
          }}
        />
        <span style={{ fontSize: "0.9rem", fontWeight: 500 }}>
          Under Development — Check back after Day 2
        </span>
      </div>
    </div>
  );
}
