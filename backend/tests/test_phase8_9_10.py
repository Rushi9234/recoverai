import pytest
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base, init_db
from backend.app.models.domain import RecoveryCase, Customer, Subscription, RecoveryAction, AuditEvent
from scripts.seed_demo import seed_demo_data
from scripts.reset_demo import reset_demo
from scripts.run_evaluation import run_evaluation

def test_demo_seeding_and_reset():
    seed_demo_data()
    
    # Verify evaluation benchmark runs on synthetic dataset
    report = run_evaluation("data/synthetic_50.json", "data/ground_truth.json")
    assert report["unsafe_action_rate_pct"] == 0.0
    assert report["stop_rule_violation_rate_pct"] == 0.0
    assert report["duplicate_execution_rate_pct"] == 0.0

    # Reset demo database
    reset_demo()
