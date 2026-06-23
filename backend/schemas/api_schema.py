"""
API Schema — Pydantic models for the API specification stage.

Defines models for generated API specifications including:
- REST endpoints (method, path, parameters, responses)
- Request/response body schemas
- Authentication requirements per endpoint
"""

from typing import Any
from pydantic import BaseModel, Field


class APIEndpoint(BaseModel):
    """A REST API endpoint specification."""
    path: str = Field(..., description="Endpoint path (e.g., '/api/users')")
    method: str = Field(..., description="HTTP method (e.g., 'GET', 'POST')")
    description: str = Field(..., description="Description of what the endpoint does")
    request_body: dict[str, Any] = Field(default_factory=dict, description="Schema for request body")
    response_body: dict[str, Any] = Field(default_factory=dict, description="Schema for response body")
    auth_required: bool = Field(default=True, description="Whether authentication is required")
    allowed_roles: list[str] = Field(default_factory=list, description="Roles allowed to access this endpoint")


class APISchema(BaseModel):
    """Complete API schema generated from architecture."""
    endpoints: list[APIEndpoint] = Field(..., description="List of all API endpoints")
