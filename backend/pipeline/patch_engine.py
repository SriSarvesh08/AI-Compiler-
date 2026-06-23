"""
Patch Engine — Applies modification requests to existing architecture.

Uses the pipeline components to selectively re-run only the affected layers
based on the change type.
"""

import logging
import time

from schemas.intent_schema import IntentOutput
from schemas.architecture_schema import ApplicationArchitecture, SchemaGenerationOutput
from schemas.validation_schema import ValidationOutput
from schemas.repair_schema import RepairOutput
from schemas.runtime_schema import RuntimeOutput
from schemas.modify_schema import ModifyInput, ModifyResponse

from pipeline.change_request_analyzer import ChangeRequestAnalyzer, ChangeType
from pipeline.intent_extractor import IntentExtractor
from pipeline.system_designer import SystemDesigner
from pipeline.schema_generator import SchemaGenerator
from pipeline.validator import Validator
from pipeline.repair_engine import RepairEngine
from pipeline.runtime_simulator import RuntimeSimulator

logger = logging.getLogger(__name__)


class PatchEngine:
    """Modifies an existing application configuration."""

    def __init__(self, api_key: str | None = None):
        self.analyzer = ChangeRequestAnalyzer()
        self.intent_extractor = IntentExtractor(api_key=api_key) if api_key else None
        self.designer = SystemDesigner(api_key=api_key)
        self.generator = SchemaGenerator(api_key=api_key)
        self.validator = Validator()
        self.repair_engine = RepairEngine()
        self.simulator = RuntimeSimulator()

    async def apply_patch(self, modify_input: ModifyInput) -> ModifyResponse:
        """Apply a change request to an existing pipeline output."""
        start_time = time.perf_counter()
        
        # 1. Analyze change
        analysis = self.analyzer.analyze(modify_input.change_request)
        
        if analysis["clarification_needed"]:
            return ModifyResponse(
                success=False,
                change_type=analysis["change_type"],
                clarification_needed=True,
                clarification_questions=analysis["clarification_questions"],
                updated_stages=modify_input.existing_stages,
                patch_summary=[],
                total_time_ms=0,
            )

        affected_layers = analysis["affected_layers"]
        logger.info(f"Applying patch. Affected layers: {affected_layers}")
        
        # We will mutate the existing stages
        stages = modify_input.existing_stages.copy()
        patch_summary = []
        
        # Get existing objects
        intent_dict = stages.get("intent", {})
        arch_dict = stages.get("architecture", {})
        schema_dict = stages.get("schemas", {})
        
        current_intent = IntentOutput(**intent_dict) if intent_dict else None
        current_arch = ApplicationArchitecture(**arch_dict) if arch_dict else None
        current_schemas = SchemaGenerationOutput(**schema_dict) if schema_dict else None
        
        if not current_intent or not current_arch or not current_schemas:
            return ModifyResponse(
                success=False,
                change_type=analysis["change_type"],
                error="Cannot patch: Missing required existing pipeline stages (intent, architecture, or schemas).",
                updated_stages=stages,
                total_time_ms=0,
            )

        # 2. Patch Intent (if needed)
        if "intent" in affected_layers:
            logger.info("Patching Intent")
            if self.intent_extractor:
                # To patch intent, we append the change request to the original prompt
                # if we had it, or we just ask to modify the intent object directly.
                # Since intent_extractor takes a full prompt, we construct a compound prompt
                compound_prompt = f"Original app: {current_intent.domain} with features: {current_intent.features} and roles: {current_intent.roles}. Modification: {modify_input.change_request}"
                new_intent, _ = await self.intent_extractor.extract(compound_prompt)
                
                # Compare
                added_features = set(new_intent.features) - set(current_intent.features)
                added_roles = set(new_intent.roles) - set(current_intent.roles)
                
                if added_features:
                    patch_summary.append(f"Added intent features: {', '.join(added_features)}")
                if added_roles:
                    patch_summary.append(f"Added intent roles: {', '.join(added_roles)}")
                    
                current_intent = new_intent
                stages["intent"] = current_intent.model_dump()
        
        # 3. Patch Architecture (if needed)
        if "architecture" in affected_layers:
            logger.info("Patching Architecture")
            new_arch, _ = await self.designer.design(current_intent)
            
            # Compare
            old_pages = {p.name for p in current_arch.pages}
            new_pages = {p.name for p in new_arch.pages}
            added_pages = new_pages - old_pages
            if added_pages:
                patch_summary.append(f"Added pages: {', '.join(added_pages)}")
                
            old_entities = {e.name for e in current_arch.entities}
            new_entities = {e.name for e in new_arch.entities}
            added_entities = new_entities - old_entities
            if added_entities:
                patch_summary.append(f"Added entities: {', '.join(added_entities)}")
                
            current_arch = new_arch
            stages["architecture"] = current_arch.model_dump()

        # 4. Patch Schemas (if needed)
        # Note: In a true patch engine, we would only re-generate the specific schema.
        # But our schema_generator takes the whole architecture and outputs all schemas.
        # So we just re-run schema generation if any schema is affected.
        schema_layers = ["ui_schema", "api_schema", "db_schema", "auth_schema"]
        if any(l in affected_layers for l in schema_layers):
            logger.info("Patching Schemas")
            new_schemas, _ = await self.generator.generate(current_arch)
            
            if "api_schema" in affected_layers and new_schemas.api_schema:
                old_apis = {f"{e.method} {e.path}" for e in (current_schemas.api_schema.endpoints if current_schemas.api_schema else [])}
                new_apis = {f"{e.method} {e.path}" for e in new_schemas.api_schema.endpoints}
                added_apis = new_apis - old_apis
                if added_apis:
                    patch_summary.append(f"Added APIs: {len(added_apis)} endpoints")
                    
            if "db_schema" in affected_layers and new_schemas.db_schema:
                old_tables = {t.name for t in (current_schemas.db_schema.tables if current_schemas.db_schema else [])}
                new_tables = {t.name for t in new_schemas.db_schema.tables}
                added_tables = new_tables - old_tables
                if added_tables:
                    patch_summary.append(f"Added DB tables: {', '.join(added_tables)}")

            current_schemas = new_schemas
            stages["schemas"] = current_schemas.model_dump()

        # 5. Validation
        logger.info("Validating Patched Schemas")
        validation_output, _ = self.validator.validate(current_schemas, current_intent)
        stages["validation"] = validation_output.model_dump()

        # 6. Repair (if needed)
        if not validation_output.is_valid:
            logger.info("Repairing Patched Schemas")
            repair_output = self.repair_engine.repair(current_schemas, validation_output)
            if repair_output.repaired and repair_output.repaired_schemas:
                current_schemas = repair_output.repaired_schemas
                validation_output, _ = self.validator.validate(current_schemas, current_intent)
                patch_summary.append(f"Auto-repaired {len(repair_output.repair_summary)} schema issues")
            
            stages["repair"] = {
                "repaired": repair_output.repaired,
                "repair_attempts": repair_output.repair_attempts,
                "repair_summary": [s.model_dump() for s in repair_output.repair_summary],
                "message": repair_output.message,
            }
        else:
            stages["repair"] = {
                "repaired": False,
                "repair_attempts": 0,
                "repair_summary": [],
                "message": "No repair needed",
            }
            
        stages["final_validation"] = validation_output.model_dump()

        # 7. Runtime Simulation
        logger.info("Simulating Patched Runtime")
        runtime_output, _ = self.simulator.simulate(current_schemas, validation_output)
        stages["runtime"] = runtime_output.model_dump()
        
        if not patch_summary:
            patch_summary.append("Modified existing layers successfully.")

        total_time = (time.perf_counter() - start_time) * 1000

        return ModifyResponse(
            success=True,
            change_type=analysis["change_type"],
            patch_summary=patch_summary,
            updated_stages=stages,
            total_time_ms=total_time
        )
