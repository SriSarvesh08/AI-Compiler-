/**
 * TypeScript types mirroring the backend Pydantic schemas.
 * Shared contract between frontend and backend.
 */

/** Input for the intent extraction endpoint */
export interface IntentInput {
  prompt: string;
}

/** Structured output from intent extraction */
export interface IntentOutput {
  domain: string;
  features: string[];
  roles: string[];
}

/** API response wrapper for intent extraction */
export interface IntentResponse {
  success: boolean;
  intent: IntentOutput | null;
  error: string | null;
  extraction_time_ms: number;
}

/** A data entity in the application architecture */
export interface Entity {
  name: string;
  description: string;
}

/** A UI page in the application architecture */
export interface PageSpec {
  name: string;
  route: string;
  purpose: string;
}

/** A user flow in the application architecture */
export interface Flow {
  name: string;
  steps: string[];
}

/** A role with its permissions */
export interface RolePermission {
  name: string;
  permissions: string[];
}

/** Complete application architecture from System Design stage */
export interface ApplicationArchitecture {
  app_name: string;
  entities: Entity[];
  pages: PageSpec[];
  flows: Flow[];
  roles: RolePermission[];
  assumptions: string[];
}

export interface UIComponent {
  type: string;
  name: string;
  data_source: string | null;
  action: string | null;
}

export interface UIPage {
  name: string;
  route: string;
  layout: string;
  components: UIComponent[];
  required_api_endpoints: string[];
}

export interface UISchema {
  pages: UIPage[];
}

export interface APIEndpoint {
  path: string;
  method: string;
  description: string;
  request_body: any;
  response_body: any;
  auth_required: boolean;
  allowed_roles: string[];
}

export interface APISchema {
  endpoints: APIEndpoint[];
}

export interface Column {
  name: string;
  type: string;
  required: boolean;
  relation: string | null;
}

export interface Table {
  name: string;
  columns: Column[];
}

export interface DatabaseSchema {
  tables: Table[];
}

export interface AuthRole {
  name: string;
  permissions: string[];
}

export interface ProtectedRoute {
  route: string;
  allowed_roles: string[];
}

export interface AuthSchema {
  roles: AuthRole[];
  protected_routes: ProtectedRoute[];
}

export interface SchemaGenerationOutput {
  ui_schema: UISchema | null;
  api_schema: APISchema | null;
  db_schema: DatabaseSchema | null;
  auth_schema: AuthSchema | null;
}

export interface ValidationError {
  code: string;
  layer: string;
  message: string;
  severity: string;
  repairable: boolean;
  path: string;
}

export interface ValidationWarning {
  code: string;
  layer: string;
  message: string;
  severity: string;
  repairable: boolean;
  path: string;
}

export interface ValidationReport {
  ui_valid: boolean;
  api_valid: boolean;
  db_valid: boolean;
  auth_valid: boolean;
  cross_layer_valid: boolean;
}

export interface ValidationOutput {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  validation_report: ValidationReport;
}

export interface RepairSummary {
  error_code: string;
  layer: string;
  path: string;
  action: string;
  before: any;
  after: any;
}

export interface RepairOutput {
  repaired: boolean;
  repair_attempts: number;
  repair_summary: RepairSummary[];
  message: string;
  repaired_schemas: SchemaGenerationOutput | null;
}

export interface ExecutionReport {
  ui_runtime_valid: boolean;
  api_bindings_valid: boolean;
  auth_bindings_valid: boolean;
  db_bindings_valid: boolean;
}

export interface RenderedComponent {
  page: string;
  component: string;
  status: "renderable" | "warning" | "error";
}

export interface PreviewComponent {
  runtime_type: string;
  label: string;
  data_source: string | null;
  render_status: string;
}

export interface PreviewPage {
  name: string;
  route: string;
  layout: string;
  auth_required: boolean;
  components: PreviewComponent[];
}

export interface PreviewNavigation {
  label: string;
  route: string;
}

export interface PreviewApp {
  app_name: string;
  navigation: PreviewNavigation[];
  pages: PreviewPage[];
}

export interface RuntimeOutput {
  runtime_ready: boolean;
  message: string | null;
  pages_rendered: number;
  routes: string[];
  components_rendered: RenderedComponent[];
  execution_report: ExecutionReport | null;
  runtime_warnings: string[];
  preview_app: PreviewApp | null;
}

/** API response wrapper for design generation */
export interface DesignResponse {
  success: boolean;
  architecture: ApplicationArchitecture | null;
  error: string | null;
  design_time_ms: number;
}

/** API response wrapper for full pipeline */
export interface FullPipelineResponse {
  success: boolean;
  stages: {
    intent?: IntentOutput;
    architecture?: ApplicationArchitecture;
    schemas?: SchemaGenerationOutput;
    validation?: ValidationOutput;
    repair?: RepairOutput;
    final_validation?: ValidationOutput;
    runtime?: RuntimeOutput;
  } | null;
  error: string | null;
  total_time_ms: number;
}

/** API response wrapper for modify endpoint */
export interface ModifyResponse {
  success: boolean;
  change_type: string;
  clarification_needed: boolean;
  clarification_questions: string[];
  patch_summary: string[];
  updated_stages: {
    intent?: IntentOutput;
    architecture?: ApplicationArchitecture;
    schemas?: SchemaGenerationOutput;
    validation?: ValidationOutput;
    repair?: RepairOutput;
    final_validation?: ValidationOutput;
    runtime?: RuntimeOutput;
  } | null;
  error: string | null;
  total_time_ms: number;
}

/** Pipeline stage status */
export type StageStatus = "idle" | "active" | "completed" | "error" | "locked";

/** Individual pipeline stage */
export interface PipelineStage {
  id: string;
  label: string;
  status: StageStatus;
  description: string;
}
