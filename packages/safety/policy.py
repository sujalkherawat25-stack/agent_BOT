from pydantic import BaseModel


class ActionPolicyDecision(BaseModel):
    allow: bool
    requires_approval: bool
    reason: str
    risk_level: int


def evaluate(risk_level: int) -> ActionPolicyDecision:
    if risk_level >= 3:
        return ActionPolicyDecision(allow=False, requires_approval=True, reason="High-consequence actions are not enabled.", risk_level=risk_level)
    return ActionPolicyDecision(allow=True, requires_approval=risk_level >= 2, reason="Policy evaluated before execution.", risk_level=risk_level)
