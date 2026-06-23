"""
Modify Schema — Pydantic models for the /generate/modify endpoint.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ModifyInput(BaseModel):
    """Input schema for modifying an existing configuration."""
    existing_stages: dict = Field(
        ...,
        description="The latest full pipeline output stages dictionary."
    )
    change_request: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language description of the modification to make."
    )


class ModifyResponse(BaseModel):
    """API response wrapper for the modify endpoint."""
    success: bool = Field(
        ...,
        description="Whether the modification was successful"
    )
    change_type: str = Field(
        ...,
        description="Classified change type (e.g., add_feature, update_role)"
    )
    clarification_needed: bool = Field(
        default=False,
        description="True if the request was ambiguous"
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Questions to ask the user if clarification is needed"
    )
    patch_summary: list[str] = Field(
        default_factory=list,
        description="Summary of applied patches (e.g., 'Added pages: X', 'Updated roles')"
    )
    updated_stages: dict | None = Field(
        default=None,
        description="The newly updated pipeline stages dictionary"
    )
    error: str | None = Field(
        default=None,
        description="Error message (null on success)"
    )
    total_time_ms: float = Field(
        default=0.0,
        description="Total patch execution time in milliseconds"
    )
