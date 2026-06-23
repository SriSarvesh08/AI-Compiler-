"""
Generate Routes — API endpoints for the compiler pipeline.

Day 1: /generate/intent endpoint (Intent Extraction).
Day 2: /generate/design endpoint (System Design) + /generate/full-pipeline.
"""

import logging
import os
import time

from fastapi import APIRouter, HTTPException, Depends
from routes.auth import get_current_user_optional
import json

from schemas.intent_schema import IntentInput, IntentOutput, IntentResponse
from schemas.architecture_schema import (
    DesignInput,
    DesignResponse,
    SchemaGenerationInput,
    SchemaGenerationResponse,
    FullPipelineInput,
    FullPipelineResponse,
)
from schemas.validation_schema import ValidationInput, ValidationResponse
from schemas.repair_schema import RepairInput, RepairResponse
from schemas.runtime_schema import RuntimeInput, RuntimeResponse
from schemas.modify_schema import ModifyInput, ModifyResponse
from pipeline.intent_extractor import IntentExtractor
from pipeline.system_designer import SystemDesigner
from pipeline.schema_generator import SchemaGenerator
from pipeline.validator import Validator
from pipeline.repair_engine import RepairEngine
from pipeline.runtime_simulator import RuntimeSimulator
from pipeline.patch_engine import PatchEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


def _get_extractor(model_pref: str = "gemini") -> IntentExtractor:
    """Get or create an IntentExtractor instance.

    Returns:
        Configured IntentExtractor.

    Raises:
        HTTPException: If the OpenAI API key is not configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and model_pref == "gemini":
        pass # Will fall back or handle in extractor
    return IntentExtractor(api_key=api_key or "", model=model_pref)


def _get_designer() -> SystemDesigner:
    """Get or create a SystemDesigner instance.

    Returns:
        Configured SystemDesigner (with LLM if API key available,
        otherwise rule-based only).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    return SystemDesigner(api_key=api_key)


def _get_schema_generator() -> SchemaGenerator:
    """Get or create a SchemaGenerator instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    return SchemaGenerator(api_key=api_key)


def _get_validator() -> Validator:
    """Get or create a Validator instance."""
    return Validator()


def _get_repair_engine() -> RepairEngine:
    """Get or create a RepairEngine instance."""
    return RepairEngine()


def _get_runtime_simulator() -> RuntimeSimulator:
    """Get or create a RuntimeSimulator instance."""
    return RuntimeSimulator()


def _get_patch_engine() -> PatchEngine:
    """Get or create a PatchEngine instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    return PatchEngine(api_key=api_key)


# ──────────────────────────────────────────────
# Stage 1: Intent Extraction
# ──────────────────────────────────────────────

