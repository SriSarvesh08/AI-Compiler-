"use client";

/**
 * LoadingState — Animated loading component with pulsing dots.
 * Shows current pipeline stage being processed.
 */

interface LoadingStateProps {
  stage?: string;
  message?: string;
}

export default function LoadingState({
  stage = "Intent Extraction",
  message = "Analyzing your requirements...",
}: LoadingStateProps) {
  return (
    <div
      className="card animate-fade-in"
      style={{
        padding: 32,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
      }}
    >
      {/* Pulsing Dots */}
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          height: 24,
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "var(--color-accent)",
              animation: `pulse-dot 1.4s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>

      {/* Stage label */}
      <div style={{ textAlign: "center" }}>
        <div
          style={{
            fontSize: "0.95rem",
            fontWeight: 600,
            marginBottom: 4,
          }}
        >
          {stage}
        </div>
        <div style={{ fontSize: "0.85rem" }} className="text-muted">
          {message}
        </div>
      </div>

      {/* Shimmer bar */}
      <div
        style={{
          width: "100%",
          maxWidth: 280,
          height: 4,
          borderRadius: 2,
          overflow: "hidden",
        }}
        className="bg-surface"
      >
        <div
          style={{
            width: "40%",
            height: "100%",
            borderRadius: 2,
            background:
              "linear-gradient(90deg, transparent 0%, var(--color-accent) 50%, transparent 100%)",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.5s linear infinite",
          }}
        />
      </div>
    </div>
  );
}
