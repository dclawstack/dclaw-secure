"""AI Security Copilot service — OpenRouter or Ollama backend."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import httpx

from app.core.config import settings
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability, VulnSeverity, VulnStatus
from app.models.security_scan import SecurityScan
from app.models.policy import Policy, PolicyAcknowledgment, PolicyStatus
from app.models.compliance import ComplianceFramework, ComplianceControl, ControlStatus


async def _build_security_context(db: AsyncSession) -> tuple[str, dict]:
    """Query the DB and return a context string + sources metadata."""

    # Asset summary
    asset_count_result = await db.execute(select(func.count()).select_from(Asset))
    asset_count = asset_count_result.scalar() or 0

    # Vulnerability breakdown
    sev_result = await db.execute(
        select(Vulnerability.severity, func.count())
        .where(Vulnerability.status != VulnStatus.RESOLVED)
        .group_by(Vulnerability.severity)
    )
    vulns_by_sev = {sev: cnt for sev, cnt in sev_result.all()}

    # Top 5 critical/high open vulns
    top_vulns_result = await db.execute(
        select(Vulnerability)
        .where(
            Vulnerability.severity.in_([VulnSeverity.CRITICAL, VulnSeverity.HIGH]),
            Vulnerability.status == VulnStatus.OPEN,
        )
        .order_by(Vulnerability.discovered_at.desc())
        .limit(5)
    )
    top_vulns = list(top_vulns_result.scalars().all())

    # Policy acknowledgment rate
    pub_policies_result = await db.execute(
        select(func.count()).select_from(Policy)
        .where(Policy.status == PolicyStatus.PUBLISHED, Policy.requires_acknowledgment == True)
    )
    pub_policies = pub_policies_result.scalar() or 0
    total_acks_result = await db.execute(
        select(func.count()).select_from(PolicyAcknowledgment)
        .where(PolicyAcknowledgment.acknowledged_at.isnot(None))
    )
    total_acks = total_acks_result.scalar() or 0

    # Compliance posture
    frameworks_result = await db.execute(
        select(ComplianceFramework).where(ComplianceFramework.is_active == True)
    )
    frameworks = list(frameworks_result.scalars().all())
    compliance_summary = []
    for fw in frameworks:
        total_result = await db.execute(
            select(func.count()).select_from(ComplianceControl)
            .where(ComplianceControl.framework_id == fw.id)
        )
        total_ctrl = total_result.scalar() or 0
        impl_result = await db.execute(
            select(func.count()).select_from(ComplianceControl)
            .where(
                ComplianceControl.framework_id == fw.id,
                ComplianceControl.status == ControlStatus.IMPLEMENTED,
            )
        )
        impl_ctrl = impl_result.scalar() or 0
        na_result = await db.execute(
            select(func.count()).select_from(ComplianceControl)
            .where(
                ComplianceControl.framework_id == fw.id,
                ComplianceControl.status == ControlStatus.NOT_APPLICABLE,
            )
        )
        na_ctrl = na_result.scalar() or 0
        applicable = total_ctrl - na_ctrl
        pct = round(impl_ctrl / applicable * 100, 1) if applicable > 0 else 0
        compliance_summary.append({"name": fw.name, "pct": pct, "total": total_ctrl, "implemented": impl_ctrl})

    # Build context text
    lines = [
        f"ASSET INVENTORY: {asset_count} total assets tracked.",
        "",
        "OPEN VULNERABILITIES BY SEVERITY:",
    ]
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = vulns_by_sev.get(sev, 0)
        lines.append(f"  - {sev.upper()}: {count}")

    if top_vulns:
        lines.append("")
        lines.append("TOP OPEN CRITICAL/HIGH VULNERABILITIES:")
        for v in top_vulns:
            lines.append(f"  - [{v.severity.upper()}] {v.title} (CVE: {v.cve_id or 'N/A'})")

    lines.append("")
    if pub_policies > 0:
        lines.append(f"POLICY ACKNOWLEDGMENTS: {total_acks} acknowledgments across {pub_policies} published policies requiring acknowledgment.")
    else:
        lines.append("POLICY ACKNOWLEDGMENTS: No published policies requiring acknowledgment yet.")

    if compliance_summary:
        lines.append("")
        lines.append("COMPLIANCE POSTURE:")
        for fw in compliance_summary:
            lines.append(f"  - {fw['name']}: {fw['pct']}% ({fw['implemented']}/{fw['total']} controls implemented)")
    else:
        lines.append("")
        lines.append("COMPLIANCE: No compliance frameworks configured yet.")

    context_text = "\n".join(lines)
    sources = {
        "asset_count": asset_count,
        "vulnerabilities_by_severity": {k: v for k, v in vulns_by_sev.items()},
        "policy_acknowledgments": total_acks,
        "compliance_frameworks": compliance_summary,
    }
    return context_text, sources


def _build_messages(security_context: str, history: list[dict], user_message: str) -> list[dict]:
    system_prompt = (
        "You are the DClaw Secure AI Copilot — an expert security analyst assistant. "
        "You have access to real-time data from the organization's security platform. "
        "Answer questions about the security posture, vulnerabilities, compliance status, and policies. "
        "Be concise, actionable, and security-focused. "
        "Always suggest concrete next steps.\n\n"
        "CURRENT SECURITY POSTURE DATA:\n"
        f"{security_context}"
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


async def _call_openrouter(messages: list[dict]) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://dclaw-secure.dclawstack.io",
                "X-Title": "DClaw Secure Copilot",
            },
            json={"model": settings.openrouter_model, "messages": messages},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_ollama(messages: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ollama_url}/api/chat",
            json={"model": settings.ollama_model, "messages": messages, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


async def generate_response(
    db: AsyncSession,
    user_message: str,
    history: list[dict],
) -> tuple[str, dict]:
    """Return (assistant_reply, sources_dict)."""
    context_text, sources = await _build_security_context(db)
    messages = _build_messages(context_text, history, user_message)

    provider = settings.ai_provider
    try:
        if provider == "ollama":
            reply = await _call_ollama(messages)
        else:
            reply = await _call_openrouter(messages)
    except Exception as exc:
        reply = (
            "I'm currently unable to reach the AI backend. "
            f"Here's a summary of your security posture from the database:\n\n{context_text}\n\n"
            f"(Error: {exc})"
        )

    return reply, sources


# ─── C2.1 Vulnerability Prioritization ──────────────────────────────────────

_SEVERITY_BASE = {"critical": 85, "high": 65, "medium": 40, "low": 20, "info": 5}
_ENV_MULTIPLIER = {"production": 1.0, "staging": 0.7, "development": 0.4}


def _heuristic_score(severity: str, environment: str, cvss: float | None) -> float:
    """Fallback score when LLM is unavailable."""
    base = _SEVERITY_BASE.get(severity, 40)
    mult = _ENV_MULTIPLIER.get(environment, 0.6)
    if cvss is not None:
        base = max(base, cvss * 10)
    return min(round(base * mult, 1), 100.0)


async def prioritize_vulnerability(
    vuln_title: str,
    vuln_description: str,
    severity: str,
    cvss_score: float | None,
    cve_id: str | None,
    asset_name: str,
    asset_type: str,
    environment: str,
) -> tuple[float, str]:
    """Return (business_impact_score 0-100, reason string)."""
    prompt = (
        "You are a security risk analyst. Score the business impact of this vulnerability "
        "on a scale of 0 to 100, where 100 is catastrophic immediate business impact.\n\n"
        f"Vulnerability: {vuln_title}\n"
        f"Description: {vuln_description}\n"
        f"Severity: {severity.upper()}"
        + (f" | CVSS: {cvss_score}" if cvss_score else "")
        + (f" | CVE: {cve_id}" if cve_id else "") + "\n"
        f"Affected asset: {asset_name} ({asset_type}) in {environment} environment\n\n"
        "Respond with exactly two lines:\n"
        "SCORE: <integer 0-100>\n"
        "REASON: <one sentence explaining the score>"
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        if settings.ai_provider == "ollama":
            raw = await _call_ollama(messages)
        else:
            raw = await _call_openrouter(messages)
        score_line = next((l for l in raw.splitlines() if l.startswith("SCORE:")), "")
        reason_line = next((l for l in raw.splitlines() if l.startswith("REASON:")), "")
        score = float(score_line.replace("SCORE:", "").strip())
        score = max(0.0, min(100.0, score))
        reason = reason_line.replace("REASON:", "").strip() or raw[:200]
    except Exception:
        score = _heuristic_score(severity, environment, cvss_score)
        reason = (
            f"Heuristic score: {severity} severity on a {environment} asset "
            + (f"(CVSS {cvss_score})" if cvss_score else "") + "."
        )
    return score, reason
