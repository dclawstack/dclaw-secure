from app.models.identity import IdentityProfile, BehaviorEvent, BehaviorEventType
from app.services.ai_service import _call_openrouter, _call_ollama
from app.core.config import settings

_RISK_WEIGHTS = {
    BehaviorEventType.PRIVILEGE_ESCALATION: 30,
    BehaviorEventType.DATA_EXPORT: 25,
    BehaviorEventType.FAILED_AUTH: 20,
    BehaviorEventType.API_CALL: 5,
    BehaviorEventType.FILE_ACCESS: 3,
    BehaviorEventType.LOGIN: 1,
    BehaviorEventType.LOGOUT: 0,
}


def _heuristic_risk(profile: IdentityProfile, recent_events: list[BehaviorEvent]) -> tuple[float, str]:
    """Compute risk score from recent behavior heuristics."""
    score = 0.0
    reasons = []

    for event in recent_events[-20:]:
        weight = _RISK_WEIGHTS.get(event.event_type, 2)
        score += weight
        if event.event_type == BehaviorEventType.PRIVILEGE_ESCALATION:
            reasons.append("privilege escalation detected")
        elif event.event_type == BehaviorEventType.DATA_EXPORT:
            reasons.append("data export activity")
        elif event.event_type == BehaviorEventType.FAILED_AUTH:
            reasons.append("failed authentication")

    locations = {e.location for e in recent_events if e.location}
    if len(locations) > 2:
        score += 15
        reasons.append("multiple geographic locations")

    score = min(score, 100.0)
    analysis = f"Risk factors: {'; '.join(set(reasons))}" if reasons else "No significant risk indicators in recent activity"
    return round(score, 1), analysis


async def analyze_identity_risk(
    profile: IdentityProfile, recent_events: list[BehaviorEvent]
) -> tuple[float, str]:
    """AI risk analysis with heuristic fallback."""
    heuristic_score, heuristic_analysis = _heuristic_risk(profile, recent_events)

    event_summary = "\n".join(
        f"- {e.event_type} from {e.location or 'unknown'} at {e.occurred_at}"
        for e in recent_events[-10:]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a UEBA (User and Entity Behavior Analytics) system. "
                "Analyze the user's recent activity and return ONLY:\n"
                "RISK_SCORE: 0-100\n"
                "ANALYSIS: one sentence summary of risk indicators\n"
                "No other text."
            ),
        },
        {
            "role": "user",
            "content": (
                f"User: {profile.email} ({profile.role or 'no role'}, {profile.department or 'no dept'})\n"
                f"Recent events:\n{event_summary or 'No recent activity'}\n"
            ),
        },
    ]

    try:
        if settings.ai_provider == "openrouter" and settings.openrouter_api_key:
            raw = await _call_openrouter(messages)
        else:
            raw = await _call_ollama(messages)

        score = heuristic_score
        analysis = heuristic_analysis

        for line in raw.splitlines():
            if line.startswith("RISK_SCORE:"):
                try:
                    score = max(0.0, min(100.0, float(line.split(":", 1)[1].strip())))
                except ValueError:
                    pass
            elif line.startswith("ANALYSIS:"):
                analysis = line.split(":", 1)[1].strip()

        return round(score, 1), analysis
    except Exception:
        return heuristic_score, heuristic_analysis
