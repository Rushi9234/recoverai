import json
from typing import Dict, Any, Tuple, Optional, List
from pydantic import BaseModel, Field, field_validator
from backend.app.models.enums import DiagnosisCategoryEnum, ActionTypeEnum

class AgentDiagnosisSchema(BaseModel):
    category: DiagnosisCategoryEnum
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(min_length=1)
    explanation: str

class AgentRecommendationSchema(BaseModel):
    action: ActionTypeEnum
    timing: str = "NOW"
    delay_hours: Optional[int] = None
    expected_outcome: str = "HIGH"

class AgentOutputSchema(BaseModel):
    diagnosis: AgentDiagnosisSchema
    recommendation: AgentRecommendationSchema
    customer_message: Optional[str] = None

class AgentOutputValidator:
    @staticmethod
    def validate_raw_json(raw_json_str: str, allowed_actions: List[str]) -> Tuple[bool, Optional[AgentOutputSchema], Optional[str]]:
        try:
            # Clean markdown codeblocks if LLM returned ```json ... ```
            clean_str = raw_json_str.strip()
            if clean_str.startswith("```"):
                lines = clean_str.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_str = "\n".join(lines).strip()

            parsed_dict = json.loads(clean_str)
            validated = AgentOutputSchema(**parsed_dict)

            # Validate action is in allowed actions
            action_name = validated.recommendation.action.value
            if action_name not in allowed_actions and validated.recommendation.action.name not in allowed_actions:
                return False, None, f"Action '{action_name}' is not in allowed_actions: {allowed_actions}"

            return True, validated, None
        except json.JSONDecodeError as e:
            return False, None, f"JSON decode error: {str(e)}"
        except Exception as e:
            return False, None, f"Schema validation error: {str(e)}"
