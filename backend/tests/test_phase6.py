import pytest
import os
import json
from scripts.run_evaluation import run_evaluation

def test_evaluation_dataset_files_exist():
    assert os.path.exists("data/synthetic_50.json")
    assert os.path.exists("data/synthetic_250.json")
    assert os.path.exists("data/ground_truth.json")

def test_run_evaluation_benchmark():
    report = run_evaluation("data/synthetic_50.json", "data/ground_truth.json")
    assert report["total_cases_processed"] == 50
    assert report["unsafe_action_rate_pct"] == 0.0
    assert report["stop_rule_violation_rate_pct"] == 0.0
    assert report["duplicate_execution_rate_pct"] == 0.0
    assert report["risk_detection_accuracy_pct"] == 100.0
    assert report["diagnosis_accuracy_pct"] >= 90.0
    assert report["median_latency_ms"] < 200.0