@router.post("/intent", response_model=IntentResponse)
async def extract_intent(input_data: IntentInput) -> IntentResponse:
    """Extract structured intent from a natural language prompt.

    Takes a user's application description and returns structured data
    including the application domain, features, and user roles.

    Args:
        input_data: The user's prompt wrapped in an IntentInput model.

    Returns:
        IntentResponse with success status, extracted intent, and timing data.
    """
    logger.info(f"Received intent extraction request | Prompt: {input_data.prompt[:100]}...")

    try:
        extractor = _get_extractor()
        intent, extraction_time_ms = await extractor.extract(input_data.prompt)

        logger.info(
            f"Intent extraction completed successfully | "
            f"Domain: {intent.domain} | "
            f"Time: {extraction_time_ms:.2f}ms"
        )

        return IntentResponse(
            success=True,
            intent=intent,
            error=None,
            extraction_time_ms=round(extraction_time_ms, 2),
        )

    except ValueError as e:
        logger.error(f"Intent extraction validation error: {e}")
        return IntentResponse(
            success=False,
            intent=None,
            error=f"Failed to parse intent: {str(e)}",
            extraction_time_ms=0.0,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (e.g., missing API key)
        raise

    except Exception as e:
        logger.error(f"Intent extraction unexpected error: {e}", exc_info=True)
        return IntentResponse(
            success=False,
            intent=None,
            error=f"Internal error during intent extraction: {str(e)}",
            extraction_time_ms=0.0,
        )


# ──────────────────────────────────────────────
# Stage 2: System Design
# ──────────────────────────────────────────────

@router.post("/design", response_model=DesignResponse)
async def generate_design(input_data: DesignInput) -> DesignResponse:
    """Generate application architecture from structured intent.

    Takes the extracted intent (domain, features, roles) and produces
    a complete application architecture with entities, pages, flows,
    role permissions, and design assumptions.

    Args:
        input_data: The extracted intent wrapped in a DesignInput model.

    Returns:
        DesignResponse with success status and generated architecture.
    """
    logger.info(
        f"Received design generation request | "
        f"Domain: {input_data.intent.domain} | "
        f"Features: {len(input_data.intent.features)}"
    )

    try:
        designer = _get_designer()
        architecture, design_time_ms = await designer.design(input_data.intent)

        logger.info(
            f"Design generation completed successfully | "
            f"App: {architecture.app_name} | "
            f"Time: {design_time_ms:.2f}ms"
        )

        return DesignResponse(
            success=True,
            architecture=architecture,
            error=None,
            design_time_ms=round(design_time_ms, 2),
        )

    except ValueError as e:
        logger.error(f"Design generation validation error: {e}")
        return DesignResponse(
            success=False,
            architecture=None,
            error=f"Failed to generate design: {str(e)}",
            design_time_ms=0.0,
        )

    except Exception as e:
        logger.error(f"Design generation unexpected error: {e}", exc_info=True)
        return DesignResponse(
            success=False,
            architecture=None,
            error=f"Internal error during design generation: {str(e)}",
            design_time_ms=0.0,
        )


# ──────────────────────────────────────────────
# Stage 3: Schema Generation
# ──────────────────────────────────────────────

@router.post("/schema", response_model=SchemaGenerationResponse)
async def generate_schema(input_data: SchemaGenerationInput) -> SchemaGenerationResponse:
    """Generate detailed schemas from application architecture.

    Args:
        input_data: The architecture wrapped in a SchemaGenerationInput model.

    Returns:
        SchemaGenerationResponse with success status and generated schemas.
    """
    logger.info(
        f"Received schema generation request | "
        f"App: {input_data.architecture.app_name}"
    )

    try:
        generator = _get_schema_generator()
        schemas, gen_time_ms = await generator.generate(input_data.architecture)

        logger.info(
            f"Schema generation completed successfully | "
            f"Time: {gen_time_ms:.2f}ms"
        )

        return SchemaGenerationResponse(
            success=True,
            schemas=schemas,
            error=None,
            generation_time_ms=round(gen_time_ms, 2),
        )

    except Exception as e:
        logger.error(f"Schema generation unexpected error: {e}", exc_info=True)
        return SchemaGenerationResponse(
            success=False,
            schemas=None,
            error=f"Internal error during schema generation: {str(e)}",
            generation_time_ms=0.0,
        )


# ──────────────────────────────────────────────
# Stage 4: Validation Engine
# ──────────────────────────────────────────────

@router.post("/validate", response_model=ValidationResponse)
async def validate_schemas(input_data: ValidationInput) -> ValidationResponse:
    """Validate generated schemas.

    Args:
        input_data: Generated schemas wrapped in a ValidationInput model.

    Returns:
        ValidationResponse with success status and validation results.
    """
    logger.info("Received validation request")

    try:
        validator = _get_validator()
        validation_output, val_time_ms = validator.validate(input_data.schemas)

        logger.info(
            f"Validation completed successfully | "
            f"Valid: {validation_output.is_valid} | "
            f"Time: {val_time_ms:.2f}ms"
        )

        return ValidationResponse(
            success=True,
            validation=validation_output,
            error=None,
            validation_time_ms=round(val_time_ms, 2),
        )

    except Exception as e:
        logger.error(f"Validation unexpected error: {e}", exc_info=True)
        return ValidationResponse(
            success=False,
            validation=None,
            error=f"Internal error during validation: {str(e)}",
            validation_time_ms=0.0,
        )


# ──────────────────────────────────────────────
# Stage 5: Repair Engine
# ──────────────────────────────────────────────

@router.post("/repair", response_model=RepairResponse)
async def repair_schemas(input_data: RepairInput) -> RepairResponse:
    """Repair generated schemas using deterministic logic.

    Args:
        input_data: Schemas and validation report wrapped in a RepairInput model.

    Returns:
        RepairResponse with success status, repaired schemas, and before/after validation states.
    """
    logger.info("Received repair request")

    try:
        engine = _get_repair_engine()
        repair_output = engine.repair(input_data.schemas, input_data.validation)
        
        after_validation = None
        if repair_output.repaired and repair_output.repaired_schemas:
            # Re-validate
            validator = _get_validator()
            after_validation, _ = validator.validate(repair_output.repaired_schemas)

        logger.info(
            f"Repair completed successfully | "
            f"Repaired: {repair_output.repaired} | "
            f"Attempts: {repair_output.repair_attempts}"
        )

        return RepairResponse(
            success=True,
            before_validation=input_data.validation,
            repair=repair_output,
            after_validation=after_validation,
            error=None,
        )

    except Exception as e:
        logger.error(f"Repair unexpected error: {e}", exc_info=True)
        return RepairResponse(
            success=False,
            before_validation=input_data.validation,
            repair=None,
            after_validation=None,
            error=f"Internal error during repair: {str(e)}",
        )


# ──────────────────────────────────────────────
# Stage 6: Runtime Simulator
# ──────────────────────────────────────────────

@router.post("/runtime", response_model=RuntimeResponse)
async def simulate_runtime(input_data: RuntimeInput) -> RuntimeResponse:
    """Simulate the generated schemas.

    Args:
        input_data: Schemas and final validation report wrapped in a RuntimeInput model.

    Returns:
        RuntimeResponse with simulation status and preview app structure.
    """
    logger.info("Received runtime simulation request")

    try:
        simulator = _get_runtime_simulator()
        runtime_output, sim_time_ms = simulator.simulate(input_data.schemas, input_data.final_validation)

        logger.info(
            f"Runtime simulation completed successfully | "
            f"Ready: {runtime_output.runtime_ready} | "
            f"Time: {sim_time_ms:.2f}ms"
        )

        return RuntimeResponse(
            success=True,
            runtime=runtime_output,
            error=None,
        )

    except Exception as e:
        logger.error(f"Runtime simulation unexpected error: {e}", exc_info=True)
        return RuntimeResponse(
            success=False,
            runtime=None,
            error=f"Internal error during runtime simulation: {str(e)}",
        )


# ──────────────────────────────────────────────
# Full Pipeline: Prompt → Intent → Design → Schemas → Validation → Repair → Runtime
# ──────────────────────────────────────────────

@router.post("/full-pipeline", response_model=FullPipelineResponse)
async def run_full_pipeline(input_data: FullPipelineInput, current_user: dict = Depends(get_current_user_optional)) -> FullPipelineResponse:
    """Run the full compiler pipeline.

    Executes each stage sequentially:
    1. Intent Extraction
    2. System Design
    3. Schema Generation
    4. Validation
    5. Repair (if needed)
    6. Final Validation (if repaired)
    7. Runtime Simulation


    Args:
        input_data: The user's prompt wrapped in a FullPipelineInput model.

    Returns:
        FullPipelineResponse with outputs from each completed stage.
    """
    logger.info(f"Starting full pipeline | Prompt: {input_data.prompt[:100]}...")
    pipeline_start = time.perf_counter()

    stages: dict = {}

    # Extract model preference
    model_pref = "gemini"
    if current_user and "settings_json" in current_user:
        try:
            settings = json.loads(current_user["settings_json"])
            model_pref = settings.get("model", "gemini")
        except:
            pass
    
    try:
        logger.info("Pipeline Stage 1: Intent Extraction — Starting")
        extractor = _get_extractor(model_pref)
        intent, extraction_time_ms = await extractor.extract(input_data.prompt)

        stages["intent"] = intent.model_dump()
        logger.info(
            f"Pipeline Stage 1: Intent Extraction — Complete | "
            f"Domain: {intent.domain} | "
            f"Time: {extraction_time_ms:.2f}ms"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Pipeline failed at Stage 1 (Intent Extraction): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages if stages else None,
            error=f"Pipeline failed at Intent Extraction: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Stage 2: System Design ──
    try:
        logger.info("Pipeline Stage 2: System Design — Starting")
        designer = _get_designer()
        architecture, design_time_ms = await designer.design(intent)

        stages["architecture"] = architecture.model_dump()
        logger.info(
            f"Pipeline Stage 2: System Design — Complete | "
            f"App: {architecture.app_name} | "
            f"Time: {design_time_ms:.2f}ms"
        )

    except Exception as e:
        logger.error(f"Pipeline failed at Stage 2 (System Design): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages,
            error=f"Pipeline failed at System Design: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Stage 3: Schema Generation ──
    try:
        logger.info("Pipeline Stage 3: Schema Generation — Starting")
        generator = _get_schema_generator()
        schemas, gen_time_ms = await generator.generate(architecture)

        stages["schemas"] = schemas.model_dump()
        logger.info(
            f"Pipeline Stage 3: Schema Generation — Complete | "
            f"Time: {gen_time_ms:.2f}ms"
        )

    except Exception as e:
        logger.error(f"Pipeline failed at Stage 3 (Schema Generation): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages,
            error=f"Pipeline failed at Schema Generation: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Stage 4: Validation ──
    try:
        logger.info("Pipeline Stage 4: Validation — Starting")
        validator = _get_validator()
        validation_output, val_time_ms = validator.validate(schemas, intent)

        stages["validation"] = validation_output.model_dump()
        logger.info(
            f"Pipeline Stage 4: Validation — Complete | "
            f"Valid: {validation_output.is_valid} | "
            f"Time: {val_time_ms:.2f}ms"
        )

    except Exception as e:
        logger.error(f"Pipeline failed at Stage 4 (Validation): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages,
            error=f"Pipeline failed at Validation: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Stage 5: Repair Engine (Conditional) ──
    try:
        if not validation_output.is_valid:
            logger.info("Pipeline Stage 5: Repair Engine — Starting")
            engine = _get_repair_engine()
            
            # Allow up to 3 repair passes for complex multi-layer fixes
            # The UI spec only requires 1 pass, but safety limit to 3.
            max_attempts = 3
            current_schemas = schemas
            current_validation = validation_output
            
            total_summaries = []
            passes = 0
            
            for attempt in range(max_attempts):
                passes += 1
                repair_output = engine.repair(current_schemas, current_validation)
                
                if not repair_output.repaired:
                    break
                    
                total_summaries.extend(repair_output.repair_summary)
                current_schemas = repair_output.repaired_schemas
                
                # Re-validate
                current_validation, _ = validator.validate(current_schemas, intent)
                if current_validation.is_valid:
                    break

            # Build aggregated repair output
            agg_repair = {
                "repaired": len(total_summaries) > 0,
                "repair_attempts": passes,
                "repair_summary": [s.model_dump() for s in total_summaries],
                "message": f"Applied {len(total_summaries)} total repairs over {passes} passes.",
                "repaired_schemas": current_schemas.model_dump() if current_schemas else None
            }
            
            stages["repair"] = agg_repair
            stages["final_validation"] = current_validation.model_dump()
            
            logger.info(
                f"Pipeline Stage 5: Repair Engine — Complete | "
                f"Repaired: {agg_repair['repaired']} | "
                f"Final Valid: {current_validation.is_valid}"
            )
        else:
            logger.info("Pipeline Stage 5: Repair Engine — Skipped (Validation passed)")
            stages["repair"] = {
                "repaired": False,
                "repair_attempts": 0,
                "repair_summary": [],
                "message": "No repair needed",
                "repaired_schemas": None
            }
            stages["final_validation"] = validation_output.model_dump()
            
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 5 (Repair Engine): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages,
            error=f"Pipeline failed at Repair Engine: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Stage 6: Runtime Simulator ──
    try:
        logger.info("Pipeline Stage 6: Runtime Simulator — Starting")
        simulator = _get_runtime_simulator()
        # Ensure we pass the active schemas (which might be the repaired ones)
        active_schemas = current_schemas if stages["repair"]["repaired"] else schemas
        active_validation = current_validation if stages["repair"]["repaired"] else validation_output
        
        runtime_output, sim_time_ms = simulator.simulate(active_schemas, active_validation)
        
        stages["runtime"] = runtime_output.model_dump()
        logger.info(
            f"Pipeline Stage 6: Runtime Simulator — Complete | "
            f"Ready: {runtime_output.runtime_ready} | "
            f"Time: {sim_time_ms:.2f}ms"
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 6 (Runtime Simulator): {e}")
        total_time = (time.perf_counter() - pipeline_start) * 1000
        return FullPipelineResponse(
            success=False,
            stages=stages,
            error=f"Pipeline failed at Runtime Simulator: {str(e)}",
            total_time_ms=round(total_time, 2),
        )

    # ── Pipeline Complete ──
    total_time = (time.perf_counter() - pipeline_start) * 1000
    logger.info(
        f"Full pipeline completed successfully | "
        f"Total time: {total_time:.2f}ms | "
        f"Stages completed: {len(stages)}"
    )

    return FullPipelineResponse(
        success=True,
        stages=stages,
        error=None,
        total_time_ms=round(total_time, 2),
    )


# ──────────────────────────────────────────────
# Modify Existing App (Patch Engine)
# ──────────────────────────────────────────────

@router.post("/modify", response_model=ModifyResponse)
async def modify_pipeline(input_data: ModifyInput) -> ModifyResponse:
    """Modify an existing pipeline generation with a new change request.
    
    Args:
        input_data: ModifyInput containing existing stages and the change request.
        
    Returns:
        ModifyResponse containing the patched pipeline stages and summary.
    """
    logger.info(f"Starting pipeline modification | Request: {input_data.change_request[:100]}...")
    
    try:
        engine = _get_patch_engine()
        response = await engine.apply_patch(input_data)
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Pipeline modification failed: {e}", exc_info=True)
        return ModifyResponse(
            success=False,
            change_type="error",
            error=f"Pipeline modification failed: {str(e)}",
            updated_stages=input_data.existing_stages,
        )
