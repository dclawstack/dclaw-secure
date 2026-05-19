from app.models.siem_event import SiemEvent, SiemSeverity
from app.services.ai_service import _call_openrouter, _call_ollama
from app.core.config import settings

_SEVERITY_RISK = {
    SiemSeverity.CRITICAL: 90,
    SiemSeverity.HIGH: 70,
    SiemSeverity.MEDIUM: 45,
    SiemSeverity.LOW: 20,
    SiemSeverity.INFO: 5,
}


def _heuristic_correlate(event: SiemEvent, recent: list[SiemEvent]) -> tuple[bool, float, str]:
    """Return (is_anomaly, risk_score, analysis) using rules when LLM unavailable."""
    base_score = _SEVERITY_RISK.get(event.severity, 10)
    is_anomaly = False
    reasons = []

    if event.event_type == "threat":
        is_anomaly = True
        base_score = max(base_score, 85)
        reasons.append("Event categorized as direct threat")

    same_source_recent = [e for e in recent if e.source_system == event.source_system and e.id != event.id]
    failed_auths = [e for e in same_source_recent if e.event_type == "authentication" and "fail" in str(e.normalized_data).lower()]
    if len(failed_auths) >= 3:
        is_anomaly = True
        base_score = min(base_score + 25, 100)
        reasons.append(f"Repeated authentication failures ({len(failed_auths)} recent events from same source)")

    if event.severity in (SiemSeverity.CRITICAL, SiemSeverity.HIGH):
        is_anomaly = True
        reasons.append(f"High severity event: {event.severity}")

    analysis = "; ".join(reasons) if reasons else f"Routine {event.event_type} event from {event.source_system}"
    return is_anomaly, round(base_score, 1), analysis


async def correlate_event(event: SiemEvent, recent_events: list[SiemEvent]) -> tuple[bool, float, str]:
    """AI-powered event correlation. Falls back to heuristics if LLM unavailable."""
    heuristic_anomaly, heuristic_score, heuristic_analysis = _heuristic_correlate(event, recent_events)

    context = (
        f"Security event from {event.source_system}:\n"
        f"Type: {event.event_type}, Severity: {event.severity}\n"
        f"Data: {event.normalized_data or event.raw_event}\n\n"
        f"Recent events from same source: {len([e for e in recent_events if e.source_system == event.source_system])}\n"
        f"Recent anomalies in feed: {len([e for e in recent_events if e.is_anomaly])}\n"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a security analyst performing SIEM event correlation. "
                "Analyze the event and respond ONLY with:\n"
                "ANOMALY: yes/no\n"
                "RISK_SCORE: 0-100\n"
                "ANALYSIS: one sentence explanation\n"
                "No other text."
            ),
        },
        {"role": "user", "content": context},
    ]

    try:
        if settings.ai_provider == "openrouter" and settings.openrouter_api_key:
            raw = await _call_openrouter(messages)
        else:
            raw = await _call_ollama(messages)

        anomaly = False
        score = heuristic_score
        analysis = heuristic_analysis

        for line in raw.splitlines():
            if line.startswith("ANOMALY:"):
                anomaly = "yes" in line.lower()
            elif line.startswith("RISK_SCORE:"):
                try:
                    score = max(0.0, min(100.0, float(line.split(":", 1)[1].strip())))
                except ValueError:
                    pass
            elif line.startswith("ANALYSIS:"):
                analysis = line.split(":", 1)[1].strip()

        return anomaly, round(score, 1), analysis
    except Exception:
        return heuristic_anomaly, heuristic_score, heuristic_analysis
