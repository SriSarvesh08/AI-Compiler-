"""
Auth Schema — Pydantic models for the Authentication/Authorization stage.

Defines models for auth specifications including:
- Authorization rules and role definitions
- Protected routes
"""

from pydantic import BaseModel, Field


class AuthRole(BaseModel):
    """A role definition with its permissions."""
    name: str = Field(..., description="Role name (e.g., 'admin', 'user')")
    permissions: list[str] = Field(..., description="List of permissions granted to this role")


class ProtectedRoute(BaseModel):
    """A route that requires specific roles to access."""
    route: str = Field(..., description="URL route pattern (e.g., '/dashboard/*')")
    allowed_roles: list[str] = Field(..., description="List of roles allowed to access this route")


class AuthSchema(BaseModel):
    """Complete authentication schema generated from architecture."""
    roles: list[AuthRole] = Field(..., description="List of all roles and their permissions")
    protected_routes: list[ProtectedRoute] = Field(..., description="List of route protection rules")
