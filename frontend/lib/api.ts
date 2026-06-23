/**
 * API client for the AI Application Compiler backend.
 *
 * All API calls go through this module for centralized error handling
 * and type safety.
 */

import { IntentResponse, DesignResponse, SchemaGenerationResponse, ValidationResponse, RepairResponse, RuntimeResponse, FullPipelineResponse, ModifyResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Helper to get authorization headers
 */
function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * Extract intent from a natural language prompt.
 *
 * Calls POST /generate/intent on the FastAPI backend.
 *
 * @param prompt - The user's application description
 * @returns IntentResponse with success status and extracted intent
 * @throws Error if the network request fails
 */
export async function generateIntent(prompt: string): Promise<IntentResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/intent`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        intent: null,
        error: errorMessage,
        extraction_time_ms: 0,
      };
    }

    const data: IntentResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<IntentResponse>(error, {
      success: false,
      intent: null,
      error: "",
      extraction_time_ms: 0,
    });
  }
}

/**
 * Generate system design from extracted intent.
 *
 * Calls POST /generate/design on the FastAPI backend.
 *
 * @param intent - The extracted intent from Stage 1
 * @returns DesignResponse with success status and generated architecture
 */
export async function generateDesign(
  intent: { domain: string; features: string[]; roles: string[] }
): Promise<DesignResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/design`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ intent }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        architecture: null,
        error: errorMessage,
        design_time_ms: 0,
      };
    }

    const data: DesignResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<DesignResponse>(error, {
      success: false,
      architecture: null,
      error: "",
      design_time_ms: 0,
    });
  }
}

/**
 * Generate specific schemas from application architecture.
 *
 * Calls POST /generate/schema on the FastAPI backend.
 *
 * @param architecture - The generated architecture from Stage 2
 * @returns SchemaGenerationResponse with success status and generated schemas
 */
export async function generateSchema(
  architecture: any
): Promise<SchemaGenerationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/schema`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ architecture }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        schemas: null,
        error: errorMessage,
        generation_time_ms: 0,
      };
    }

    const data: SchemaGenerationResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<SchemaGenerationResponse>(error, {
      success: false,
      schemas: null,
      error: "",
      generation_time_ms: 0,
    });
  }
}

/**
 * Generate repairs for validation errors.
 *
 * Calls POST /generate/repair on the FastAPI backend.
 *
 * @param schemas - The flawed schemas
 * @param validation - The validation report detailing the errors
 * @returns RepairResponse with success status and repair results
 */
export async function generateRepair(
  schemas: any,
  validation: any
): Promise<RepairResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/repair`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ schemas, validation }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        before_validation: null,
        repair: null,
        after_validation: null,
        error: errorMessage,
      };
    }

    const data: RepairResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<RepairResponse>(error, {
      success: false,
      before_validation: null,
      repair: null,
      after_validation: null,
      error: "",
    });
  }
}

/**
 * Generate runtime simulation from schemas.
 *
 * Calls POST /generate/runtime on the FastAPI backend.
 *
 * @param schemas - The generated schemas
 * @param final_validation - The final validation report
 * @returns RuntimeResponse with simulation results
 */
export async function generateRuntime(
  schemas: any,
  final_validation: any
): Promise<RuntimeResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/runtime`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ schemas, final_validation }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        runtime: null,
        error: errorMessage,
      };
    }

    const data: RuntimeResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<RuntimeResponse>(error, {
      success: false,
      runtime: null,
      error: "",
    });
  }
}

/**
 * Run the full compiler pipeline.
 *
 * Calls POST /generate/full-pipeline on the FastAPI backend.
 *
 * @param prompt - The user's application description
 * @returns FullPipelineResponse with outputs from each completed stage
 */
export async function runFullPipeline(
  prompt: string
): Promise<FullPipelineResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/full-pipeline`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        stages: null,
        error: errorMessage,
        total_time_ms: 0,
      };
    }

    const data: FullPipelineResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<FullPipelineResponse>(error, {
      success: false,
      stages: null,
      error: "",
      total_time_ms: 0,
    });
  }
}

/**
 * Modify an existing pipeline generation with a new change request.
 *
 * Calls POST /generate/modify on the FastAPI backend.
 *
 * @param existing_stages - The currently generated pipeline stages
 * @param change_request - The natural language request to modify the app
 * @returns ModifyResponse with patched stages and summary
 */
export async function modifyPipeline(
  existing_stages: any,
  change_request: string
): Promise<ModifyResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/modify`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ existing_stages, change_request }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Server error: ${response.status} ${response.statusText}`;
      return {
        success: false,
        change_type: "error",
        clarification_needed: false,
        clarification_questions: [],
        patch_summary: [],
        updated_stages: null,
        error: errorMessage,
        total_time_ms: 0,
      };
    }

    const data: ModifyResponse = await response.json();
    return data;
  } catch (error) {
    return _handleNetworkError<ModifyResponse>(error, {
      success: false,
      change_type: "error",
      clarification_needed: false,
      clarification_questions: [],
      patch_summary: [],
      updated_stages: null,
      error: "",
      total_time_ms: 0,
    });
  }
}

/**
 * Shared network error handler for all API calls.
 */
function _handleNetworkError<T extends { error: string | null }>(
  error: unknown,
  fallback: T
): T {
  const message =
    error instanceof Error ? error.message : "Unknown error occurred";

  if (message.includes("fetch") || message.includes("Failed")) {
    return {
      ...fallback,
      error:
        "Cannot connect to the backend server. Make sure the FastAPI server is running on " +
        API_BASE_URL,
    };
  }

  return {
    ...fallback,
    error: `Request failed: ${message}`,
  };
}

// ──────────────────────────────────────────────
// Evaluation Framework
// ──────────────────────────────────────────────

export interface EvaluationSummary {
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  success_rate: number;
  runtime_ready_rate: number;
  average_latency_ms: number;
  average_repair_attempts: number;
  average_errors_before_repair: number;
  average_errors_after_repair: number;
  most_common_failure_types: {type: string; count: number}[];
  normal_prompt_success_rate: number;
  edge_case_success_rate: number;
}

export interface EvaluationResult {
  id: string;
  category: string;
  prompt: string;
  success: boolean;
  final_validation_passed: boolean;
  runtime_ready: boolean;
  repair_attempts: number;
  error_count_before_repair: number;
  error_count_after_repair: number;
  warning_count: number;
  latency_ms: number;
  failure_type: string | null;
  assumptions_count: number;
}

export interface EvaluationResponse {
  success: boolean;
  summary: EvaluationSummary;
  results: EvaluationResult[];
  message?: string;
}

export async function getEvaluationDataset(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluation/dataset`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error("Failed to fetch dataset");
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    return { success: false, dataset: [] };
  }
}

export async function runEvaluation(): Promise<EvaluationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluation/run`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    throw error;
  }
}

export async function getLatestEvaluation(): Promise<EvaluationResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluation/latest`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    if (!data.success) return null;
    return data;
  } catch (error) {
    console.error(error);
    return null;
  }
}
