"""
Validator — Stage 4 of the Compiler Pipeline.

Validates the generated schemas and specifications for:
- Schema consistency and completeness
- Cross-reference integrity (e.g., API endpoints match DB tables)
- Required structural fields
- Type constraints

This validation is entirely rule-based and deterministic.
"""

import logging
import time

from schemas.architecture_schema import SchemaGenerationOutput
from schemas.validation_schema import (
    ValidationOutput,
    ValidationError,
    ValidationWarning,
    ValidationReport,
)

logger = logging.getLogger(__name__)


class Validator:
    """Validates generated specifications for consistency and correctness.

    Implements a strict, rule-based deterministic validation engine.
    Does not rely on LLM logic.
    """

    def __init__(self):
        """Initialize the deterministic Validator."""
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationWarning] = []
        self.report = ValidationReport()
        logger.info("Validator initialized in deterministic rule-based mode")

    def validate(self, schemas: SchemaGenerationOutput, intent=None) -> tuple[ValidationOutput, float]:
        """Validate generated schemas.

        Args:
            schemas: Generated schema specifications from Stage 3.
            intent: Optional IntentOutput from Stage 1 to perform completeness checks.

        Returns:
            Tuple of (ValidationOutput, validation_time_ms)
        """
        logger.info("Starting schema validation")
        start_time = time.perf_counter()

        # Reset state for this run
        self.errors = []
        self.warnings = []
        self.report = ValidationReport()

        if not schemas:
            self.errors.append(
                ValidationError(
                    code="EMPTY_SCHEMAS",
                    layer="global",
                    message="The input schemas object is empty or null.",
                    repairable=False,
                    path="schemas"
                )
            )
            return self._finalize_output(start_time)

        # 1. UI Validation
        if schemas.ui_schema:
            self._validate_ui(schemas)
        else:
            self.errors.append(ValidationError(code="MISSING_LAYER", layer="ui_schema", message="UI Schema is missing", repairable=False, path="ui_schema"))
            self.report.ui_valid = False

        # 2. API Validation
        if schemas.api_schema:
            self._validate_api(schemas)
        else:
            self.errors.append(ValidationError(code="MISSING_LAYER", layer="api_schema", message="API Schema is missing", repairable=False, path="api_schema"))
            self.report.api_valid = False

        # 3. DB Validation
        if schemas.db_schema:
            self._validate_db(schemas)
        else:
            self.errors.append(ValidationError(code="MISSING_LAYER", layer="db_schema", message="DB Schema is missing", repairable=False, path="db_schema"))
            self.report.db_valid = False

        # 4. Auth Validation
        if schemas.auth_schema:
            self._validate_auth(schemas)
        else:
            self.errors.append(ValidationError(code="MISSING_LAYER", layer="auth_schema", message="Auth Schema is missing", repairable=False, path="auth_schema"))
            self.report.auth_valid = False

        # 5. Cross-layer Validation
        if schemas.ui_schema and schemas.api_schema and schemas.db_schema and schemas.auth_schema:
            self._validate_cross_layer(schemas)
        else:
            self.report.cross_layer_valid = False

        # 6. Completeness Quality Guard
        if intent:
            self._validate_completeness(schemas, intent)

        return self._finalize_output(start_time)

    def _validate_completeness(self, schemas: SchemaGenerationOutput, intent):
        """Check if generated output is too shallow for complex intents."""
        if intent.features and schemas.ui_schema and schemas.ui_schema.pages:
            num_features = len(intent.features)
            num_pages = len(schemas.ui_schema.pages)
            if num_features > 5 and num_pages <= 2:
                self.warnings.append(ValidationWarning(
                    code="LOW_PAGE_COVERAGE",
                    layer="global",
                    message=f"Intent extracted {num_features} features, but only {num_pages} pages were generated.",
                    repairable=False,
                    path="ui_schema.pages"
                ))

        if intent.roles and schemas.auth_schema and schemas.auth_schema.roles:
            num_intent_roles = len(intent.roles)
            num_auth_roles = len(schemas.auth_schema.roles)
            if num_intent_roles > 3 and num_auth_roles <= 2:
                self.warnings.append(ValidationWarning(
                    code="LOW_ROLE_COVERAGE",
                    layer="global",
                    message=f"Intent extracted {num_intent_roles} roles, but only {num_auth_roles} auth roles were generated.",
                    repairable=False,
                    path="auth_schema.roles"
                ))

    def _finalize_output(self, start_time: float) -> tuple[ValidationOutput, float]:
        """Wrap up the validation metrics."""
        val_time_ms = (time.perf_counter() - start_time) * 1000
        
        is_valid = len(self.errors) == 0
        
        logger.info(
            f"Validation complete | "
            f"Valid: {is_valid} | "
            f"Errors: {len(self.errors)} | "
            f"Warnings: {len(self.warnings)} | "
            f"Time: {val_time_ms:.2f}ms"
        )
        
        output = ValidationOutput(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            validation_report=self.report
        )
        
        return output, val_time_ms

    def _validate_ui(self, schemas: SchemaGenerationOutput):
        """Validate UI Schema."""
        ui = schemas.ui_schema
        has_error = False

        for i, page in enumerate(ui.pages):
            base_path = f"ui_schema.pages[{i}]"
            
            if not page.name:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="ui_schema", message="Page is missing name", repairable=True, path=f"{base_path}.name"))
                has_error = True
            
            if not page.route:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="ui_schema", message=f"Page {page.name or i} is missing route", repairable=True, path=f"{base_path}.route"))
                has_error = True
                
            if not page.layout:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="ui_schema", message=f"Page {page.name or i} is missing layout", repairable=True, path=f"{base_path}.layout"))
                has_error = True

            if not page.components:
                self.warnings.append(ValidationWarning(code="EMPTY_COMPONENTS", layer="ui_schema", message=f"Page {page.name or i} has no components", repairable=True, path=f"{base_path}.components"))

        self.report.ui_valid = not has_error

    def _validate_api(self, schemas: SchemaGenerationOutput):
        """Validate API Schema."""
        api = schemas.api_schema
        has_error = False
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}

        for i, ep in enumerate(api.endpoints):
            base_path = f"api_schema.endpoints[{i}]"

            if not ep.path:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="api_schema", message="Endpoint is missing path", repairable=True, path=f"{base_path}.path"))
                has_error = True
            
            if not ep.method:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="api_schema", message=f"Endpoint {ep.path or i} is missing method", repairable=True, path=f"{base_path}.method"))
                has_error = True
            elif ep.method.upper() not in valid_methods:
                self.errors.append(ValidationError(code="INVALID_METHOD", layer="api_schema", message=f"Endpoint {ep.path} has invalid method {ep.method}", repairable=True, path=f"{base_path}.method"))
                has_error = True
                
            if not ep.description:
                self.warnings.append(ValidationWarning(code="MISSING_DESCRIPTION", layer="api_schema", message=f"Endpoint {ep.method} {ep.path} is missing description", repairable=True, path=f"{base_path}.description"))

            if ep.auth_required and not ep.allowed_roles:
                self.warnings.append(ValidationWarning(code="AUTH_NO_ROLES", layer="api_schema", message=f"Endpoint {ep.method} {ep.path} requires auth but defines no allowed roles", repairable=True, path=f"{base_path}.allowed_roles"))

        self.report.api_valid = not has_error

    def _validate_db(self, schemas: SchemaGenerationOutput):
        """Validate Database Schema."""
        db = schemas.db_schema
        has_error = False

        for i, table in enumerate(db.tables):
            base_path = f"db_schema.tables[{i}]"

            if not table.name:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="db_schema", message="Table is missing name", repairable=True, path=f"{base_path}.name"))
                has_error = True
                
            if not table.columns:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="db_schema", message=f"Table {table.name or i} has no columns", repairable=True, path=f"{base_path}.columns"))
                has_error = True
            else:
                has_id = False
                for j, col in enumerate(table.columns):
                    col_path = f"{base_path}.columns[{j}]"
                    if not col.name:
                        self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="db_schema", message=f"Column in table {table.name} is missing name", repairable=True, path=f"{col_path}.name"))
                        has_error = True
                    if not col.type:
                        self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="db_schema", message=f"Column {col.name} in table {table.name} is missing type", repairable=True, path=f"{col_path}.type"))
                        has_error = True
                    if col.name == "id":
                        has_id = True

                if not has_id:
                    self.errors.append(ValidationError(code="MISSING_PRIMARY_KEY", layer="db_schema", message=f"Table {table.name} is missing 'id' column", repairable=True, path=f"{base_path}.columns"))
                    has_error = True

        self.report.db_valid = not has_error

    def _validate_auth(self, schemas: SchemaGenerationOutput):
        """Validate Auth Schema."""
        auth = schemas.auth_schema
        has_error = False

        for i, role in enumerate(auth.roles):
            base_path = f"auth_schema.roles[{i}]"
            if not role.name:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="auth_schema", message="Role is missing name", repairable=True, path=f"{base_path}.name"))
                has_error = True
            
            if not role.permissions:
                self.warnings.append(ValidationWarning(code="EMPTY_PERMISSIONS", layer="auth_schema", message=f"Role {role.name} has no permissions", repairable=True, path=f"{base_path}.permissions"))

        for i, route in enumerate(auth.protected_routes):
            base_path = f"auth_schema.protected_routes[{i}]"
            if not route.route:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="auth_schema", message="Protected route is missing route path", repairable=True, path=f"{base_path}.route"))
                has_error = True
            
            if not route.allowed_roles:
                self.errors.append(ValidationError(code="MISSING_REQUIRED_FIELD", layer="auth_schema", message=f"Protected route {route.route} has no allowed roles", repairable=True, path=f"{base_path}.allowed_roles"))
                has_error = True

        self.report.auth_valid = not has_error

    def _validate_cross_layer(self, schemas: SchemaGenerationOutput):
        """Cross-validate dependencies between UI, API, DB, and Auth."""
        has_error = False
        
        # Build lookup sets
        api_endpoints = {ep.path for ep in schemas.api_schema.endpoints if ep.path}
        auth_roles = {r.name for r in schemas.auth_schema.roles if r.name}
        ui_routes = {p.route for p in schemas.ui_schema.pages if p.route}
        db_tables = {t.name for t in schemas.db_schema.tables if t.name}

        # UI required API endpoints -> must exist in API schema
        for i, page in enumerate(schemas.ui_schema.pages):
            for j, req_ep in enumerate(page.required_api_endpoints):
                # Simple exact match or base path match for paths with variables
                match_found = any(ep == req_ep or (req_ep in ep) or (ep in req_ep) for ep in api_endpoints)
                if not match_found and req_ep not in api_endpoints:
                    # Ignore wildcard-like endpoints as they might be dynamically mapped, but issue error if completely distinct
                    self.errors.append(ValidationError(
                        code="ORPHANED_UI_ENDPOINT", 
                        layer="cross_layer", 
                        message=f"UI page '{page.name}' requires API endpoint '{req_ep}' which does not exist in API Schema", 
                        repairable=True, 
                        path=f"ui_schema.pages[{i}].required_api_endpoints[{j}]"
                    ))
                    has_error = True

        # API allowed roles -> must exist in Auth schema
        for i, ep in enumerate(schemas.api_schema.endpoints):
            for j, role in enumerate(ep.allowed_roles):
                if role not in auth_roles:
                    self.errors.append(ValidationError(
                        code="INVALID_API_ROLE", 
                        layer="cross_layer", 
                        message=f"API endpoint '{ep.path}' allows role '{role}' which is not defined in Auth Schema", 
                        repairable=True, 
                        path=f"api_schema.endpoints[{i}].allowed_roles[{j}]"
                    ))
                    has_error = True
                    
            # Check if response fields loosely map to DB tables (warning if uncertain)
            # E.g. if an endpoint returns `contacts`, there should be a `contacts` table
            for resp_key in ep.response_body.keys():
                if resp_key not in ["success", "token", "error", "message"]:
                    # Is there a table that somewhat matches the response key?
                    table_match = any(resp_key.lower() in t.lower() or t.lower() in resp_key.lower() for t in db_tables)
                    if not table_match:
                        self.warnings.append(ValidationWarning(
                            code="UNMAPPED_RESPONSE_FIELD",
                            layer="cross_layer",
                            message=f"Response field '{resp_key}' in API '{ep.path}' does not clearly map to database tables",
                            repairable=False,
                            path=f"api_schema.endpoints[{i}].response_body.{resp_key}"
                        ))

        # Auth protected routes -> should exist in UI schema or API schema
        for i, pr in enumerate(schemas.auth_schema.protected_routes):
            clean_route = pr.route.replace("/*", "")
            
            ui_match = any(clean_route in r for r in ui_routes)
            api_match = any(clean_route in a for a in api_endpoints)
            
            if not ui_match and not api_match:
                self.warnings.append(ValidationWarning(
                    code="ORPHANED_PROTECTED_ROUTE",
                    layer="cross_layer",
                    message=f"Protected route '{pr.route}' does not seem to match any UI page or API endpoint",
                    repairable=True,
                    path=f"auth_schema.protected_routes[{i}].route"
                ))
                
            for j, role in enumerate(pr.allowed_roles):
                if role not in auth_roles:
                    self.errors.append(ValidationError(
                        code="INVALID_AUTH_ROLE", 
                        layer="cross_layer", 
                        message=f"Protected route '{pr.route}' allows role '{role}' which is not defined in Auth Schema", 
                        repairable=True, 
                        path=f"auth_schema.protected_routes[{i}].allowed_roles[{j}]"
                    ))
                    has_error = True

        self.report.cross_layer_valid = not has_error
