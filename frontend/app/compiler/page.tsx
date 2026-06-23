"use client";

import { useState, useCallback } from "react";
import PipelineVisualizer from "@/components/PipelineVisualizer";
import JsonViewer from "@/components/JsonViewer";
import LoadingState from "@/components/LoadingState";
import { runFullPipeline, modifyPipeline } from "@/lib/api";
import {
  IntentOutput,
  ApplicationArchitecture,
  SchemaGenerationOutput,
  ValidationOutput,
  RepairOutput,
  RuntimeOutput,
  PipelineStage,
  StageStatus,
} from "@/lib/types";

const EXAMPLE_PROMPTS = [
  {
    label: "CRM with Roles",
    value:
      "Build a CRM with login, contacts list, dashboard, role-based access for admin and sales agents, and a premium plan with payments. Admins can see analytics.",
  },
  {
    label: "Hospital Management",
    value:
      "Create a hospital management system with patients, doctors, nurses, admins. Patients can book appointments. Doctors view schedules. Admins manage staff and billing.",
  },
  {
    label: "E-Commerce Platform",
    value:
      "Build an e-commerce platform with product listings, shopping cart, checkout, order tracking, seller dashboard, admin panel with analytics and inventory management.",
  },
  {
    label: "LMS Platform",
    value:
      "Build a learning management system with students, instructors, and admins. Instructors create courses, students enroll and track progress. Admins manage users.",
  },
];

function getDefaultStages(
  overrides?: Partial<Record<string, StageStatus>>
): PipelineStage[] {
  const stages: PipelineStage[] = [
    { id: "prompt", label: "User Prompt", status: "idle", description: "Natural language input" },
    { id: "intent", label: "Intent Extraction", status: "idle", description: "Parse domain, features & roles" },
    { id: "design", label: "System Design", status: "idle", description: "Architecture & data model" },
    { id: "schema", label: "Schema Generation", status: "idle", description: "Database & API schemas" },
    { id: "validation", label: "Validation", status: "idle", description: "Consistency & correctness checks" },
    { id: "repair", label: "Repair Engine", status: "idle", description: "Auto-fix validation errors" },
    { id: "simulation", label: "Runtime Simulation", status: "idle", description: "Verify application behavior" },
  ];
  if (overrides) {
    return stages.map((s) => ({ ...s, status: overrides[s.id] ?? s.status }));
  }
  return stages;
}

