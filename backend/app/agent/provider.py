import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.agent.prompts import SYSTEM_PROMPT, generate_user_prompt
from backend.app.agent.validator import AgentOutputValidator
from backend.app.agent.fallback import DeterministicFallbackAgent
from backend.app.agent.reflection import AgentReflectionEngine

class AgentProvider:
    """
    LLM Provider Abstraction.
    Invokes live LLM (OpenAI / Gemini / Claude API if configured) or seamless deterministic fallback.
    """
    
    @classmethod
    def generate_recommendation(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        allowed_actions = context.get("allowed_actions", ["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"])
        failure_code = context.get("case", {}).get("failure_code", "gateway_timeout")
        attempt_count = context.get("subscription", {}).get("retry_count", 1)
        max_attempts = context.get("policy", {}).get("retry_limit", 3)

        # If LLM key not configured or explicit demo fallback, use Deterministic Fallback directly
        if not settings.LLM_API_KEY:
            fallback_dict = DeterministicFallbackAgent.generate_fallback_recommendation(
                failure_code=failure_code,
                attempt_count=attempt_count,
                max_attempts=max_attempts,
                days_since_failure=0,
                allowed_actions=allowed_actions
            )
            reflected_dict, _ = AgentReflectionEngine.reflect_if_needed(fallback_dict, context)
            return reflected_dict

        # If API key is present, attempt live provider call with deterministic fallback handling
        try:
            # Simple OpenAI/OpenAI-compatible chat completion payload
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            user_prompt = generate_user_prompt(json.dumps(context))
            body = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                content = res_body["choices"][0]["message"]["content"]
                
                is_valid, validated_output, error_msg = AgentOutputValidator.validate_raw_json(content, allowed_actions)
                if is_valid and validated_output:
                    res_dict = validated_output.model_dump()
                    res_dict["source"] = "LLM"
                    reflected_dict, _ = AgentReflectionEngine.reflect_if_needed(res_dict, context)
                    return reflected_dict
        except Exception:
            pass # Fallback cleanly on timeout or network issue

        # Deterministic Fallback on LLM failure
        fallback_dict = DeterministicFallbackAgent.generate_fallback_recommendation(
            failure_code=failure_code,
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            days_since_failure=0,
            allowed_actions=allowed_actions
        )
        reflected_dict, _ = AgentReflectionEngine.reflect_if_needed(fallback_dict, context)
        return reflected_dict
