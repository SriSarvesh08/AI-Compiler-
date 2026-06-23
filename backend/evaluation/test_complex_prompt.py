import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

# Add backend directory to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.evaluator import EvaluationEngine

async def main():
    engine = EvaluationEngine()
    
    prompt = """Build a system for managing educational institutions, hospitals, and employee training programs in a single platform.
Students, patients, and employees should have separate dashboards.
Admins can manage everything.
Managers can manage employees but cannot access patient data.
Doctors can access patient records but cannot access employee records.
Faculty can access student records but cannot access patient records.
Premium organizations should have access to advanced analytics, AI recommendations, and custom reporting."""

    test_case = {
        "id": "complex_test",
        "category": "complex",
        "prompt": prompt
    }

    print("Running evaluation engine...")
    metrics = await engine.evaluate_prompt(test_case)
    
    print("\n" + "="*50)
    print("RESULTS:")
    print(f"Success: {metrics['success']}")
    print(f"Failure Type: {metrics['failure_type']}")
    print(f"Latency: {metrics['latency_ms']}ms")
    print(f"Validation Passed: {metrics['final_validation_passed']}")
    print(f"Runtime Ready: {metrics['runtime_ready']}")
    print("="*50 + "\n")

    # To inspect pages and components, we'll need to run the pipeline manually or mock the evaluator 
    # Let's run it manually to see the exact schema counts
    print("Running manual pipeline to get counts...")
    intent, _ = await engine.intent_extractor.extract(prompt)
    print(f"Extracted Roles ({len(intent.roles)}): {intent.roles}")
    print(f"Extracted Features ({len(intent.features)}): {intent.features}")
    
    architecture, _ = await engine.system_designer.design(intent)
    print(f"Designed Pages ({len(architecture.pages)}): {[p.name for p in architecture.pages]}")
    
    schemas, _ = await engine.schema_generator.generate(architecture)
    ui_pages = schemas.ui_schema.pages if schemas and schemas.ui_schema else []
    print(f"UI Schema Pages ({len(ui_pages)})")
    
    total_components = sum(len(p.components) for p in ui_pages)
    print(f"UI Schema Components ({total_components})")
    
if __name__ == "__main__":
    asyncio.run(main())
