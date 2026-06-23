"""
Validation Schema — Pydantic models for the Validation Engine stage.

Defines models for validation outputs including:
- Errors and warnings
- Validation reports
- Full validation response
"""

from pydantic import BaseModel, Field

from schemas.architecture_schema import SchemaGenerationOutput


class ValidationError(BaseModel):
    """An error found during validation."""
    code: str = Field(..., description="Error code (e.g., 'MISSING_REQUIRED_FIELD')")
    layer: str = Field(..., description="Schema layer where error occurred (e.g., 'ui_schema', 'api_schema')")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(default="error", description="Always 'error' for validation errors")
    repairable: bool = Field(..., description="Whether the Repair Engine could potentially fix this")
    path: str = Field(..., description="JSON path to the erroneous field (e.g., 'ui_schema.pages[0].route')")


class ValidationWarning(BaseModel):
    """A warning found during validation (non-blocking)."""
    code: str = Field(..., description="Warning code (e.g., 'UNMAPPED_RESPONSE_FIELD')")
    layer: str = Field(..., description="Schema layer where warning occurred")
    message: str = Field(..., description="Human-readable warning message")
    severity: str = Field(default="warning", description="Always 'warning' for validation warnings")
    repairable: bool = Field(default=False, description="Usually false for warnings")
    path: str = Field(..., description="JSON path to the field causing the warning")


class ValidationReport(BaseModel):
    """Summary report of validation results per layer."""
    ui_valid: bool = Field(default=True, description="Whether the UI schema passed validation")
    api_valid: bool = Field(default=True, description="Whether the API schema passed validation")
    db_valid: bool = Field(default=True, description="Whether the DB schema passed validation")
    auth_valid: bool = Field(default=True, description="Whether the Auth schema passed validation")
    cross_layer_valid: bool = Field(default=True, description="Whether cross-layer validation passed")


class ValidationOutput(BaseModel):
    """Complete output from the Validation Engine."""
    is_valid: bool = Field(..., description="True if no errors were found")
    errors: list[ValidationError] = Field(default_factory=list, description="List of validation errors")
    warnings: list[ValidationWarning] = Field(default_factory=list, description="List of validation warnings")
    validation_report: ValidationReport = Field(default_factory=ValidationReport, description="Layer-by-layer report")


class ValidationInput(BaseModel):
    """Input for the /generate/validate endpoint."""
    schemas: SchemaGenerationOutput = Field(..., description="The generated schemas to validate")


class ValidationResponse(BaseModel):
    """API response wrapper for validation endpoint."""
    success: bool = Field(..., description="Whether the validation process completed successfully")
    validation: ValidationOutput | None = Field(default=None, description="The validation results")
    error: str | None = Field(default=None, description="System error message if process failed")
    validation_time_ms: float = Field(default=0.0, description="Time taken to validate in ms")
