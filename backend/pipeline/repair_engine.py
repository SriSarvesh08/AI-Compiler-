"""
Repair Engine — Stage 5 of the Compiler Pipeline.

Takes validation errors and attempts to automatically repair:
- Missing fields or relationships
- Inconsistent naming conventions
- Cross-layer mismatches

This engine is deterministic and uses strict rule-based logic to fix errors.
It limits attempts to prevent infinite loops and delegates re-validation back to the caller.
"""

import logging
import copy
from typing import Any

from schemas.architecture_schema import SchemaGenerationOutput
from schemas.validation_schema import ValidationOutput, ValidationError
from schemas.repair_schema import RepairOutput, RepairSummary
from schemas.db_schema import Column
from schemas.auth_schema import ProtectedRoute
from schemas.api_schema import APIEndpoint

logger = logging.getLogger(__name__)


class RepairEngine:
    """Automatically repairs validation errors in generated specifications.
    
    Operates on a deep copy of the schemas to avoid partial mutation bugs.
    Uses rule-based logic matching specific error codes.
    """

    def __init__(self):
        """Initialize the RepairEngine."""
        logger.info("RepairEngine initialized in deterministic mode")

    def repair(self, schemas: SchemaGenerationOutput, validation: ValidationOutput) -> RepairOutput:
        """Repair schemas based on validation errors.

        Args:
            schemas: Generated schema specifications with errors.
            validation: Validation report detailing the errors.

        Returns:
            RepairOutput with repaired schemas and summary of actions taken.
        """
        logger.info("Starting repair process")
        
        if validation.is_valid or not validation.errors:
            logger.info("Validation was successful, no repairs needed.")
            return RepairOutput(
                repaired=False,
                repair_attempts=0,
                message="No repair needed",
                repaired_schemas=schemas
            )

        # Work on a deep copy
        repaired_schemas = copy.deepcopy(schemas)
        summaries: list[RepairSummary] = []
        
        # We only do 1 pass internally. The orchestrator can loop if desired,
        # but the logic here handles all currently repairable errors in a single sweep.
        attempts = 1
        
        # Sort errors so we handle simpler things first (optional, but good practice)
        repairable_errors = [e for e in validation.errors if e.repairable]
        
        logger.info(f"Found {len(repairable_errors)} repairable errors out of {len(validation.errors)} total.")
        
        for error in repairable_errors:
            summary = self._apply_repair(error, repaired_schemas)
            if summary:
                summaries.append(summary)

        return RepairOutput(
            repaired=len(summaries) > 0,
            repair_attempts=attempts,
            repair_summary=summaries,
            message=f"Applied {len(summaries)} repairs.",
            repaired_schemas=repaired_schemas
        )

    def _apply_repair(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        """Route the error to the correct repair handler based on layer and code."""
        layer = error.layer
        code = error.code
        
        try:
            if layer == "ui_schema":
                return self._repair_ui(error, schemas)
            elif layer == "api_schema":
                return self._repair_api(error, schemas)
            elif layer == "db_schema":
                return self._repair_db(error, schemas)
            elif layer == "auth_schema":
                return self._repair_auth(error, schemas)
            elif layer == "cross_layer":
                return self._repair_cross_layer(error, schemas)
        except Exception as e:
            logger.error(f"Failed to apply repair for {code} at {error.path}: {e}")
            return None
            
        return None

    def _repair_ui(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        if error.code == "MISSING_REQUIRED_FIELD" and ".route" in error.path:
            # Extract page index
            idx = int(error.path.split("[")[1].split("]")[0])
            page = schemas.ui_schema.pages[idx]
            if page.name:
                before = page.route
                after = f"/{page.name.lower().replace(' ', '-')}"
                page.route = after
                return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Added missing route using page name", before=before, after=after)
            
        if error.code == "MISSING_REQUIRED_FIELD" and ".layout" in error.path:
            idx = int(error.path.split("[")[1].split("]")[0])
            page = schemas.ui_schema.pages[idx]
            before = page.layout
            after = "dashboard"
            page.layout = after
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Added default layout", before=before, after=after)

        return None

    def _repair_api(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        if error.code == "INVALID_METHOD":
            idx = int(error.path.split("[")[1].split("]")[0])
            ep = schemas.api_schema.endpoints[idx]
            before = ep.method
            after = "GET"
            ep.method = after
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Replaced invalid method with GET", before=before, after=after)
            
        if error.code == "MISSING_REQUIRED_FIELD" and ".method" in error.path:
            idx = int(error.path.split("[")[1].split("]")[0])
            ep = schemas.api_schema.endpoints[idx]
            before = ep.method
            after = "GET"
            ep.method = after
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Added default method GET", before=before, after=after)

        if error.code == "MISSING_REQUIRED_FIELD" and ".path" in error.path:
            idx = int(error.path.split("[")[1].split("]")[0])
            ep = schemas.api_schema.endpoints[idx]
            before = ep.path
            after = "/api/unknown"
            ep.path = after
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Added fallback path", before=before, after=after)

        return None

    def _repair_db(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        if error.code == "MISSING_PRIMARY_KEY":
            idx = int(error.path.split("[")[1].split("]")[0])
            table = schemas.db_schema.tables[idx]
            
            new_col = Column(name="id", type="uuid", required=True)
            table.columns.insert(0, new_col)
            
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action=f"Added missing id column to table {table.name}", before=None, after="id: uuid")

        if error.code == "MISSING_REQUIRED_FIELD" and ".type" in error.path:
            # db_schema.tables[X].columns[Y].type
            parts = error.path.split("[")
            t_idx = int(parts[1].split("]")[0])
            c_idx = int(parts[2].split("]")[0])
            
            col = schemas.db_schema.tables[t_idx].columns[c_idx]
            before = col.type
            
            # Infer type
            name = col.name.lower()
            if "email" in name:
                after = "string"
            elif "name" in name:
                after = "string"
            elif "created_at" in name or "updated_at" in name or "date" in name:
                after = "datetime"
            elif "amount" in name or "price" in name or "count" in name:
                after = "number"
            elif "is_" in name or "has_" in name or "status" in name:
                after = "boolean"
            else:
                after = "string"
                
            col.type = after
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action=f"Inferred missing type for column {col.name}", before=before, after=after)

        return None

    def _repair_auth(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        if error.code == "MISSING_REQUIRED_FIELD" and ".allowed_roles" in error.path:
            idx = int(error.path.split("[")[1].split("]")[0])
            pr = schemas.auth_schema.protected_routes[idx]
            before = pr.allowed_roles
            
            # Grant to all defined roles as a safe fallback
            all_roles = [r.name for r in schemas.auth_schema.roles] if schemas.auth_schema.roles else ["admin"]
            pr.allowed_roles = all_roles
            
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Added default roles to protected route", before=before, after=all_roles)
        return None

    def _repair_cross_layer(self, error: ValidationError, schemas: SchemaGenerationOutput) -> RepairSummary | None:
        if error.code == "ORPHANED_UI_ENDPOINT":
            # ui_schema.pages[X].required_api_endpoints[Y]
            parts = error.path.split("[")
            p_idx = int(parts[1].split("]")[0])
            e_idx = int(parts[2].split("]")[0])
            
            req_ep = schemas.ui_schema.pages[p_idx].required_api_endpoints[e_idx]
            
            # Action: Create matching API endpoint
            new_ep = APIEndpoint(
                path=req_ep,
                method="GET",
                description=f"Auto-generated endpoint for UI requirement",
                auth_required=False,
                allowed_roles=[]
            )
            schemas.api_schema.endpoints.append(new_ep)
            
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action=f"Created missing API endpoint {req_ep}", before=None, after=req_ep)

        if error.code == "INVALID_API_ROLE":
            # api_schema.endpoints[X].allowed_roles[Y]
            parts = error.path.split("[")
            ep_idx = int(parts[1].split("]")[0])
            r_idx = int(parts[2].split("]")[0])
            
            ep = schemas.api_schema.endpoints[ep_idx]
            # Since index could shift if we pop, it's safer to just rebuild the list without the invalid role
            
            valid_roles = [r.name for r in schemas.auth_schema.roles]
            before = list(ep.allowed_roles)
            ep.allowed_roles = [r for r in ep.allowed_roles if r in valid_roles]
            
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Removed unknown role from API endpoint", before=before, after=ep.allowed_roles)

        if error.code == "INVALID_AUTH_ROLE":
            parts = error.path.split("[")
            pr_idx = int(parts[1].split("]")[0])
            
            pr = schemas.auth_schema.protected_routes[pr_idx]
            valid_roles = [r.name for r in schemas.auth_schema.roles]
            
            before = list(pr.allowed_roles)
            pr.allowed_roles = [r for r in pr.allowed_roles if r in valid_roles]
            
            return RepairSummary(error_code=error.code, layer=error.layer, path=error.path, action="Removed unknown role from protected route", before=before, after=pr.allowed_roles)

        return None
