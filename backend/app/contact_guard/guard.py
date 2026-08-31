from datetime import datetime, timezone, timedelta
from typing import Tuple, List, Optional, Dict, Any
from backend.app.models.enums import ConsentStateEnum, SuppressionStateEnum, ContactChannelEnum

class ContactGuard:
    """
    Deterministic Customer Contact Guard.
    Enforces contact limits, cooldowns, and suppression rules before customer outreach.
    """
    
    @staticmethod
    def evaluate_contact(
        channel: ContactChannelEnum,
        consent_state: ConsentStateEnum,
        suppression_state: SuppressionStateEnum,
        contacts_24h: int,
        contacts_7d: int,
        last_contact_at: Optional[datetime],
        limit_24h: int = 1,
        limit_7d: int = 3,
        cooldown_hours: int = 24
    ) -> Tuple[bool, str, Dict[str, Any]]:
        details = {
            "channel": channel,
            "contacts_24h": contacts_24h,
            "limit_24h": limit_24h,
            "contacts_7d": contacts_7d,
            "limit_7d": limit_7d,
            "consent_state": consent_state,
            "suppression_state": suppression_state,
        }

        # 1. Hard suppression check
        if suppression_state in [SuppressionStateEnum.DND, SuppressionStateEnum.MERCHANT_BLOCKED, SuppressionStateEnum.SYSTEM_BLOCKED]:
            return False, f"CUSTOMER_SUPPRESSED_{suppression_state.value}", details

        # 2. Consent check
        if consent_state == ConsentStateEnum.WITHDRAWN:
            return False, "CONSENT_WITHDRAWN", details

        # 3. 24h limit check
        if contacts_24h >= limit_24h:
            return False, "24H_CONTACT_LIMIT_EXCEEDED", details

        # 4. 7d limit check
        if contacts_7d >= limit_7d:
            return False, "7D_CONTACT_LIMIT_EXCEEDED", details

        # 5. Cooldown check
        if last_contact_at is not None:
            now = datetime.now(timezone.utc)
            if last_contact_at.tzinfo is None:
                last_contact_at = last_contact_at.replace(tzinfo=timezone.utc)
            elapsed_hours = (now - last_contact_at).total_seconds() / 3600.0
            details["elapsed_hours"] = round(elapsed_hours, 2)
            if elapsed_hours < cooldown_hours:
                details["cooldown_remaining_hours"] = round(cooldown_hours - elapsed_hours, 2)
                return False, "COOLDOWN_ACTIVE", details

        return True, "CONTACT_ALLOWED", details