export default function CompilerPage() {
  const [prompt, setPrompt] = useState("");
  const [projectName, setProjectName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string>("Intent Extraction");
  const [loadingMessage, setLoadingMessage] = useState<string>("Analyzing your requirements...");
  const [intentResult, setIntentResult] = useState<IntentOutput | null>(null);
  const [architectureResult, setArchitectureResult] = useState<ApplicationArchitecture | null>(null);
  const [schemasResult, setSchemasResult] = useState<SchemaGenerationOutput | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationOutput | null>(null);
  const [repairResult, setRepairResult] = useState<RepairOutput | null>(null);
  const [finalValidationResult, setFinalValidationResult] = useState<ValidationOutput | null>(null);
  const [runtimeResult, setRuntimeResult] = useState<RuntimeOutput | null>(null);
  const [activeSchemaTab, setActiveSchemaTab] = useState<string>("intent");
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [activePreviewTab, setActivePreviewTab] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [totalTime, setTotalTime] = useState<number>(0);
  const [stages, setStages] = useState<PipelineStage[]>(getDefaultStages());
  const [modifyPrompt, setModifyPrompt] = useState("");
  const [isModifying, setIsModifying] = useState(false);
  const [patchSummary, setPatchSummary] = useState<string[]>([]);
  const [changeType, setChangeType] = useState<string | null>(null);
  const [clarificationNeeded, setClarificationNeeded] = useState<boolean>(false);
  const [clarificationQuestions, setClarificationQuestions] = useState<string[]>([]);
  const [showExamples, setShowExamples] = useState(false);

  const hasResults = !!(intentResult || architectureResult || schemasResult || validationResult || repairResult);

  const handleClear = () => {
    setPrompt("");
    setProjectName("");
    setIntentResult(null);
    setArchitectureResult(null);
    setSchemasResult(null);
    setValidationResult(null);
    setRepairResult(null);
    setFinalValidationResult(null);
    setRuntimeResult(null);
    setError(null);
    setTotalTime(0);
    setPatchSummary([]);
    setChangeType(null);
    setClarificationNeeded(false);
    setClarificationQuestions([]);
    setStages(getDefaultStages());
    setActiveTab("overview");
  };

  const handleRunPipeline = useCallback(async () => {
    if (!prompt.trim() || prompt.length < 10) return;
    setIsLoading(true);
    setIntentResult(null); setArchitectureResult(null); setSchemasResult(null);
    setValidationResult(null); setRepairResult(null); setFinalValidationResult(null);
    setRuntimeResult(null); setError(null); setTotalTime(0);
    setPatchSummary([]); setChangeType(null);
    setClarificationNeeded(false); setClarificationQuestions([]);

    setLoadingStage("Pipeline Running");
    setLoadingMessage("Extracting Intent → Designing System → Generating Schemas → Validating → Repairing → Simulating Runtime");
    setStages(getDefaultStages({ prompt: "completed", intent: "active", design: "active", schema: "active", validation: "active", repair: "active", simulation: "active" }));

    try {
      const response = await runFullPipeline(prompt);
      if (response.success && response.stages) {
        setIntentResult(response.stages.intent || null);
        setArchitectureResult(response.stages.architecture || null);
        setSchemasResult(response.stages.schemas || null);
        setValidationResult(response.stages.validation || null);
        setRepairResult(response.stages.repair || null);
        setFinalValidationResult(response.stages.final_validation || null);
        setRuntimeResult(response.stages.runtime || null);
        setTotalTime(response.total_time_ms);
        setError(null);
        if (response.stages.runtime?.runtime_ready) setActiveTab("runtime");
        else if (response.stages.repair?.repaired) setActiveTab("repair");
        else if (response.stages.validation && !response.stages.validation.is_valid) setActiveTab("validation");
        else setActiveTab("overview");

        setStages(getDefaultStages({
          prompt: "completed",
          intent: response.stages.intent ? "completed" : "error",
          design: response.stages.architecture ? "completed" : "error",
          schema: response.stages.schemas ? "completed" : "error",
          validation: response.stages.validation ? "completed" : "error",
          repair: response.stages.repair ? "completed" : "error",
          simulation: response.stages.runtime ? "completed" : "error",
        }));
      } else {
        setError(response.error || "Unknown error occurred");
        const intentDone = !!response.stages?.intent;
        const designDone = !!response.stages?.architecture;
        const schemaDone = !!response.stages?.schemas;
        const validationDone = !!response.stages?.validation;
        const repairDone = !!response.stages?.repair;
        const runtimeDone = !!response.stages?.runtime;
        if (intentDone) setIntentResult(response.stages!.intent || null);
        if (designDone) setArchitectureResult(response.stages!.architecture || null);
        if (schemaDone) setSchemasResult(response.stages!.schemas || null);
        if (validationDone) setValidationResult(response.stages!.validation || null);
        if (repairDone) { setRepairResult(response.stages!.repair || null); setFinalValidationResult(response.stages!.final_validation || null); }
        if (runtimeDone) setRuntimeResult(response.stages!.runtime || null);
        setStages(getDefaultStages({
          prompt: "completed",
          intent: intentDone ? "completed" : "error",
          design: intentDone ? (designDone ? "completed" : "error") : "idle",
          schema: designDone ? (schemaDone ? "completed" : "error") : "idle",
          validation: schemaDone ? (validationDone ? "completed" : "error") : "idle",
          repair: validationDone ? (repairDone ? "completed" : "error") : "idle",
          simulation: repairDone ? (runtimeDone ? "completed" : "error") : "idle",
        }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
      setStages(getDefaultStages({ prompt: "completed", intent: "error" }));
    } finally {
      setIsLoading(false);
    }
  }, [prompt]);

  const handleModifyPipeline = useCallback(async () => {
    if (!modifyPrompt.trim() || modifyPrompt.length < 3) return;
    const existingStages: any = {};
    if (intentResult) existingStages.intent = intentResult;
    if (architectureResult) existingStages.architecture = architectureResult;
    if (schemasResult) existingStages.schemas = schemasResult;
    if (validationResult) existingStages.validation = validationResult;
    if (repairResult) existingStages.repair = repairResult;
    if (finalValidationResult) existingStages.final_validation = finalValidationResult;
    if (runtimeResult) existingStages.runtime = runtimeResult;
    setIsModifying(true); setError(null); setClarificationNeeded(false); setClarificationQuestions([]);
    try {
      const response = await modifyPipeline(existingStages, modifyPrompt);
      if (response.success && response.updated_stages) {
        if (response.clarification_needed) { setClarificationNeeded(true); setClarificationQuestions(response.clarification_questions || []); setPatchSummary([]); return; }
        setChangeType(response.change_type); setPatchSummary(response.patch_summary || []);
        if (response.updated_stages.intent) setIntentResult(response.updated_stages.intent);
        if (response.updated_stages.architecture) setArchitectureResult(response.updated_stages.architecture);
        if (response.updated_stages.schemas) setSchemasResult(response.updated_stages.schemas);
        if (response.updated_stages.validation) setValidationResult(response.updated_stages.validation);
        if (response.updated_stages.repair) setRepairResult(response.updated_stages.repair);
        if (response.updated_stages.final_validation) setFinalValidationResult(response.updated_stages.final_validation);
        if (response.updated_stages.runtime) setRuntimeResult(response.updated_stages.runtime);
        setModifyPrompt("");
      } else {
        setError(response.error || "Failed to modify configuration.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsModifying(false);
    }
  }, [modifyPrompt, intentResult, architectureResult, schemasResult, validationResult, repairResult, finalValidationResult, runtimeResult]);

  const outputTabs = [
    { id: "overview", label: "Overview" },
    { id: "json_output", label: "JSON Output" },
    { id: "validation", label: "Validation" },
    { id: "repair", label: "Repair" },
    { id: "runtime", label: "Runtime Preview" },
  ];

  return (
    <div style={{ maxWidth: 1280, margin: "0 auto", padding: "40px 24px 80px" }}>
      {/* Page Header */}
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: "clamp(1.6rem, 4vw, 2.2rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 8 }}>
          AI Application{" "}
          <span className="gradient-text">Compiler</span>
        </h1>
        <p style={{ color: "var(--color-text-secondary)", fontSize: "0.95rem" }}>
          Describe any application in plain English. The pipeline produces structured, validated schemas automatically.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 28, alignItems: "start" }} className="main-grid">
        {/* ── Left Column ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

          {/* Input Card */}
          <div className="glass-card" style={{ padding: 28 }}>
            {/* Project name */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                Project Name <span style={{ color: "var(--color-text-muted)", fontWeight: 400 }}>(optional)</span>
              </label>
              <input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g. My CRM App"
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: 9,
                  border: "1.5px solid var(--color-border)",
                  background: "var(--color-bg-input)",
                  fontSize: "0.92rem",
                  color: "var(--color-text-primary)",
                  outline: "none",
                  boxSizing: "border-box",
                  transition: "all 0.2s",
                }}
                className="dark:border-[var(--color-dark-border)] dark:bg-[var(--color-dark-bg-input)]"
              />
            </div>

            {/* Prompt */}
            <div style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <label style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  Application Description
                </label>
                <div style={{ position: "relative" }}>
                  <button
                    onClick={() => setShowExamples(!showExamples)}
                    style={{
                      display: "flex", alignItems: "center", gap: 5,
                      padding: "4px 10px", borderRadius: 7,
                      border: "1px solid var(--color-border)",
                      background: "transparent", cursor: "pointer",
                      fontSize: "0.78rem", fontWeight: 600,
                      color: "var(--color-text-secondary)",
                    }}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                      <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                    Examples
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </button>
                  {showExamples && (
                    <div style={{
                      position: "absolute", right: 0, top: "calc(100% + 6px)",
                      background: "var(--color-bg-card)", border: "1px solid var(--color-border)",
                      borderRadius: 12, padding: 8, minWidth: 280,
                      boxShadow: "0 8px 30px rgba(0,0,0,0.12)", zIndex: 50,
                    }} className="dark:bg-[var(--color-dark-bg-card)] dark:border-[var(--color-dark-border)]">
                      {EXAMPLE_PROMPTS.map((ex) => (
                        <button
                          key={ex.label}
                          onClick={() => { setPrompt(ex.value); setShowExamples(false); }}
                          style={{
                            display: "block", width: "100%", textAlign: "left",
                            padding: "10px 12px", borderRadius: 8,
                            border: "none", background: "transparent",
                            cursor: "pointer", fontSize: "0.85rem",
                          }}
                        >
                          <div style={{ fontWeight: 600, marginBottom: 2, color: "var(--color-text-primary)" }}>{ex.label}</div>
                          <div style={{ color: "var(--color-text-muted)", fontSize: "0.78rem", lineHeight: 1.4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{ex.value}</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <textarea
                id="prompt-input"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && prompt.length >= 10 && !isLoading) { e.preventDefault(); handleRunPipeline(); } }}
                placeholder='e.g. "Build a CRM with login, contacts, dashboard, role-based access, and premium plans. Admins can see analytics."'
                maxLength={2000}
                className="input-area"
                style={{ minHeight: 150, lineHeight: 1.65, boxSizing: "border-box" }}
                disabled={isLoading}
              />
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: "0.78rem", color: "var(--color-text-muted)" }}>
                <span>{prompt.length < 10 && prompt.length > 0 ? `Minimum 10 characters` : "Ctrl+Enter to run"}</span>
                <span style={{ color: prompt.length > 1800 ? "var(--color-error)" : undefined }}>{prompt.length} / 2000</span>
              </div>
            </div>

            {/* Action buttons */}
            <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
              <button
                id="run-pipeline-button"
                onClick={handleRunPipeline}
                disabled={prompt.length < 10 || isLoading}
                className="btn-primary"
                style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "13px 24px", fontSize: "0.95rem" }}
              >
                {isLoading ? (
                  <>
                    <span style={{ width: 18, height: 18, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.8s linear infinite", display: "inline-block" }} />
                    Running Pipeline...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                    </svg>
                    Run Full Pipeline
                  </>
                )}
              </button>
              {hasResults && !isLoading && (
                <button
                  onClick={handleClear}
                  style={{
                    padding: "13px 18px", borderRadius: 12,
                    border: "1.5px solid var(--color-border)",
                    background: "transparent", cursor: "pointer",
                    fontSize: "0.9rem", fontWeight: 600,
                    color: "var(--color-text-secondary)",
                    display: "flex", alignItems: "center", gap: 6,
                    transition: "all 0.2s",
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.96"/>
                  </svg>
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Loading State */}
          {isLoading && <LoadingState stage={loadingStage} message={loadingMessage} />}

          {/* Error */}
          {error && !isLoading && (
            <div className="glass-card animate-slide-down" style={{ padding: 18, borderLeft: "4px solid var(--color-error)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span style={{ fontWeight: 700, color: "var(--color-error)", fontSize: "0.9rem" }}>Pipeline Error</span>
              </div>
              <p style={{ fontSize: "0.85rem", margin: 0, lineHeight: 1.5, color: "var(--color-text-secondary)" }}>{error}</p>
            </div>
          )}

          {/* Results Section */}
          {!isLoading && hasResults && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }} className="animate-fade-in">

              {/* Executive Summary */}
              {activeTab === "overview" && (
                <div className="glass-card animate-slide-up" style={{ padding: 24 }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    {projectName ? `"${projectName}" — ` : ""}Pipeline Summary
                  </h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 14 }}>
                    <div style={{ padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 12 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                      <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", marginBottom: 4, fontWeight: 500 }}>Total Latency</div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--color-accent)" }}>{totalTime.toFixed(0)}ms</div>
                    </div>
                    {architectureResult && (
                      <div style={{ padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 12 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                        <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", marginBottom: 4, fontWeight: 500 }}>Pages</div>
                        <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{architectureResult.pages.length}</div>
                      </div>
                    )}
                    {schemasResult?.api_schema && (
                      <div style={{ padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 12 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                        <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", marginBottom: 4, fontWeight: 500 }}>API Endpoints</div>
                        <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{schemasResult.api_schema.endpoints.length}</div>
                      </div>
                    )}
                    {schemasResult?.db_schema && (
                      <div style={{ padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 12 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                        <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", marginBottom: 4, fontWeight: 500 }}>DB Tables</div>
                        <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{schemasResult.db_schema.tables.length}</div>
                      </div>
                    )}
                    {validationResult && (
                      <div style={{ padding: 16, backgroundColor: validationResult.is_valid ? "var(--color-success-bg)" : "var(--color-error-bg)", borderRadius: 12 }}>
                        <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", marginBottom: 4, fontWeight: 500 }}>Validation</div>
                        <div style={{ fontSize: "1.1rem", fontWeight: 800, color: validationResult.is_valid ? "var(--color-success)" : "var(--color-error)" }}>
                          {validationResult.is_valid ? "✓ Valid" : `${validationResult.errors.length} Errors`}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab Navigation */}
              <div style={{ display: "flex", gap: 6, borderBottom: "1.5px solid var(--color-border)", paddingBottom: 0, overflowX: "auto" }} className="hide-scrollbar">
                {outputTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      padding: "10px 18px",
                      borderRadius: "10px 10px 0 0",
                      border: "none",
                      borderBottom: activeTab === tab.id ? "2px solid var(--color-accent)" : "2px solid transparent",
                      background: activeTab === tab.id ? "var(--color-accent-glow)" : "transparent",
                      color: activeTab === tab.id ? "var(--color-accent)" : "var(--color-text-secondary)",
                      fontWeight: activeTab === tab.id ? 700 : 500,
                      fontSize: "0.88rem",
                      cursor: "pointer",
                      transition: "all 0.2s",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* ── Validation Tab ── */}
              {activeTab === "validation" && validationResult && (
                <div className="glass-card animate-slide-up" style={{ padding: 24 }}>
                  <div style={{ marginBottom: 20 }}>
                    {validationResult.is_valid ? (
                      <div style={{ padding: 16, backgroundColor: "var(--color-success-bg)", border: "1px solid var(--color-success)", borderRadius: 10, color: "var(--color-success)", fontWeight: 600, display: "flex", alignItems: "center", gap: 10 }}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="9 11 12 14 22 4"/></svg>
                        Configuration passed validation — no repairs needed.
                      </div>
                    ) : (
                      <div style={{ padding: 16, backgroundColor: "var(--color-error-bg)", border: "1px solid var(--color-error)", borderRadius: 10, color: "var(--color-error)", fontWeight: 600, display: "flex", alignItems: "center", gap: 10 }}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                        {validationResult.errors.length} errors · {validationResult.warnings.length} warnings
                      </div>
                    )}
                  </div>
                  <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
                    <div style={{ flex: 1, padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 10 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                      <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>Errors</div>
                      <div style={{ fontSize: "1.5rem", fontWeight: 800, color: validationResult.errors.length > 0 ? "var(--color-error)" : "var(--color-text-primary)" }}>{validationResult.errors.length}</div>
                    </div>
                    <div style={{ flex: 1, padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 10 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                      <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>Warnings</div>
                      <div style={{ fontSize: "1.5rem", fontWeight: 800, color: validationResult.warnings.length > 0 ? "#eab308" : "var(--color-text-primary)" }}>{validationResult.warnings.length}</div>
                    </div>
                  </div>
                  {(validationResult.errors.length > 0 || validationResult.warnings.length > 0) && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      {validationResult.errors.map((err, idx) => (
                        <div key={`err-${idx}`} style={{ padding: 14, borderLeft: "4px solid var(--color-error)", backgroundColor: "var(--color-bg-secondary)", borderRadius: "0 8px 8px 0" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                            <strong style={{ color: "var(--color-error)", fontSize: "0.88rem" }}>{err.code}</strong>
                            <span style={{ fontSize: "0.72rem", padding: "2px 8px", backgroundColor: "rgba(239,68,68,0.1)", color: "var(--color-error)", borderRadius: 8 }}>{err.layer}</span>
                          </div>
                          <div style={{ fontSize: "0.88rem" }}>{err.message}</div>
                          {err.repairable && <div style={{ fontSize: "0.76rem", color: "var(--color-accent)", marginTop: 6, fontWeight: 600 }}>✨ Auto-repairable</div>}
                        </div>
                      ))}
                      {validationResult.warnings.map((w, idx) => (
                        <div key={`warn-${idx}`} style={{ padding: 14, borderLeft: "4px solid #eab308", backgroundColor: "var(--color-bg-secondary)", borderRadius: "0 8px 8px 0" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                            <strong style={{ color: "#eab308", fontSize: "0.88rem" }}>{w.code}</strong>
                            <span style={{ fontSize: "0.72rem", padding: "2px 8px", backgroundColor: "rgba(234,179,8,0.1)", color: "#eab308", borderRadius: 8 }}>{w.layer}</span>
                          </div>
                          <div style={{ fontSize: "0.88rem" }}>{w.message}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* ── JSON Output Tab ── */}
              {activeTab === "json_output" && (
                <div className="glass-card animate-slide-up" style={{ padding: 24 }}>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 20 }}>
                    {["intent", "architecture", "ui", "api", "db", "auth", "validation", "repair", "runtime"].map((s) => (
                      <button
                        key={s}
                        onClick={() => setActiveSchemaTab(s)}
                        style={{
                          padding: "6px 14px", borderRadius: 8,
                          border: "1.5px solid",
                          borderColor: activeSchemaTab === s ? "var(--color-accent)" : "var(--color-border)",
                          background: activeSchemaTab === s ? "var(--color-accent-glow)" : "transparent",
                          color: activeSchemaTab === s ? "var(--color-accent)" : "var(--color-text-secondary)",
                          fontWeight: activeSchemaTab === s ? 700 : 500,
                          cursor: "pointer",
                          textTransform: "uppercase",
                          fontSize: "0.75rem",
                          letterSpacing: "0.04em",
                          transition: "all 0.2s",
                        }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                  {activeSchemaTab === "intent" && intentResult && <JsonViewer data={intentResult} title="Intent JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "architecture" && architectureResult && <JsonViewer data={architectureResult} title="Architecture JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "ui" && schemasResult?.ui_schema && <JsonViewer data={schemasResult.ui_schema} title="UI Schema JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "api" && schemasResult?.api_schema && <JsonViewer data={schemasResult.api_schema} title="API Schema JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "db" && schemasResult?.db_schema && <JsonViewer data={schemasResult.db_schema} title="DB Schema JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "auth" && schemasResult?.auth_schema && <JsonViewer data={schemasResult.auth_schema} title="Auth Schema JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "validation" && validationResult && <JsonViewer data={validationResult} title="Validation JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "repair" && repairResult && <JsonViewer data={repairResult} title="Repair JSON" defaultExpanded={true} />}
                  {activeSchemaTab === "runtime" && runtimeResult && <JsonViewer data={runtimeResult} title="Runtime JSON" defaultExpanded={true} />}
                  {/* Empty state */}
                  {!["intent","architecture","ui","api","db","auth","validation","repair","runtime"].some(s => {
                    if (s === "intent") return !!intentResult;
                    if (s === "architecture") return !!architectureResult;
                    if (s === "ui") return !!schemasResult?.ui_schema;
                    if (s === "api") return !!schemasResult?.api_schema;
                    if (s === "db") return !!schemasResult?.db_schema;
                    if (s === "auth") return !!schemasResult?.auth_schema;
                    if (s === "validation") return !!validationResult;
                    if (s === "repair") return !!repairResult;
                    if (s === "runtime") return !!runtimeResult;
                    return false;
                  }) && activeSchemaTab && (
                    <div style={{ padding: 40, textAlign: "center", color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
                      No data available for this stage yet.
                    </div>
                  )}
                </div>
              )}

              {/* ── Repair Tab ── */}
              {activeTab === "repair" && repairResult && (
                <div className="glass-card animate-slide-up" style={{ padding: 24 }}>
                  <div style={{ marginBottom: 20 }}>
                    {!repairResult.repaired ? (
                      <div style={{ padding: 16, backgroundColor: "var(--color-bg-secondary)", borderRadius: 10, color: "var(--color-text-secondary)", fontWeight: 500 }}>{repairResult.message}</div>
                    ) : finalValidationResult?.is_valid ? (
                      <div style={{ padding: 16, backgroundColor: "var(--color-success-bg)", border: "1px solid var(--color-success)", borderRadius: 10, color: "var(--color-success)", fontWeight: 600, display: "flex", alignItems: "center", gap: 10 }}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="9 11 12 14 22 4"/></svg>
                        Repair complete. Configuration passed final validation.
                      </div>
                    ) : (
                      <div style={{ padding: 16, backgroundColor: "var(--color-error-bg)", border: "1px solid var(--color-error)", borderRadius: 10, color: "var(--color-error)", fontWeight: 600 }}>
                        Some issues could not be repaired automatically.
                      </div>
                    )}
                  </div>
                  {repairResult.repaired && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                        <h4 style={{ fontSize: "0.95rem", fontWeight: 700, margin: 0 }}>Repairs Applied ({repairResult.repair_summary.length})</h4>
                        <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Attempts: {repairResult.repair_attempts}</span>
                      </div>
                      {repairResult.repair_summary.map((s, idx) => (
                        <div key={`rep-${idx}`} style={{ padding: 14, borderLeft: "4px solid var(--color-accent)", backgroundColor: "var(--color-bg-secondary)", borderRadius: "0 8px 8px 0" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                            <strong style={{ color: "var(--color-accent)", fontSize: "0.88rem" }}>{s.action}</strong>
                            <span style={{ fontSize: "0.72rem", padding: "2px 8px", backgroundColor: "var(--color-success-bg)", color: "var(--color-success)", borderRadius: 8 }}>{s.error_code}</span>
                          </div>
                          <div style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", fontFamily: "monospace", marginBottom: 6 }}>Layer: {s.layer} | Path: {s.path}</div>
                          {(s.before !== undefined || s.after !== undefined) && (
                            <div style={{ display: "flex", gap: 10, fontSize: "0.82rem" }}>
                              {s.before != null && <div style={{ flex: 1, padding: 8, backgroundColor: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 6, wordBreak: "break-all" }}>
                                <div style={{ color: "var(--color-error)", fontSize: "0.72rem", marginBottom: 4, fontWeight: 700 }}>Before</div>
                                {typeof s.before === "object" ? JSON.stringify(s.before) : String(s.before)}
                              </div>}
                              {s.after != null && <div style={{ flex: 1, padding: 8, backgroundColor: "rgba(16,185,129,0.05)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 6, wordBreak: "break-all" }}>
                                <div style={{ color: "var(--color-success)", fontSize: "0.72rem", marginBottom: 4, fontWeight: 700 }}>After</div>
                                {typeof s.after === "object" ? JSON.stringify(s.after) : String(s.after)}
                              </div>}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* ── Runtime Preview Tab ── */}
              {activeTab === "runtime" && runtimeResult && (
                <div className="glass-card animate-slide-up" style={{ padding: 24 }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 500, color: "var(--color-text-muted)", marginBottom: 14, padding: "8px 12px", background: "var(--color-bg-secondary)", borderRadius: 8, display: "flex", alignItems: "center", gap: 6 }}
                    className="dark:bg-[var(--color-dark-bg-secondary)]">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    Runtime Preview generated from validated configuration — not a production app.
                  </div>
                  {runtimeResult.runtime_ready ? (
                    <div style={{ padding: 12, backgroundColor: "var(--color-success-bg)", border: "1px solid var(--color-success)", borderRadius: 8, color: "var(--color-success)", fontWeight: 600, display: "flex", alignItems: "center", gap: 8, marginBottom: 20, fontSize: "0.88rem" }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="9 11 12 14 22 4"/></svg>
                      Configuration is executable — runtime preview generated.
                    </div>
                  ) : (
                    <div style={{ padding: 12, backgroundColor: "var(--color-error-bg)", border: "1px solid var(--color-error)", borderRadius: 8, color: "var(--color-error)", fontWeight: 600, marginBottom: 20, fontSize: "0.88rem" }}>
                      Runtime simulation failed.
                    </div>
                  )}

                  {runtimeResult.runtime_ready && runtimeResult.preview_app && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                      <div style={{ display: "flex", gap: 12 }}>
                        {[
                          { label: "Pages", value: runtimeResult.pages_rendered },
                          { label: "Components", value: runtimeResult.components_rendered.length },
                          { label: "Warnings", value: runtimeResult.runtime_warnings.length, warn: runtimeResult.runtime_warnings.length > 0 },
                        ].map((m) => (
                          <div key={m.label} style={{ flex: 1, padding: "12px 16px", backgroundColor: "var(--color-bg-secondary)", borderRadius: 10 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                            <div style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)" }}>{m.label}</div>
                            <div style={{ fontSize: "1.3rem", fontWeight: 800, color: m.warn ? "#eab308" : "var(--color-text-primary)" }}>{m.value}</div>
                          </div>
                        ))}
                      </div>

                      {/* App Shell */}
                      <div style={{ border: "1px solid var(--color-border)", borderRadius: 12, overflow: "hidden", display: "flex", minHeight: 440 }}>
                        {/* Sidebar Nav */}
                        <div style={{ width: 200, backgroundColor: "var(--color-bg-secondary)", borderRight: "1px solid var(--color-border)", padding: "20px 14px", flexShrink: 0 }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                          <div style={{ fontWeight: 800, fontSize: "0.92rem", marginBottom: 20, padding: "0 8px" }}>{runtimeResult.preview_app.app_name}</div>
                          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                            {runtimeResult.preview_app.navigation.map((nav, i) => (
                              <button
                                key={`nav-${i}`}
                                onClick={() => setActivePreviewTab(i)}
                                style={{
                                  padding: "8px 12px", borderRadius: 8,
                                  background: i === activePreviewTab ? "var(--color-accent)" : "transparent",
                                  color: i === activePreviewTab ? "white" : "var(--color-text-secondary)",
                                  fontSize: "0.85rem", cursor: "pointer", border: "none",
                                  textAlign: "left", fontWeight: i === activePreviewTab ? 600 : 500,
                                  transition: "all 0.2s",
                                }}
                              >
                                {nav.label}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Page Content */}
                        <div style={{ flex: 1, padding: 28, overflowY: "auto" }}>
                          {runtimeResult.preview_app.pages[activePreviewTab] && (() => {
                            const page = runtimeResult.preview_app.pages[activePreviewTab];
                            return (
                              <>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border)", paddingBottom: 14, marginBottom: 24 }}>
                                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700, margin: 0 }}>{page.name}</h2>
                                  <div style={{ display: "flex", gap: 8 }}>
                                    {page.auth_required && (
                                      <span style={{ fontSize: "0.72rem", padding: "3px 10px", backgroundColor: "rgba(234,179,8,0.1)", color: "#eab308", border: "1px solid rgba(234,179,8,0.3)", borderRadius: 999, fontWeight: 600 }}>
                                        🔒 Protected
                                      </span>
                                    )}
                                    <span style={{ fontSize: "0.72rem", padding: "3px 10px", backgroundColor: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", borderRadius: 999, fontFamily: "monospace" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                                      {page.route}
                                    </span>
                                  </div>
                                </div>
                                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                                  {page.components.map((comp, i) => (
                                    <div key={`comp-${i}`} style={{ padding: 20, border: "1.5px dashed var(--color-border)", borderRadius: 12, position: "relative" }}>
                                      <span style={{ position: "absolute", top: -10, left: 14, fontSize: "0.65rem", padding: "2px 10px", backgroundColor: "var(--color-bg-card)", border: "1px solid var(--color-border)", borderRadius: 999, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }} className="dark:bg-[var(--color-dark-bg-card)]">
                                        {comp.runtime_type}
                                      </span>
                                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                                        <strong style={{ fontSize: "1rem" }}>{comp.label}</strong>
                                        {comp.data_source && (
                                          <span style={{ fontSize: "0.7rem", padding: "2px 8px", backgroundColor: "rgba(99,102,241,0.1)", color: "var(--color-accent)", borderRadius: 6, fontFamily: "monospace" }}>{comp.data_source}</span>
                                        )}
                                      </div>
                                      {/* Component mocks */}
                                      {comp.runtime_type === "table" && (
                                        <div style={{ border: "1px solid var(--color-border)", borderRadius: 8, overflow: "hidden" }}>
                                          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", padding: "10px 16px", backgroundColor: "var(--color-bg-secondary)", fontWeight: 600, fontSize: "0.8rem", color: "var(--color-text-secondary)" }} className="dark:bg-[var(--color-dark-bg-secondary)]">
                                            <span>Column 1</span><span>Column 2</span><span>Column 3</span><span>Status</span>
                                          </div>
                                          {[1,2,3].map(r => (
                                            <div key={r} style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", padding: "10px 16px", borderTop: "1px solid var(--color-border)" }}>
                                              {[60,80,40].map((w, ci) => <div key={ci} style={{ height: 8, width: `${w}%`, backgroundColor: "var(--color-border)", borderRadius: 4 }} />)}
                                              <span style={{ fontSize: "0.72rem", padding: "2px 8px", backgroundColor: "var(--color-success-bg)", color: "var(--color-success)", borderRadius: 8, fontWeight: 600, alignSelf: "center", width: "fit-content" }}>Active</span>
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                      {comp.runtime_type === "form" && (
                                        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                                          {["Field One", "Field Two"].map(f => (
                                            <div key={f}>
                                              <div style={{ fontSize: "0.78rem", fontWeight: 600, marginBottom: 6 }}>{f}</div>
                                              <div style={{ height: 38, border: "1.5px solid var(--color-border)", borderRadius: 8, backgroundColor: "var(--color-bg-input)" }} />
                                            </div>
                                          ))}
                                          <div style={{ height: 40, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 700, fontSize: "0.88rem" }}>Submit</div>
                                        </div>
                                      )}
                                      {comp.runtime_type === "stat_card" && (
                                        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                                          <div style={{ width: 52, height: 52, borderRadius: 14, backgroundColor: "var(--color-accent-glow)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--color-accent)" }}>
                                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                                          </div>
                                          <div>
                                            <div style={{ fontSize: "0.82rem", color: "var(--color-text-secondary)", fontWeight: 500 }}>Metric</div>
                                            <div style={{ fontSize: "2rem", fontWeight: 800 }}>8,492</div>
                                          </div>
                                        </div>
                                      )}
                                      {comp.runtime_type === "chart" && (
                                        <div style={{ height: 140, display: "flex", alignItems: "flex-end", gap: "4%", padding: "0 8px", borderBottom: "2px solid var(--color-border)" }}>
                                          {[40,70,45,90,65,85,60].map((h, ci) => (
                                            <div key={ci} style={{ flex: 1, height: `${h}%`, background: `linear-gradient(180deg, #6366f1, #8b5cf6)`, borderRadius: "6px 6px 0 0", opacity: 0.55 + ci * 0.06 }} />
                                          ))}
                                        </div>
                                      )}
                                      {["card","modal","text","button","nav"].includes(comp.runtime_type) && (
                                        <div style={{ height: 80, border: "2px dashed var(--color-border)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--color-text-muted)", fontSize: "0.85rem", fontWeight: 500 }}>
                                          Interactive {comp.runtime_type} container
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </>
                            );
                          })()}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ── Modify App Section ── */}
          {!isLoading && hasResults && (
            <div className="glass-card animate-slide-up" style={{ padding: 24, marginTop: 8 }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Modify Existing App
                <span style={{ fontSize: "0.7rem", padding: "2px 8px", backgroundColor: "rgba(99,102,241,0.1)", color: "var(--color-accent)", borderRadius: 999, fontWeight: 600 }}>PATCH MODE</span>
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", marginBottom: 14 }}>Describe a change and only the affected pipeline stages will re-run.</p>

              {clarificationNeeded && (
                <div style={{ padding: 16, backgroundColor: "rgba(234,179,8,0.1)", border: "1px solid #eab308", borderRadius: 10, marginBottom: 14 }}>
                  <div style={{ fontWeight: 700, color: "#eab308", marginBottom: 10, fontSize: "0.88rem" }}>⚠ Clarification needed</div>
                  {clarificationQuestions.map((q, i) => <div key={i} style={{ fontSize: "0.85rem", marginBottom: 4 }}>• {q}</div>)}
                </div>
              )}
              {patchSummary.length > 0 && (
                <div style={{ padding: 16, backgroundColor: "var(--color-success-bg)", border: "1px solid var(--color-success)", borderRadius: 10, marginBottom: 14 }}>
                  <div style={{ fontWeight: 700, color: "var(--color-success)", marginBottom: 8, fontSize: "0.88rem" }}>✓ Patch applied — {changeType}</div>
                  {patchSummary.map((s, i) => <div key={i} style={{ fontSize: "0.82rem", marginBottom: 3 }}>• {s}</div>)}
                </div>
              )}

              <textarea
                value={modifyPrompt}
                onChange={(e) => setModifyPrompt(e.target.value)}
                placeholder='e.g. "Add a premium billing page" or "Remove the reports module"'
                className="input-area"
                style={{ minHeight: 90, fontSize: "0.9rem", boxSizing: "border-box" }}
                disabled={isModifying}
              />
              <div style={{ marginTop: 10 }}>
                <button
                  onClick={handleModifyPipeline}
                  disabled={modifyPrompt.length < 3 || isModifying}
                  style={{
                    padding: "11px 24px",
                    borderRadius: 10,
                    background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
                    color: "white", border: "none", cursor: "pointer",
                    fontWeight: 700, fontSize: "0.9rem",
                    display: "flex", alignItems: "center", gap: 8,
                    opacity: (modifyPrompt.length < 3 || isModifying) ? 0.6 : 1,
                    transition: "all 0.2s",
                  }}
                >
                  {isModifying ? (
                    <><span style={{ width: 15, height: 15, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.8s linear infinite", display: "inline-block" }} />Applying Patch...</>
                  ) : (
                    <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Apply Patch</>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── Right Sidebar ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <PipelineVisualizer stages={stages} />

          {/* Tips card */}
          <div className="glass-card" style={{ padding: 20 }}>
            <h4 style={{ fontSize: "0.85rem", fontWeight: 700, marginBottom: 12, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Tips</h4>
            {[
              "Include user roles for better auth schemas",
              "Mention premium/paid features explicitly",
              "Name key entities (products, orders, users)",
              "Specify which pages are admin-only",
            ].map((tip) => (
              <div key={tip} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 10, fontSize: "0.82rem", color: "var(--color-text-secondary)" }}>
                <span style={{ color: "var(--color-success)", flexShrink: 0, marginTop: 1 }}>✓</span>
                {tip}
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        .animate-slide-up { animation: fadeIn 0.4s cubic-bezier(0.4,0,0.2,1) forwards; }
        @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr !important; } }
      `}</style>
    </div>
  );
}
