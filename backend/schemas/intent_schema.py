"""
Intent Schema — Pydantic models for the Intent Extraction stage.

Defines the input/output contracts for the first stage of the compiler pipeline.
The IntentExtractor takes a natural language prompt and produces a structured
IntentOutput with domain, features, and roles.
"""

from pydantic import BaseModel, Field


class IntentInput(BaseModel):
    """Input schema for intent extraction endpoint."""
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language description of the application to build",
        examples=["Build a CRM with login, contacts, dashboard, role-based access and premium plans"],
    )


class IntentOutput(BaseModel):
    """Structured output from intent extraction.

    Represents the parsed intent from a user's natural language prompt,
    broken down into domain, features, and user roles.
    """
    domain: str = Field(
        ...,
        description="The application domain (e.g., CRM, E-Commerce, LMS)",
        examples=["CRM"],
    )
    features: list[str] = Field(
        ...,
        description="List of features extracted from the prompt, in snake_case",
        examples=[["login", "contacts", "dashboard", "role_based_access", "premium_plan"]],
    )
    roles: list[str] = Field(
        ...,
        description="List of user roles inferred from the prompt",
        examples=[["admin", "user"]],
    )
    access_rules: list[str] = Field(
        default_factory=list,
        description="List of restricted access rules or permission constraints mentioned",
        examples=[["doctors can access patient records", "faculty cannot access patient records"]],
    )


class IntentResponse(BaseModel):
    """API response wrapper for intent extraction."""
    success: bool = Field(
        ...,
        description="Whether the extraction was successful",
    )
    intent: IntentOutput | None = Field(
        default=None,
        description="Extracted intent data (null on failure)",
    )
    error: str | None = Field(
        default=None,
        description="Error message (null on success)",
    )
    extraction_time_ms: float = Field(
        default=0.0,
        description="Time taken for extraction in milliseconds",
    )
