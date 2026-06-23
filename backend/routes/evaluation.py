"""
Evaluation Routes for Day 7.

Exposes endpoints to retrieve evaluation dataset, trigger runs,
and fetch latest evaluation metrics.
"""

import os
import json
import logging
from fastapi import APIRouter, HTTPException

from evaluation.evaluator import EvaluationEngine
from evaluation.metrics import calculate_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "evaluation", "dataset.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "evaluation", "results")
LATEST_RESULTS_PATH = os.path.join(RESULTS_DIR, "latest_results.json")


def _load_dataset():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Evaluation dataset not found.")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/dataset")
async def get_dataset():
    """Return the evaluation dataset."""
    return {"success": True, "dataset": _load_dataset()}


@router.post("/run")
async def run_evaluation():
    """Run the evaluation framework against the dataset."""
    dataset = _load_dataset()
    logger.info(f"Starting evaluation run for {len(dataset)} prompts")

    engine = EvaluationEngine()
    results = []

    for idx, test_case in enumerate(dataset):
        logger.info(f"--- Running Test {idx+1}/{len(dataset)}: {test_case['id']} ---")
        metrics = await engine.evaluate_prompt(test_case)
        results.append(metrics)

    logger.info("Calculating final evaluation metrics")
    summary = calculate_metrics(results)

    final_output = {
        "success": True,
        "summary": summary,
        "results": results
    }

    # Store results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(LATEST_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    return final_output


@router.get("/latest")
async def get_latest_results():
    """Fetch the most recent evaluation results."""
    if not os.path.exists(LATEST_RESULTS_PATH):
        return {"success": False, "message": "No previous evaluation results found."}
    
    with open(LATEST_RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data
