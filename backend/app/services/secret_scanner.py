"""Secret scanning service — regex-based detection with masking."""

import re
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.secret_scan import SecretScanJob, SecretFinding, SecretType
from app.core.utils import utc_now


def _mask_value(value: str) -> str:
    """Mask a secret value: first4...last4 if len > 8, else ****."""
    if len(value) > 8:
        return value[:4] + "..." + value[-4:]
    return "****"


# Each pattern: (regex, secret_type, severity)
_PATTERNS: list[tuple[re.Pattern, SecretType, str]] = [
    # AWS Access Key
    (re.compile(r'\b(AKIA[0-9A-Z]{16})\b'), SecretType.api_key, "critical"),
    # AWS Secret Access Key (40 chars after aws_secret or similar)
    (re.compile(r'(?i)aws[_\-\s]?secret[_\-\s]?(?:access[_\-\s]?)?key["\s]*[:=]["\s]*([A-Za-z0-9/+=]{40})'), SecretType.api_key, "critical"),
    # GitHub tokens
    (re.compile(r'\b(ghp_[A-Za-z0-9]{36})\b'), SecretType.token, "critical"),
    (re.compile(r'\b(gho_[A-Za-z0-9]{36})\b'), SecretType.token, "critical"),
    (re.compile(r'\b(github_pat_[A-Za-z0-9_]{59})\b'), SecretType.token, "critical"),
    # Stripe live keys
    (re.compile(r'\b(sk_live_[A-Za-z0-9]{24,})\b'), SecretType.api_key, "critical"),
    (re.compile(r'\b(pk_live_[A-Za-z0-9]{24,})\b'), SecretType.api_key, "high"),
    # Google API keys
    (re.compile(r'\b(AIza[0-9A-Za-z\-_]{35})\b'), SecretType.api_key, "high"),
    # Twilio auth token
    (re.compile(r'(?i)twilio.*auth.*token["\s]*[:=]["\s]*([A-Za-z0-9]{32})'), SecretType.token, "high"),
    # JWT secrets (long base64-like strings after jwt_secret or JWT_SECRET)
    (re.compile(r'(?i)jwt[_\-\s]?secret["\s]*[:=]["\s]*([A-Za-z0-9+/=_\-]{32,})'), SecretType.jwt_secret, "high"),
    # Database URLs
    (re.compile(r'(postgresql://[^\s"\'<>]+)'), SecretType.database_url, "critical"),
    (re.compile(r'(postgres://[^\s"\'<>]+)'), SecretType.database_url, "critical"),
    (re.compile(r'(mysql://[^\s"\'<>]+)'), SecretType.database_url, "critical"),
    (re.compile(r'(mongodb://[^\s"\'<>]+)'), SecretType.database_url, "critical"),
    (re.compile(r'(mongodb\+srv://[^\s"\'<>]+)'), SecretType.database_url, "critical"),
    # RSA private keys
    (re.compile(r'(-----BEGIN RSA PRIVATE KEY-----)'), SecretType.private_key, "critical"),
    (re.compile(r'(-----BEGIN PRIVATE KEY-----)'), SecretType.private_key, "critical"),
    (re.compile(r'(-----BEGIN EC PRIVATE KEY-----)'), SecretType.private_key, "critical"),
    # Generic API keys in config
    (re.compile(r'(?i)api[_\-]?key["\s]*[:=]["\s]*([A-Za-z0-9\-_]{16,})'), SecretType.api_key, "high"),
    (re.compile(r'(?i)apikey["\s]*[:=]["\s]*([A-Za-z0-9\-_]{16,})'), SecretType.api_key, "high"),
    # Bearer tokens
    (re.compile(r'(?i)bearer\s+([A-Za-z0-9\-_.~+/]+=*)'), SecretType.token, "high"),
    # Generic passwords in config
    (re.compile(r'(?i)password["\s]*[:=]["\s]*([^\s"\'<>{}\[\]]{8,})'), SecretType.password, "high"),
]


def scan_text(content: str, source_label: str) -> list[dict]:
    """Scan text content for secrets. Returns list of finding dicts."""
    findings = []
    lines = content.splitlines()

    for line_num, line in enumerate(lines, start=1):
        for pattern, secret_type, severity in _PATTERNS:
            for match in pattern.finditer(line):
                # Use group 1 if it exists, else full match
                try:
                    value = match.group(1)
                except IndexError:
                    value = match.group(0)

                findings.append({
                    "secret_type": secret_type,
                    "severity": severity,
                    "masked_value": _mask_value(value),
                    "file_path": source_label,
                    "line_number": line_num,
                })

    return findings


async def run_scan_job(
    job: SecretScanJob,
    content: str,
    db: AsyncSession,
) -> SecretScanJob:
    """Run scan_text on content, persist findings, and update job counts."""
    raw_findings = scan_text(content, job.scan_target)

    for f in raw_findings:
        finding = SecretFinding(
            id=uuid.uuid4(),
            job_id=job.id,
            file_path=f["file_path"],
            line_number=f["line_number"],
            secret_type=f["secret_type"],
            severity=f["severity"],
            masked_value=f["masked_value"],
            is_revoked=False,
            is_false_positive=False,
            detected_at=utc_now(),
            created_at=utc_now(),
        )
        db.add(finding)

    job.secrets_found = len(raw_findings)
    job.files_scanned = 1
    job.completed_at = utc_now()
    job.status = "completed"

    await db.commit()
    await db.refresh(job)
    return job
