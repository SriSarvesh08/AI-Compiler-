"use client";

import { PipelineStage } from "@/lib/types";

interface PipelineVisualizerProps {
  stages: PipelineStage[];
}

/**
 * PipelineVisualizer — Vertical pipeline showing all compiler stages.
 * Displays stages connected by animated arrows with status indicators.
 */
export default function PipelineVisualizer({ stages }: PipelineVisualizerProps) {
  return (
    <div
      className="glass-card animate-fade-in"
      style={{
        padding: 24,
        animationDelay: "0.2s",
      }}
    >
      <h3
        style={{
          fontSize: "0.85rem",
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          marginBottom: 20,
        }}
        className="text-muted"
      >
        Compiler Pipeline
      </h3>

      <div style={{ display: "flex", flexDirection: "column" }}>
        {stages.map((stage, index) => (
          <div key={stage.id}>
            {/* Stage Row */}
            <div className={`pipeline-stage ${stage.status}`}>
              {/* Status Icon */}
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                  fontSize: "1rem",
                  background: getStatusBg(stage.status),
                  border: `1px solid ${getStatusBorder(stage.status)}`,
                  transition: "all 0.4s ease",
                }}
              >
                {getStatusIcon(stage.status)}
              </div>

              {/* Stage Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: "0.9rem",
                    fontWeight: 600,
                    transition: "color 0.3s ease",
                  }}
                >
                  {stage.label}
                </div>
                <div
                  style={{
                    fontSize: "0.75rem",
                    marginTop: 2,
                  }}
                  className="text-muted"
                >
                  {stage.description}
                </div>
              </div>

              {/* Status Badge */}
              {stage.status === "locked" && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    padding: "3px 8px",
                    borderRadius: 6,
                    whiteSpace: "nowrap",
                  }}
                  className="text-muted bg-surface"
                >
                  Pending
                </span>
              )}
              {stage.status === "completed" && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    padding: "3px 8px",
                    borderRadius: 6,
                    background: "var(--color-success-bg)",
                    color: "var(--color-success)",
                    whiteSpace: "nowrap",
                  }}
                >
                  Done
                </span>
              )}
              {stage.status === "active" && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    padding: "3px 8px",
                    borderRadius: 6,
                    background: "var(--color-accent-glow)",
                    color: "var(--color-accent)",
                    whiteSpace: "nowrap",
                  }}
                >
                  Running
                </span>
              )}
              {stage.status === "error" && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    padding: "3px 8px",
                    borderRadius: 6,
                    background: "var(--color-error-bg)",
                    color: "var(--color-error)",
                    whiteSpace: "nowrap",
                  }}
                >
                  Failed
                </span>
              )}
            </div>

            {/* Connector Line (between stages) */}
            {index < stages.length - 1 && (
              <div
                className={`pipeline-connector ${
                  stage.status === "completed" ? "active" : ""
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function getStatusIcon(status: string): string {
  switch (status) {
    case "completed":
      return "✓";
    case "active":
      return "⟳";
    case "error":
      return "✕";
    case "locked":
      return "🔒";
    default:
      return "○";
  }
}

function getStatusBg(status: string): string {
  switch (status) {
    case "completed":
      return "var(--color-success-bg)";
    case "active":
      return "var(--color-accent-glow)";
    case "error":
      return "var(--color-error-bg)";
    default:
      return "transparent";
  }
}

function getStatusBorder(status: string): string {
  switch (status) {
    case "completed":
      return "var(--color-success)";
    case "active":
      return "var(--color-accent)";
    case "error":
      return "var(--color-error)";
    default:
      return "var(--color-border)";
  }
}
