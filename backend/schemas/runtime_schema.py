"""
Runtime Schema — Pydantic models for the Runtime Simulator stage.

Defines models for tracking runtime execution status and generating
the interactive preview app JSON structure.
"""

from typing import Literal
from pydantic import BaseModel, Field

from schemas.architecture_schema import SchemaGenerationOutput
from schemas.validation_schema import ValidationOutput


class ExecutionReport(BaseModel):
    """Tracks the validity of runtime bindings."""
    ui_runtime_valid: bool = Field(default=True)
    api_bindings_valid: bool = Field(default=True)
    auth_bindings_valid: bool = Field(default=True)
    db_bindings_valid: bool = Field(default=True)


class RenderedComponent(BaseModel):
    """Tracks status of a single component rendered in the simulator."""
    page: str = Field(...)
    component: str = Field(...)
    status: Literal["renderable", "warning", "error"] = Field(...)


class PreviewComponent(BaseModel):
    """A component object ready for frontend rendering."""
    runtime_type: str = Field(..., description="Supported type like table, form, input, button")
    label: str = Field(...)
    data_source: str | None = Field(default=None)
    render_status: str = Field(default="ready")


class PreviewPage(BaseModel):
    """A page object ready for frontend rendering."""
    name: str = Field(...)
    route: str = Field(...)
    layout: str = Field(default="dashboard")
    auth_required: bool = Field(default=False)
    components: list[PreviewComponent] = Field(default_factory=list)


class PreviewNavigation(BaseModel):
    """Navigation link for the preview app."""
    label: str = Field(...)
    route: str = Field(...)


class PreviewApp(BaseModel):
    """The complete simulated app object for the frontend."""
    app_name: str = Field(...)
    navigation: list[PreviewNavigation] = Field(default_factory=list)
    pages: list[PreviewPage] = Field(default_factory=list)


class RuntimeOutput(BaseModel):
    """Complete output from the Runtime Simulator."""
    runtime_ready: bool = Field(..., description="Whether the app can be simulated")
    message: str | None = Field(default=None, description="Message if skipped or failed")
    pages_rendered: int = Field(default=0)
    routes: list[str] = Field(default_factory=list)
    components_rendered: list[RenderedComponent] = Field(default_factory=list)
    execution_report: ExecutionReport | None = Field(default=None)
    runtime_warnings: list[str] = Field(default_factory=list)
    preview_app: PreviewApp | None = Field(default=None)


class RuntimeInput(BaseModel):
    """Input payload for the standalone /generate/runtime endpoint."""
    schemas: SchemaGenerationOutput = Field(...)
    final_validation: ValidationOutput = Field(...)


class RuntimeResponse(BaseModel):
    """API response wrapper for the runtime endpoint."""
    success: bool = Field(...)
    runtime: RuntimeOutput | None = Field(default=None)
    error: str | None = Field(default=None)
