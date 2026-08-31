from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.app.core.database import get_db

router = APIRouter(prefix="/api/simulator", tags=["Simulator"])

@router.post("/compare", summary="Compare Recovery Strategies in Simulator")
def compare_strategies(payload: Dict[str, Any], db: Session = Depends(get_db)):
    case_ids = payload.get("case_ids", [])
    strategies = payload.get("strategies", ["AI_RECOMMENDED", "CONSERVATIVE", "AGGRESSIVE", "CURRENT_POLICY"])

    # Assumptions model
    results = [
        {
            "strategy": "AI_RECOMMENDED",
            "projected_recovered_minor": 3521000,
            "projected_action_count": 41,
            "projected_contact_count": 11,
            "projected_blocked_count": 9,
            "recovery_rate": 0.645,
            "outcome_type": "PROJECTED"
        },
        {
            "strategy": "CONSERVATIVE",
            "projected_recovered_minor": 2840000,
            "projected_action_count": 28,
            "projected_contact_count": 6,
            "projected_blocked_count": 16,
            "recovery_rate": 0.520,
            "outcome_type": "PROJECTED"
        },
        {
            "strategy": "AGGRESSIVE",
            "projected_recovered_minor": 3890000,
            "projected_action_count": 62,
            "projected_contact_count": 24,
            "projected_blocked_count": 3,
            "recovery_rate": 0.712,
            "outcome_type": "PROJECTED"
        },
        {
            "strategy": "CURRENT_POLICY",
            "projected_recovered_minor": 3140000,
            "projected_action_count": 35,
            "projected_contact_count": 10,
            "projected_blocked_count": 12,
            "recovery_rate": 0.575,
            "outcome_type": "PROJECTED"
        }
    ]

    return {
        "data": {
            "results": [r for r in results if r["strategy"] in strategies]
        }
    }
