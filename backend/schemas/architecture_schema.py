"""
Architecture Schema — Pydantic models for the System Design stage (Stage 2).

Defines the structured output of the SystemDesigner pipeline stage.
The SystemDesigner takes an IntentOutput and produces an ApplicationArchitecture
with entities, pages, flows, role permissions, and assumptions.
"""

from pydantic import BaseModel, Field

from schemas.intent_schema import IntentOutput
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DatabaseSchema
from schemas.auth_schema import AuthSchema


# ──────────────────────────────────────────────
# Component Models
# ──────────────────────────────────────────────


class Entity(BaseModel):
    """A data entity / database model for the application."""
    name: str = Field(
        ...,
        description="Entity name in PascalCase (e.g., 'User', 'Contact')",
        examples=["User", "Contact"],
    )
    description: str = Field(
        ...,
        description="Brief description of what this entity stores",
        examples=["Stores user account and authentication information"],
    )


class Page(BaseModel):
    """A UI page / screen in the application."""
    name: str = Field(
        ...,
        description="Human-readable page name",
        examples=["Dashboard", "Login"],
    )
    route: str = Field(
        ...,
        description="URL route for the page",
        examples=["/dashboard", "/login"],
    )
    purpose: str = Field(
        ...,
        description="Brief description of the page's purpose",
        examples=["Show overview and analytics"],
    )


class Flow(BaseModel):
    """A user flow / workflow in the application."""
    name: str = Field(
        ...,
        description="Human-readable name for the flow",
        examples=["User Login Flow"],
    )
    steps: list[str] = Field(
        ...,
        description="Ordered list of steps in the flow",
        examples=[["User enters email and password", "System validates credentials"]],
    )


class RolePermission(BaseModel):
    """A role and its associated permissions."""
    name: str = Field(
        ...,
        description="Role name in lowercase",
        examples=["admin", "user"],
    )
    permissions: list[str] = Field(
        ...,
        description="List of permissions granted to this role, in snake_case",
        examples=[["view_dashboard", "manage_contacts", "manage_users"]],
    )


# ──────────────────────────────────────────────
# Main Output Model
# ──────────────────────────────────────────────


class ApplicationArchitecture(BaseModel):
    """Complete application architecture produced by the System Design stage.

    Contains all structural decisions: entities, pages, flows,
    role permissions, and assumptions made during design.
    """
    app_name: str = Field(
        ...,
        description="Generated application name",
        examples=["CRM Management System"],
    )
    entities: list[Entity] = Field(
        ...,
        description="Data entities / database models",
    )
    pages: list[Page] = Field(
        ...,
        description="UI pages / screens",
    )
    flows: list[Flow] = Field(
        ...,
        description="User flows / workflows",
    )
    roles: list[RolePermission] = Field(
        ...,
        description="Role-based permission mappings",
    )
    assumptions: list[str] = Field(
        ...,
        description="Design assumptions and decisions made",
        examples=[["Email and password authentication is used by default"]],
    )


# ──────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────


class DesignInput(BaseModel):
    """Input schema for the /generate/design endpoint."""
    intent: IntentOutput = Field(
        ...,
        description="Structured intent output from Stage 1",
    )


class DesignResponse(BaseModel):
    """API response wrapper for the system design endpoint."""
    success: bool = Field(
        ...,
        description="Whether the design generation was successful",
    )
    architecture: ApplicationArchitecture | None = Field(
        default=None,
        description="Generated architecture (null on failure)",
    )
    error: str | None = Field(
        default=None,
        description="Error message (null on success)",
    )
    design_time_ms: float = Field(
        default=0.0,
        description="Time taken for design generation in milliseconds",
    )


class SchemaGenerationInput(BaseModel):
    """Input schema for the /generate/schema endpoint."""
    architecture: ApplicationArchitecture = Field(
        ...,
        description="Structured application architecture from Stage 2",
    )


class SchemaGenerationOutput(BaseModel):
    """Output wrapper for the four generated schemas."""
    ui_schema: UISchema | None = None
    api_schema: APISchema | None = None
    db_schema: DatabaseSchema | None = None
    auth_schema: AuthSchema | None = None


class SchemaGenerationResponse(BaseModel):
    """API response wrapper for the schema generation endpoint."""
    success: bool = Field(
        ...,
        description="Whether the schema generation was successful",
    )
    schemas: SchemaGenerationOutput | None = Field(
        default=None,
        description="Generated schemas (null on failure)",
    )
    error: str | None = Field(
        default=None,
        description="Error message (null on success)",
    )
    generation_time_ms: float = Field(
        default=0.0,
        description="Time taken for schema generation in milliseconds",
    )


class FullPipelineInput(BaseModel):
    """Input schema for the /generate/full-pipeline endpoint."""
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language description of the application to build",
    )


class FullPipelineResponse(BaseModel):
    """API response wrapper for the full pipeline endpoint."""
    success: bool = Field(
        ...,
        description="Whether the full pipeline run was successful",
    )
    stages: dict | None = Field(
        default=None,
        description="Output from each completed pipeline stage. Includes intent, architecture, schemas, validation, repair, final_validation, and runtime.",
    )
    error: str | None = Field(
        default=None,
        description="Error message (null on success)",
    )
    total_time_ms: float = Field(
        default=0.0,
        description="Total pipeline execution time in milliseconds",
    )
