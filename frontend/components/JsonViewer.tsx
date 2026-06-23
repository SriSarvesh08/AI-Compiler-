"use client";

import { useState } from "react";

interface JsonViewerProps {
  data: object;
  title?: string;
  extractionTime?: number;
}

/**
 * JsonViewer — Syntax-highlighted JSON display with copy-to-clipboard.
 * Renders JSON with custom token colors for a premium code viewer feel.
 */
export default function JsonViewer({
  data,
  title = "Output",
  extractionTime,
}: JsonViewerProps) {
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(data, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = jsonString;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className="card animate-slide-down"
      style={{
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "14px 20px",
          borderBottom: "1px solid var(--color-border)",
        }}
        className="dark:border-[var(--color-dark-border)]"
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "var(--color-success)",
            }}
          />
          <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{title}</span>
          {extractionTime !== undefined && (
            <span
              style={{
                fontSize: "0.75rem",
                padding: "2px 8px",
                borderRadius: 6,
              }}
              className="text-muted bg-surface"
            >
              {extractionTime.toFixed(0)}ms
            </span>
          )}
        </div>

        <button
          id="copy-json-button"
          onClick={handleCopy}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 12px",
            borderRadius: 8,
            border: "1px solid var(--color-border)",
            background: "transparent",
            fontSize: "0.78rem",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          className="text-secondary hover:bg-[var(--color-bg-secondary)] dark:border-[var(--color-dark-border)] dark:hover:bg-[var(--color-dark-bg-secondary)]"
        >
          {copied ? (
            <>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--color-success)"
                strokeWidth="2"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Copied!
            </>
          ) : (
            <>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
              </svg>
              Copy
            </>
          )}
        </button>
      </div>

      {/* JSON Content */}
      <div className="json-viewer">
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
          {highlightJson(jsonString)}
        </pre>
      </div>
    </div>
  );
}

/**
 * Simple JSON syntax highlighter.
 * Wraps tokens in spans with appropriate CSS classes.
 */
function highlightJson(json: string): React.ReactNode[] {
  const lines = json.split("\n");
  return lines.map((line, i) => {
    const parts: React.ReactNode[] = [];
    let remaining = line;
    let keyCounter = 0;

    while (remaining.length > 0) {
      // Match JSON key
      const keyMatch = remaining.match(/^(\s*)"([^"]+)"(\s*:\s*)/);
      if (keyMatch) {
        parts.push(keyMatch[1]); // whitespace
        parts.push(
          <span key={`k-${i}-${keyCounter++}`} className="json-bracket">
            &quot;
          </span>
        );
        parts.push(
          <span key={`kv-${i}-${keyCounter++}`} className="json-key">
            {keyMatch[2]}
          </span>
        );
        parts.push(
          <span key={`kb-${i}-${keyCounter++}`} className="json-bracket">
            &quot;
          </span>
        );
        parts.push(keyMatch[3]); // colon
        remaining = remaining.slice(keyMatch[0].length);
        continue;
      }

      // Match JSON string value
      const strMatch = remaining.match(/^(\s*)"([^"]*)"(.*)/);
      if (strMatch) {
        parts.push(strMatch[1]); // whitespace
        parts.push(
          <span key={`sb-${i}-${keyCounter++}`} className="json-bracket">
            &quot;
          </span>
        );
        parts.push(
          <span key={`sv-${i}-${keyCounter++}`} className="json-string">
            {strMatch[2]}
          </span>
        );
        parts.push(
          <span key={`se-${i}-${keyCounter++}`} className="json-bracket">
            &quot;
          </span>
        );
        remaining = strMatch[3];
        continue;
      }

      // Match numbers
      const numMatch = remaining.match(/^(\s*)(\d+\.?\d*)(.*)/);
      if (numMatch) {
        parts.push(numMatch[1]);
        parts.push(
          <span key={`n-${i}-${keyCounter++}`} className="json-number">
            {numMatch[2]}
          </span>
        );
        remaining = numMatch[3];
        continue;
      }

      // Match booleans
      const boolMatch = remaining.match(/^(\s*)(true|false)(.*)/);
      if (boolMatch) {
        parts.push(boolMatch[1]);
        parts.push(
          <span key={`b-${i}-${keyCounter++}`} className="json-boolean">
            {boolMatch[2]}
          </span>
        );
        remaining = boolMatch[3];
        continue;
      }

      // Match null
      const nullMatch = remaining.match(/^(\s*)(null)(.*)/);
      if (nullMatch) {
        parts.push(nullMatch[1]);
        parts.push(
          <span key={`nl-${i}-${keyCounter++}`} className="json-null">
            {nullMatch[2]}
          </span>
        );
        remaining = nullMatch[3];
        continue;
      }

      // Match brackets
      const bracketMatch = remaining.match(/^(\s*)([{}\[\],])(.*)/);
      if (bracketMatch) {
        parts.push(bracketMatch[1]);
        parts.push(
          <span key={`br-${i}-${keyCounter++}`} className="json-bracket">
            {bracketMatch[2]}
          </span>
        );
        remaining = bracketMatch[3];
        continue;
      }

      // Default — push remaining and break
      parts.push(remaining);
      break;
    }

    return (
      <React.Fragment key={`line-${i}`}>
        {parts}
        {i < lines.length - 1 ? "\n" : ""}
      </React.Fragment>
    );
  });
}
