"""
Repair Schema — Pydantic models for the Repair Engine stage.

Defines models for tracking automated repair actions:
- Repair action summaries
- Full repair engine output wrapper
"""

from typing import Any
from pydantic import BaseModel, Field

from schemas.architecture_schema import SchemaGenerationOutput
from schemas.validation_schema import ValidationOutput


class RepairSummary(BaseModel):
    """Tracks a single automated repair action."""
    error_code: str = Field(..., description="The validation error code being fixed")
    layer: str = Field(..., description="The schema layer being repaired (e.g., 'ui_schema')")
    path: str = Field(..., description="JSON path to the repaired field")
    action: str = Field(..., description="Description of the action taken")
    before: Any = Field(None, description="Value before repair")
    after: Any = Field(None, description="Value after repair")


class RepairOutput(BaseModel):
    """Complete output from the Repair Engine."""
    repaired: bool = Field(default=False, description="Whether any repairs were made")
    repair_attempts: int = Field(default=0, description="Number of passes the repair engine took")
    repair_summary: list[RepairSummary] = Field(default_factory=list, description="List of all repairs made")
    message: str = Field(default="", description="Summary message of the repair outcome")
    repaired_schemas: SchemaGenerationOutput | None = Field(default=None, description="The newly repaired schemas")


class RepairInput(BaseModel):
    """Input payload for the standalone /generate/repair endpoint."""
    schemas: SchemaGenerationOutput = Field(..., description="The flawed schemas to repair")
    validation: ValidationOutput = Field(..., description="The validation report detailing the errors")


class RepairResponse(BaseModel):
    """API response wrapper for the repair endpoint."""
    success: bool = Field(..., description="Whether the endpoint executed without crashing")
    before_validation: ValidationOutput | None = Field(default=None, description="Validation state before repairs")
    repair: RepairOutput | None = Field(default=None, description="Details of the repairs made")
    after_validation: ValidationOutput | None = Field(default=None, description="Validation state after repairs")
    error: str | None = Field(default=None, description="System error message if process failed")
