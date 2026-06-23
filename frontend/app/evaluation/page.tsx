"use client";

import React, { useState, useEffect } from "react";
import { 
  getEvaluationDataset, 
  runEvaluation, 
  getLatestEvaluation,
  EvaluationResponse,
  EvaluationSummary,
  EvaluationResult
} from "@/lib/api";

export default function EvaluationPage() {
  const [dataset, setDataset] = useState<any[]>([]);
  const [results, setResults] = useState<EvaluationResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDataset();
    loadLatestResults();
  }, []);

  const loadDataset = async () => {
    try {
      const data = await getEvaluationDataset();
      if (data.success && data.dataset) {
        setDataset(data.dataset);
      }
    } catch (err) {
      console.error("Failed to load dataset", err);
    }
  };

  const loadLatestResults = async () => {
    try {
      const data = await getLatestEvaluation();
      if (data) {
        setResults(data);
      }
    } catch (err) {
      console.error("Failed to load latest evaluation", err);
    }
  };

  const handleRunEvaluation = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const data = await runEvaluation();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Failed to run evaluation");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="container mx-auto" style={{ maxWidth: 1200, padding: "40px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 30 }}>
        <div>
          <h1 style={{ fontSize: "2rem", fontWeight: 700, margin: "0 0 8px 0" }}>Evaluation Framework</h1>
          <p style={{ color: "var(--color-text-secondary)", margin: 0 }}>
            Automated reliability and accuracy testing across {dataset.length} prompt configurations.
          </p>
        </div>
        
        <button 
          onClick={handleRunEvaluation}
          disabled={isRunning}
          style={{
            padding: "12px 24px",
            backgroundColor: isRunning ? "var(--color-border)" : "var(--color-accent)",
            color: "white",
            border: "none",
            borderRadius: 8,
            fontWeight: 600,
            cursor: isRunning ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: 10,
            transition: "all 0.2s"
          }}
        >
          {isRunning ? (
            <>
              <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
              Running Extensive Test Suite...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Run Evaluation Suite
            </>
          )}
        </button>
      </div>

      {error && (
        <div style={{ padding: 16, backgroundColor: "rgba(239, 68, 68, 0.1)", border: "1px solid var(--color-error)", borderRadius: 8, color: "var(--color-error)", marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Metrics Summary Area */}
      {results && results.summary && (
        <div style={{ display: "flex", flexDirection: "column", gap: 24, marginBottom: 40 }} className="animate-fade-in">
          <h2 style={{ fontSize: "1.2rem", fontWeight: 600, margin: 0 }}>Execution Metrics</h2>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16 }}>
            <MetricCard label="Total Tests" value={results.summary.total_tests} />
            <MetricCard label="Success Rate" value={`${results.summary.success_rate}%`} color={results.summary.success_rate > 80 ? "var(--color-success)" : "var(--color-warning)"} />
            <MetricCard label="Runtime Ready Rate" value={`${results.summary.runtime_ready_rate}%`} />
            <MetricCard label="Avg Latency" value={`${results.summary.average_latency_ms.toFixed(0)}ms`} />
            <MetricCard label="Avg Repairs/Test" value={results.summary.average_repair_attempts} />
            <MetricCard label="Edge Case Success" value={`${results.summary.edge_case_success_rate}%`} color={results.summary.edge_case_success_rate > 50 ? "var(--color-success)" : "var(--color-error)"} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            {/* Success Bar */}
            <div className="glass-card" style={{ padding: 24 }}>
               <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: "0 0 16px 0" }}>Category Performance</h3>
               <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 6 }}>
                      <span>Normal Prompts</span>
                      <span style={{ fontWeight: 600 }}>{results.summary.normal_prompt_success_rate}%</span>
                    </div>
                    <div style={{ height: 10, backgroundColor: "var(--color-bg-secondary)", borderRadius: 5, overflow: "hidden" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                      <div style={{ height: "100%", width: `${results.summary.normal_prompt_success_rate}%`, backgroundColor: "var(--color-success)" }} />
                    </div>
                  </div>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: 6 }}>
                      <span>Edge Case Prompts</span>
                      <span style={{ fontWeight: 600 }}>{results.summary.edge_case_success_rate}%</span>
                    </div>
                    <div style={{ height: 10, backgroundColor: "var(--color-bg-secondary)", borderRadius: 5, overflow: "hidden" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                      <div style={{ height: "100%", width: `${results.summary.edge_case_success_rate}%`, backgroundColor: "var(--color-warning)" }} />
                    </div>
                  </div>
               </div>
            </div>

            {/* Failure Distribution */}
            <div className="glass-card" style={{ padding: 24 }}>
               <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: "0 0 16px 0" }}>Failure Distribution</h3>
               {results.summary.most_common_failure_types.length > 0 ? (
                 <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                   {results.summary.most_common_failure_types.map((fail, i) => (
                     <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", backgroundColor: "var(--color-bg-secondary)", borderRadius: 6 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                       <span style={{ fontSize: "0.8rem", fontFamily: "monospace", color: "var(--color-error)" }}>{fail.type}</span>
                       <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{fail.count}</span>
                     </div>
                   ))}
                 </div>
               ) : (
                 <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 80, color: "var(--color-text-secondary)", fontSize: "0.9rem" }}>
                   No failures detected!
                 </div>
               )}
            </div>
          </div>
        </div>
      )}

      {/* Dataset / Results Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: 20, borderBottom: "1px solid var(--color-border)" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 600, margin: 0 }}>Detailed Results</h2>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", textAlign: "left" }}>
            <thead style={{ backgroundColor: "var(--color-bg-secondary)" }} className="dark:bg-[var(--color-dark-bg-secondary)] text-muted">
              <tr>
                <th style={{ padding: "12px 20px", fontWeight: 600 }}>ID</th>
                <th style={{ padding: "12px 20px", fontWeight: 600 }}>Category</th>
                <th style={{ padding: "12px 20px", fontWeight: 600, width: "30%" }}>Prompt Preview</th>
                {results && (
                  <>
                    <th style={{ padding: "12px 20px", fontWeight: 600 }}>Success</th>
                    <th style={{ padding: "12px 20px", fontWeight: 600 }}>Runtime</th>
                    <th style={{ padding: "12px 20px", fontWeight: 600 }}>Repairs</th>
                    <th style={{ padding: "12px 20px", fontWeight: 600 }}>Latency</th>
                    <th style={{ padding: "12px 20px", fontWeight: 600 }}>Failure Type</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {(results?.results || dataset).map((row: any, i: number) => {
                const isEdge = row.category === "edge";
                return (
                  <tr key={row.id} style={{ borderBottom: "1px solid var(--color-border)", backgroundColor: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.01)" }}>
                    <td style={{ padding: "12px 20px", fontFamily: "monospace" }}>{row.id}</td>
                    <td style={{ padding: "12px 20px" }}>
                      <span style={{ padding: "2px 8px", borderRadius: 12, fontSize: "0.7rem", fontWeight: 600, backgroundColor: isEdge ? "rgba(245, 158, 11, 0.1)" : "rgba(59, 130, 246, 0.1)", color: isEdge ? "#f59e0b" : "#3b82f6" }}>
                        {row.category.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "12px 20px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: 300 }} title={row.prompt}>
                      {row.prompt}
                    </td>
                    {results && (
                      <>
                        <td style={{ padding: "12px 20px" }}>
                          {row.success ? (
                            <span style={{ color: "var(--color-success)" }}>✅ Pass</span>
                          ) : (
                            <span style={{ color: "var(--color-error)" }}>❌ Fail</span>
                          )}
                        </td>
                        <td style={{ padding: "12px 20px" }}>
                          {row.runtime_ready ? "Yes" : "No"}
                        </td>
                        <td style={{ padding: "12px 20px", textAlign: "center" }}>
                          {row.repair_attempts > 0 ? (
                            <span style={{ color: "var(--color-warning)", fontWeight: 600 }}>{row.repair_attempts}</span>
                          ) : (
                            <span style={{ color: "var(--color-text-secondary)" }}>0</span>
                          )}
                        </td>
                        <td style={{ padding: "12px 20px" }}>{row.latency_ms.toFixed(0)}ms</td>
                        <td style={{ padding: "12px 20px", fontFamily: "monospace", color: "var(--color-error)", fontSize: "0.75rem" }}>
                          {row.failure_type || "-"}
                        </td>
                      </>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string, value: string | number, color?: string }) {
  return (
    <div className="glass-card" style={{ padding: 20 }}>
      <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: 8, fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: "1.8rem", fontWeight: 700, color: color || "var(--color-text)" }}>{value}</div>
    </div>
  );
}
