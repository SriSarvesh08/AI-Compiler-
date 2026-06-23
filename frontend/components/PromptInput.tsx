"use client";

import React from "react";

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  buttonLabel?: string;
  loadingLabel?: string;
}

/**
 * PromptInput — Large textarea with character counter and Generate button.
 * The main user input component for describing applications.
 */
export default function PromptInput({
  value,
  onChange,
  onSubmit,
  isLoading,
  buttonLabel = "Compile Intent",
  loadingLabel = "Extracting Intent...",
}: PromptInputProps) {
  const maxLength = 2000;
  const minLength = 10;
  const charCount = value.length;
  const isValid = charCount >= minLength && charCount <= maxLength;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && isValid && !isLoading) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
      {/* Input Area */}
      <div style={{ position: "relative" }}>
        <textarea
          id="prompt-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Describe your application... e.g., "Build a CRM with login, contacts, dashboard, role-based access and premium plans"'
          maxLength={maxLength}
          className="input-area"
          style={{
            minHeight: 160,
            lineHeight: 1.6,
          }}
          disabled={isLoading}
        />

        {/* Character counter */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: 8,
            fontSize: "0.8rem",
          }}
        >
          <span className="text-muted">
            {charCount < minLength && charCount > 0
              ? `Minimum ${minLength} characters`
              : "Press Ctrl+Enter to generate"}
          </span>
          <span
            className="text-muted"
            style={{
              color:
                charCount > maxLength * 0.9
                  ? "var(--color-error)"
                  : undefined,
            }}
          >
            {charCount} / {maxLength}
          </span>
        </div>
      </div>

      {/* Generate Button */}
      <div style={{ marginTop: 20, display: "flex", gap: 12 }}>
        <button
          id="run-pipeline-button"
          onClick={onSubmit}
          disabled={!isValid || isLoading}
          className="btn-primary"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
            width: "100%",
            fontSize: "1.05rem",
            padding: "16px 32px",
          }}
        >
          {isLoading ? (
            <>
              <span
                style={{
                  display: "inline-block",
                  width: 20,
                  height: 20,
                  border: "2px solid rgba(255,255,255,0.3)",
                  borderTopColor: "white",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                }}
              />
              <style jsx>{`
                @keyframes spin {
                  to {
                    transform: rotate(360deg);
                  }
                }
              `}</style>
              {loadingLabel}
            </>
          ) : (
            <>
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              {buttonLabel}
            </>
          )}
        </button>
      </div>
    </div>
  );
}
