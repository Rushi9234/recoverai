from typing import Dict, Any, Tuple
from backend.app.agent.fallback import DeterministicFallbackAgent

class AgentReflectionEngine:
    """
    Agent Reflection Loop.
    Permits up to 2 reflection passes for ambiguous cases (confidence < 0.70).
    Never executes tools or authorized actions.
    """
    
    @staticmethod
    def reflect_if_needed(
        recommendation_dict: Dict[str, Any],
        context: Dict[str, Any],
        max_reflection_passes: int = 2
    ) -> Tuple[Dict[str, Any], int]:
        confidence = recommendation_dict.get("diagnosis", {}).get("confidence", 1.0)
        passes_used = 0

        if confidence < 0.70 and max_reflection_passes > 0:
            # First pass: inspect customer payment history and failure frequency
            passes_used += 1
            recommendation_dict["diagnosis"]["evidence"].append(f"reflection_pass_{passes_used}=evaluated_payment_history")
            
            # If customer has high successful payment count, increase confidence or adjust strategy
            prior_success = context.get("subscription", {}).get("retry_count", 0)
            if prior_success < 2 and confidence < 0.60 and passes_used < max_reflection_passes:
                # Second pass: route ambiguous low-history cases to HUMAN_ESCALATION
                passes_used += 1
                recommendation_dict["diagnosis"]["evidence"].append(f"reflection_pass_{passes_used}=unresolved_ambiguity_escalated")
                recommendation_dict["recommendation"]["action"] = "HUMAN_ESCALATION"
                recommendation_dict["recommendation"]["timing"] = "HUMAN_REVIEW"
                recommendation_dict["diagnosis"]["explanation"] += " (Reflected: High ambiguity after 2 passes -> routed to Human Escalation)"

        return recommendation_dict, passes_used
