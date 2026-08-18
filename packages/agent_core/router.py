from agent_core.schemas import RouteDecision


def route(message: str) -> RouteDecision:
    text = message.casefold()
    reminder_terms = ("remind me", "reminder", "notify me")
    research_terms = ("research", "compare", "current", "latest", "find sources")
    if any(term in text for term in reminder_terms):
        return RouteDecision(mode="PRODUCTIVITY", confidence=0.98, needs_task_state=True, risk="INTERNAL_WRITE", expected_output="REMINDER")
    if any(term in text for term in research_terms):
        return RouteDecision(mode="RESEARCH", confidence=0.80, needs_web=True, expected_output="RESEARCH_REPORT")
    if "what did i" in text or "remember" in text:
        return RouteDecision(mode="MEMORY_LOOKUP", confidence=0.75, needs_memory=True, memory_scopes=["episodic"])
    return RouteDecision(mode="CHAT", confidence=0.80)
