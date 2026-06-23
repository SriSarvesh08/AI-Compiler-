"""
Metrics Module for Day 7 Evaluation Framework.

Calculates aggregated performance data across a suite of evaluation runs.
"""

from typing import List, Dict, Any


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics for a batch of evaluation results."""
    total_tests = len(results)
    if total_tests == 0:
        return {}

    passed_tests = sum(1 for r in results if r.get("success", False))
    failed_tests = total_tests - passed_tests
    
    runtime_ready_count = sum(1 for r in results if r.get("runtime_ready", False))
    
    total_latency = sum(r.get("latency_ms", 0.0) for r in results)
    total_repair_attempts = sum(r.get("repair_attempts", 0) for r in results)
    total_errors_before = sum(r.get("error_count_before_repair", 0) for r in results)
    total_errors_after = sum(r.get("error_count_after_repair", 0) for r in results)

    # Categories
    normal_results = [r for r in results if r.get("category") == "normal"]
    edge_results = [r for r in results if r.get("category") == "edge"]
    
    normal_passed = sum(1 for r in normal_results if r.get("success", False))
    edge_passed = sum(1 for r in edge_results if r.get("success", False))

    normal_success_rate = round((normal_passed / len(normal_results) * 100) if normal_results else 0, 2)
    edge_case_success_rate = round((edge_passed / len(edge_results) * 100) if edge_results else 0, 2)

    # Failure counts
    failures = [r.get("failure_type") for r in results if r.get("failure_type")]
    failure_counts = {}
    for f in failures:
        failure_counts[f] = failure_counts.get(f, 0) + 1

    most_common_failure_types = []
    if failure_counts:
        # Sort by count desc
        sorted_failures = sorted(failure_counts.items(), key=lambda item: item[1], reverse=True)
        most_common_failure_types = [{"type": k, "count": v} for k, v in sorted_failures]

    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": round((passed_tests / total_tests) * 100, 2),
        "runtime_ready_rate": round((runtime_ready_count / total_tests) * 100, 2),
        "average_latency_ms": round(total_latency / total_tests, 2),
        "average_repair_attempts": round(total_repair_attempts / total_tests, 2),
        "average_errors_before_repair": round(total_errors_before / total_tests, 2),
        "average_errors_after_repair": round(total_errors_after / total_tests, 2),
        "most_common_failure_types": most_common_failure_types,
        "normal_prompt_success_rate": normal_success_rate,
        "edge_case_success_rate": edge_case_success_rate
    }

    return summary
