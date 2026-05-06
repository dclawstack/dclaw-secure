import uuid
from datetime import datetime, timezone
from random import randint

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ScanIn(BaseModel):
    target_url: str
    scan_type: str


class Vulnerability(BaseModel):
    name: str
    severity: str


class SecurityScan(BaseModel):
    id: str
    target_url: str
    scan_type: str
    risk_score: int
    vulnerabilities: list[Vulnerability]
    status: str
    created_at: str


@router.post("/scans", response_model=SecurityScan)
async def create_scan(payload: ScanIn):
    return SecurityScan(
        id=str(uuid.uuid4()),
        target_url=payload.target_url,
        scan_type=payload.scan_type,
        risk_score=randint(1, 100),
        vulnerabilities=[Vulnerability(name="XSS", severity="high")],
        status="completed",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/scans/{scan_id}/report")
async def get_scan_report(scan_id: str):
    return [
        {"name": "XSS", "severity": "high", "description": "Reflected XSS in search parameter"},
        {"name": "SQL Injection", "severity": "critical", "description": "SQLi in login form"},
        {"name": "Missing Headers", "severity": "medium", "description": "Content-Security-Policy not set"},
    ]
