"""Compliance scanner service — runs automated compliance scans with LLM gap analysis."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import settings
from app.models.compliance import ComplianceFramework, ComplianceControl, ControlStatus
from app.models.compliance_scan import ComplianceScan, ScanTrigger, ComplianceScanStatus
from app.core.utils import utc_now


async def _call_openrouter(messages: list[dict]) -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://dclaw-secure.dclawstack.io",
                "X-Title": "DClaw Secure Compliance Scanner",
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


def _heuristic_gap_analysis(failed_controls: list[ComplianceControl]) -> str:
    """Generate a gap analysis from failed control titles when LLM is unavailable."""
    if not failed_controls:
        return "No compliance gaps identified. All controls are either implemented or not applicable."

    lines = [
        f"Compliance gap analysis identified {len(failed_controls)} control(s) requiring attention:",
        "",
    ]
    for ctrl in failed_controls:
        lines.append(f"- [{ctrl.control_id}] {ctrl.title}: Control is not implemented and requires remediation.")

    lines.append("")
    lines.append(
        "Recommended actions: Review each failed control, assign owners, establish implementation timelines, "
        "and collect evidence of remediation."
    )
    return "\n".join(lines)


async def scan_framework(
    framework_id: uuid.UUID,
    db: AsyncSession,
    triggered_by: str = "system",
    scan_type: ScanTrigger = ScanTrigger.manual,
) -> ComplianceScan:
    """Load framework and all controls, evaluate compliance, generate gap analysis via LLM."""

    # Load framework
    fw_result = await db.execute(
        select(ComplianceFramework).where(ComplianceFramework.id == framework_id)
    )
    framework = fw_result.scalar_one_or_none()
    if not framework:
        raise ValueError(f"Framework {framework_id} not found")

    # Load all controls with evidence eagerly loaded
    ctrl_result = await db.execute(
        select(ComplianceControl).where(ComplianceControl.framework_id == framework_id)
    )
    controls = list(ctrl_result.scalars().all())

    passed = 0
    failed = 0

    failed_controls: list[ComplianceControl] = []

    for ctrl in controls:
        # Access evidence (loaded via selectin in model)
        has_evidence = len(ctrl.evidence) > 0 if ctrl.evidence else False
        if has_evidence and ctrl.status == ControlStatus.IMPLEMENTED:
            passed += 1
        elif ctrl.status == ControlStatus.NOT_IMPLEMENTED:
            failed += 1
            failed_controls.append(ctrl)
        # else: neutral (partially_implemented, not_applicable, implemented without evidence)

    controls_checked = len(controls)

    # Generate gap analysis via LLM
    gap_analysis: str
    prompt_messages = [
        {
            "role": "user",
            "content": (
                f"You are a compliance expert. Analyze the following compliance scan results for framework '{framework.name}':\n\n"
                f"Total controls: {controls_checked}\n"
                f"Passed controls: {passed}\n"
                f"Failed controls: {failed}\n\n"
                "Failed control titles:\n"
                + "\n".join(f"- [{c.control_id}] {c.title}" for c in failed_controls)
                + "\n\nProvide a concise gap analysis (3-5 sentences) and actionable recommendations."
            ),
        }
    ]

    try:
        if settings.ai_provider == "ollama":
            gap_analysis = await _call_ollama(prompt_messages)
        else:
            gap_analysis = await _call_openrouter(prompt_messages)
    except Exception:
        gap_analysis = _heuristic_gap_analysis(failed_controls)

    now = utc_now()
    scan = ComplianceScan(
        id=uuid.uuid4(),
        framework_id=framework_id,
        triggered_by=triggered_by,
        scan_type=scan_type,
        status=ComplianceScanStatus.completed,
        controls_checked=controls_checked,
        controls_passed=passed,
        controls_failed=failed,
        gap_analysis=gap_analysis,
        recommendations=None,
        started_at=now,
        completed_at=now,
        created_at=now,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan
