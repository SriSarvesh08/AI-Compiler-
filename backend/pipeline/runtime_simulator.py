"""
Runtime Simulator — Stage 6 of the Compiler Pipeline.

Simulates the generated application by converting the UI schema
into a working app preview block. Verifies that all components
have necessary API bindings and Auth bindings.
"""

import logging
import time

from schemas.architecture_schema import SchemaGenerationOutput
from schemas.validation_schema import ValidationOutput
from schemas.runtime_schema import (
    RuntimeOutput,
    ExecutionReport,
    RenderedComponent,
    PreviewApp,
    PreviewNavigation,
    PreviewPage,
    PreviewComponent,
)

logger = logging.getLogger(__name__)

SUPPORTED_COMPONENTS = {
    "table", "form", "input", "button", "card", "chart",
    "sidebar", "navbar", "modal", "text", "stat_card"
}


class RuntimeSimulator:
    """Simulates the generated application to verify execution correctness.

    Uses strict rule-based bindings to link UI components to APIs and
    Auth structures. Generates a visual PreviewApp schema.
    """

    def __init__(self):
        """Initialize the deterministic Runtime Simulator."""
        logger.info("RuntimeSimulator initialized in deterministic mode")

    def simulate(self, schemas: SchemaGenerationOutput, final_validation: ValidationOutput) -> tuple[RuntimeOutput, float]:
        """Simulate the generated application.

        Args:
            schemas: Final schema specifications.
            final_validation: The validation report prior to simulation.

        Returns:
            Tuple of (RuntimeOutput, simulation_time_ms)
        """
        start_time = time.perf_counter()
        logger.info("Starting runtime simulation")

        if not final_validation.is_valid:
            logger.warning("Simulation skipped because final validation failed.")
            output = RuntimeOutput(
                runtime_ready=False,
                message="Runtime simulation skipped because final validation failed"
            )
            return output, (time.perf_counter() - start_time) * 1000

        # Build mapping caches
        api_endpoints = {ep.path for ep in schemas.api_schema.endpoints} if schemas.api_schema else set()
        protected_routes = {pr.route for pr in schemas.auth_schema.protected_routes} if schemas.auth_schema else set()
        db_tables = {t.name for t in schemas.db_schema.tables} if schemas.db_schema else set()

        report = ExecutionReport()
        warnings = []
        rendered_components = []
        routes = []
        preview_pages = []
        preview_nav = []

        runtime_ready = True
        app_name = "Generated Application"

        for page in schemas.ui_schema.pages:
            routes.append(page.route)
            
            # Auth Binding
            auth_required = False
            if any(page.route == pr or page.route.startswith(pr.replace("/*", "")) for pr in protected_routes):
                auth_required = True

            # Add to navigation
            preview_nav.append(PreviewNavigation(label=page.name, route=page.route))

            page_components = []

            for comp in page.components:
                c_type = comp.type.lower()
                status = "renderable"
                
                if c_type not in SUPPORTED_COMPONENTS:
                    warnings.append(f"Unknown component type '{c_type}' on page '{page.name}'. Using fallback 'card'.")
                    c_type = "card"
                    status = "warning"

                # API Binding
                data_source = None
                if comp.data_source:
                    data_source = comp.data_source
                    # Check if API exists
                    if data_source not in api_endpoints and not any(data_source.startswith(ep.split("{")[0]) for ep in api_endpoints):
                        warnings.append(f"Component '{comp.name}' data_source '{data_source}' not found in API schema.")
                        report.api_bindings_valid = False
                        runtime_ready = False
                        status = "error"

                rendered_components.append(RenderedComponent(
                    page=page.name,
                    component=comp.name,
                    status=status
                ))

                page_components.append(PreviewComponent(
                    runtime_type=c_type,
                    label=comp.name,
                    data_source=data_source,
                    render_status="ready" if status != "error" else "error"
                ))

            preview_pages.append(PreviewPage(
                name=page.name,
                route=page.route,
                layout=page.layout or "dashboard",
                auth_required=auth_required,
                components=page_components
            ))

        # DB Binding Weak Check (Just for warnings)
        for ep in schemas.api_schema.endpoints:
            if ep.response_body:
                for k in ep.response_body.keys():
                    if k not in ["success", "token", "error", "message"]:
                        if not any(k.lower() in t.lower() or t.lower() in k.lower() for t in db_tables):
                            warnings.append(f"API endpoint '{ep.path}' returns '{k}' which weakly maps to DB tables.")

        preview_app = PreviewApp(
            app_name=app_name,
            navigation=preview_nav,
            pages=preview_pages
        )

        if len(preview_pages) < len(schemas.ui_schema.pages):
            warnings.append(f"Only {len(preview_pages)} of {len(schemas.ui_schema.pages)} pages were successfully simulated.")
            runtime_ready = False

        output = RuntimeOutput(
            runtime_ready=runtime_ready,
            message="Runtime simulation successful" if runtime_ready else "Runtime simulation failed due to binding errors",
            pages_rendered=len(preview_pages),
            routes=routes,
            components_rendered=rendered_components,
            execution_report=report,
            runtime_warnings=warnings,
            preview_app=preview_app
        )

        sim_time_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Runtime Simulation Complete | "
            f"Ready: {runtime_ready} | "
            f"Pages: {output.pages_rendered} | "
            f"Time: {sim_time_ms:.2f}ms"
        )
        return output, sim_time_ms
