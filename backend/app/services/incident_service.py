"""Incident response AI service — generates SOAR playbooks."""

from app.models.incident import Incident, IncidentType
from app.services.ai_service import _call_openrouter, _call_ollama
from app.core.config import settings

_HEURISTIC_PLAYBOOKS = {
    IncidentType.phishing: (
        "1. Isolate affected mailboxes. "
        "2. Reset credentials for impacted users. "
        "3. Scan endpoints for persistence mechanisms. "
        "4. Notify affected users and stakeholders. "
        "5. File incident report and update email filters."
    ),
    IncidentType.breach: (
        "1. Identify and contain the breach scope. "
        "2. Revoke compromised credentials and access tokens. "
        "3. Preserve forensic evidence and logs. "
        "4. Notify legal, management, and affected parties. "
        "5. Conduct root cause analysis and patch vulnerabilities."
    ),
    IncidentType.ransomware: (
        "1. Isolate infected systems from the network immediately. "
        "2. Identify ransomware variant and check for decryptors. "
        "3. Restore from clean backups after thorough eradication. "
        "4. Notify law enforcement and legal counsel. "
        "5. Conduct post-incident review and harden defenses."
    ),
    IncidentType.insider_threat: (
        "1. Disable affected user accounts and revoke access. "
        "2. Preserve all relevant logs and communications. "
        "3. Coordinate with HR and legal for investigation. "
        "4. Assess data exfiltration scope and impact. "
        "5. Implement enhanced monitoring and access controls."
    ),
    IncidentType.ddos: (
        "1. Enable DDoS mitigation / rate limiting at edge. "
        "2. Identify and block malicious source IPs or ranges. "
        "3. Scale infrastructure to absorb traffic if needed. "
        "4. Coordinate with ISP / CDN for upstream filtering. "
        "5. Document attack patterns and update defenses."
    ),
    IncidentType.vulnerability_exploit: (
        "1. Identify the exploited vulnerability and affected systems. "
        "2. Apply emergency patches or implement mitigating controls. "
        "3. Isolate affected systems pending full remediation. "
        "4. Scan environment for additional exposure points. "
        "5. Update vulnerability management records and notify stakeholders."
    ),
    IncidentType.other: (
        "1. Assess the nature and scope of the incident. "
        "2. Contain immediate threats to limit further damage. "
        "3. Preserve evidence for forensic analysis. "
        "4. Notify relevant stakeholders per incident response plan. "
        "5. Document findings and implement corrective actions."
    ),
}


def _heuristic_playbook(incident: Incident) -> str:
    template = _HEURISTIC_PLAYBOOKS.get(incident.incident_type, _HEURISTIC_PLAYBOOKS[IncidentType.other])
    return (
        f"SOAR Playbook — {incident.incident_type.value.replace('_', ' ').title()} "
        f"({incident.severity.upper()} severity)\n\n"
        + template
    )


async def generate_playbook(incident: Incident) -> str:
    """Generate a SOAR playbook for the given incident using LLM with heuristic fallback."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior incident response analyst specializing in SOAR playbook generation. "
                "Generate a concise, numbered step-by-step playbook for the given security incident. "
                "Each step should be actionable and specific. Return only the numbered list."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate a SOAR playbook for the following incident:\n"
                f"Title: {incident.title}\n"
                f"Type: {incident.incident_type.value}\n"
                f"Severity: {incident.severity}\n"
                f"Description: {incident.description}\n"
            ),
        },
    ]

    try:
        if settings.ai_provider == "openrouter" and settings.openrouter_api_key:
            raw = await _call_openrouter(messages)
        else:
            raw = await _call_ollama(messages)
        return raw.strip()
    except Exception:
        return _heuristic_playbook(incident)
