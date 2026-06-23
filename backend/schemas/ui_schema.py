"""
UI Schema — Pydantic models for the UI/UX specification stage.

Defines models for UI specifications including:
- Page layouts and navigation structure
- Component hierarchy
- Required API endpoints
"""

from pydantic import BaseModel, Field


class UIComponent(BaseModel):
    """A UI component within a page."""
    type: str = Field(..., description="Component type (e.g., 'table', 'button', 'form')")
    name: str = Field(..., description="Component name in PascalCase")
    data_source: str | None = Field(None, description="API endpoint or data source for the component")
    action: str | None = Field(None, description="Action triggered by the component (e.g., 'open_modal')")


class UIPage(BaseModel):
    """A UI page specification."""
    name: str = Field(..., description="Human-readable page name")
    route: str = Field(..., description="URL route for the page")
    layout: str = Field(..., description="Layout template (e.g., 'dashboard', 'auth')")
    components: list[UIComponent] = Field(default_factory=list, description="List of components on the page")
    required_api_endpoints: list[str] = Field(default_factory=list, description="List of API endpoints required by this page")


class UISchema(BaseModel):
    """Complete UI schema generated from architecture."""
    pages: list[UIPage] = Field(..., description="List of all UI pages")
