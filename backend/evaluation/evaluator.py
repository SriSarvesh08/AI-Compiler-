"""
Evaluator Core for Day 7 Evaluation Framework.

Runs individual prompts through the full compilation pipeline
and collects detailed execution metrics.
"""

import os
import asyncio
import time
import logging
from typing import Dict, Any

from schemas.intent_schema import IntentInput
from schemas.architecture_schema import ApplicationArchitecture
from pipeline.intent_extractor import IntentExtractor
from pipeline.system_designer import SystemDesigner
from pipeline.schema_generator import SchemaGenerator
from pipeline.validator import Validator
from pipeline.repair_engine import RepairEngine
from pipeline.runtime_simulator import RuntimeSimulator

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """Executes the pipeline and extracts empirical metrics."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self.intent_extractor = IntentExtractor(api_key=api_key)
        self.system_designer = SystemDesigner(api_key=api_key)
        self.schema_generator = SchemaGenerator(api_key=api_key)
        self.validator = Validator()
        self.repair_engine = RepairEngine()
        self.runtime_simulator = RuntimeSimulator()

    async def evaluate_prompt(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full pipeline on a single prompt and collect metrics."""
        prompt = test_case["prompt"]
        test_id = test_case["id"]
        category = test_case["category"]
        
        logger.info(f"Evaluating {test_id} ({category}): {prompt[:50]}...")
        
        start_time = time.perf_counter()
        metrics = {
            "id": test_id,
            "category": category,
            "prompt": prompt,
            "success": False,
            "final_validation_passed": False,
            "runtime_ready": False,
            "repair_attempts": 0,
            "error_count_before_repair": 0,
            "error_count_after_repair": 0,
            "warning_count": 0,
            "latency_ms": 0.0,
            "failure_type": None,
            "assumptions_count": 0
        }

        try:
            # Stage 1: Intent Extraction
            intent, _ = await self.intent_extractor.extract(prompt)
            if not intent:
                metrics["failure_type"] = "INTENT_EXTRACTION_FAILED"
                raise Exception("Intent extraction returned None")

            # Stage 2: System Design
            architecture, _ = await self.system_designer.design(intent)
            if not architecture:
                metrics["failure_type"] = "DESIGN_GENERATION_FAILED"
                raise Exception("System design returned None")

            metrics["assumptions_count"] = len(architecture.assumptions) if architecture.assumptions else 0

            # Stage 3: Schema Generation
            schemas, _ = await self.schema_generator.generate(architecture)
            if not schemas:
                metrics["failure_type"] = "SCHEMA_GENERATION_FAILED"
                raise Exception("Schema generation returned None")

            # Stage 4: Validation
            validation, _ = self.validator.validate(schemas, intent)
            metrics["error_count_before_repair"] = len(validation.errors)
            metrics["warning_count"] = len(validation.warnings)
            
            final_schemas = schemas
            final_validation = validation

            # Stage 5: Repair
            if not validation.is_valid:
                repair_out = self.repair_engine.repair(schemas, validation)
                metrics["repair_attempts"] = repair_out.repair_attempts
                if repair_out.repaired and repair_out.repaired_schemas:
                    final_schemas = repair_out.repaired_schemas
                    # Final Validation
                    final_validation, _ = self.validator.validate(final_schemas, intent)
                    metrics["error_count_after_repair"] = len(final_validation.errors)
                else:
                    metrics["failure_type"] = "REPAIR_FAILED"

            metrics["final_validation_passed"] = final_validation.is_valid

            # Stage 6: Runtime Simulation
            if final_validation.is_valid:
                runtime, _ = self.runtime_simulator.simulate(final_schemas, final_validation)
                metrics["runtime_ready"] = runtime.runtime_ready
                if not runtime.runtime_ready:
                    metrics["failure_type"] = "RUNTIME_FAILED"
            else:
                metrics["failure_type"] = "VALIDATION_FAILED"

            # Check if it hit edge cases successfully
            if metrics["runtime_ready"]:
                metrics["success"] = True

        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}")
            if not metrics["failure_type"]:
                metrics["failure_type"] = "UNKNOWN_ERROR"

        metrics["latency_ms"] = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"Result {test_id}: Success={metrics['success']} | Type={metrics['failure_type']}")
        
        return metrics
