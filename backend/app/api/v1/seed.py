"""
Seed / clear demo data for DClaw Secure.
POST   /api/v1/seed  — populate with realistic sample data
DELETE /api/v1/seed  — wipe all data from all tables
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now

from app.models.asset import Asset, AssetType, AssetStatus, Environment, CloudProvider
from app.models.vulnerability import Vulnerability, VulnSeverity, VulnStatus
from app.models.security_scan import SecurityScan, ScanType, ScanStatus
from app.models.incident import Incident, IncidentAction, IncidentType, IncidentStatus, ActionType
from app.models.policy import Policy, PolicyAcknowledgment, PolicyStatus, PolicyCategory
from app.models.siem_event import SiemEvent, EventType, SiemSeverity
from app.models.threat_intel import ThreatFeed, ThreatIOC, FeedType, IOCType
from app.models.identity import IdentityProfile, BehaviorEvent, BehaviorEventType
from app.models.pentest import PenTestEngagement, PenTestFinding, PenTestMethodology, EngagementStatus, FindingStatus
from app.models.secret_scan import SecretScanJob, SecretFinding, ScanTargetType, SecretType, SecretScanStatus
from app.models.compliance import ComplianceFramework, ComplianceControl, ControlStatus

router = APIRouter()


@router.post("", status_code=201)
async def seed_data(db: AsyncSession = Depends(get_db)):
    """Create realistic sample data across all DClaw Secure modules."""
    now = utc_now()
    today = now.date()

    # ── Assets ───────────────────────────────────────────────────────────────
    asset_defs = [
        dict(name="prod-api-gateway", asset_type=AssetType.API, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.AWS, region="us-east-1",
             risk_score=72, owner_email="platform@acme.io",
             description="Main customer-facing API gateway"),
        dict(name="prod-postgres-01", asset_type=AssetType.DATABASE, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.AWS, region="us-east-1",
             risk_score=88, owner_email="dba@acme.io",
             description="Primary PostgreSQL RDS instance"),
        dict(name="prod-k8s-node-03", asset_type=AssetType.SERVER, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.GCP, region="us-central1",
             risk_score=45, owner_email="infra@acme.io",
             description="GKE worker node"),
        dict(name="prod-app-container", asset_type=AssetType.CONTAINER, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.GCP, region="us-central1",
             risk_score=61, owner_email="backend@acme.io",
             description="Main application Docker image"),
        dict(name="acme-backups-s3", asset_type=AssetType.S3_BUCKET, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.AWS, region="us-west-2",
             risk_score=55, owner_email="infra@acme.io",
             description="Database and config backups"),
        dict(name="acme.io", asset_type=AssetType.DOMAIN, environment=Environment.PRODUCTION,
             status=AssetStatus.ACTIVE, cloud_provider=None, region=None,
             risk_score=30, owner_email="ops@acme.io",
             description="Primary public domain"),
        dict(name="backend-service", asset_type=AssetType.REPOSITORY, environment=Environment.DEVELOPMENT,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.ON_PREMISE, region=None,
             risk_score=40, owner_email="dev@acme.io",
             description="Backend monorepo on GitHub"),
        dict(name="dev-workstation-alice", asset_type=AssetType.WORKSTATION, environment=Environment.DEVELOPMENT,
             status=AssetStatus.ACTIVE, cloud_provider=CloudProvider.ON_PREMISE, region=None,
             risk_score=22, owner_email="alice@acme.io",
             description="Alice's dev machine"),
    ]
    assets: list[Asset] = []
    for d in asset_defs:
        a = Asset(**d)
        db.add(a)
        assets.append(a)
    await db.flush()

    # ── Vulnerabilities ───────────────────────────────────────────────────────
    vuln_defs = [
        dict(asset=assets[1], title="SQL Injection in user search endpoint",
             severity=VulnSeverity.CRITICAL, cvss_score=9.8, cve_id="CVE-2024-1234",
             status=VulnStatus.OPEN,
             description="Unsanitised input allows arbitrary SQL execution on prod-postgres-01.",
             remediation="Use parameterised queries. Patch applied in v2.3.1."),
        dict(asset=assets[0], title="API rate limiting bypass via header spoofing",
             severity=VulnSeverity.HIGH, cvss_score=7.5, cve_id=None,
             status=VulnStatus.IN_PROGRESS,
             description="X-Forwarded-For header accepted without validation, allowing rate limit bypass.",
             remediation="Validate IP source at load balancer level."),
        dict(asset=assets[3], title="Container running as root",
             severity=VulnSeverity.HIGH, cvss_score=7.2, cve_id=None,
             status=VulnStatus.OPEN,
             description="Docker container runs with UID 0, increasing blast radius of any RCE.",
             remediation="Add USER directive in Dockerfile."),
        dict(asset=assets[4], title="S3 bucket ACL allows public read",
             severity=VulnSeverity.HIGH, cvss_score=7.5, cve_id=None,
             status=VulnStatus.RESOLVED,
             description="Backup bucket was publicly readable. Fixed by removing public ACL.",
             remediation="Set bucket policy to deny all public access."),
        dict(asset=assets[2], title="Outdated kernel — CVE-2024-1086",
             severity=VulnSeverity.HIGH, cvss_score=7.8, cve_id="CVE-2024-1086",
             status=VulnStatus.IN_PROGRESS,
             description="Linux kernel 5.15 affected by privilege escalation via netfilter.",
             remediation="Upgrade kernel to 5.15.148 or later."),
        dict(asset=assets[0], title="Missing HSTS header on API gateway",
             severity=VulnSeverity.MEDIUM, cvss_score=5.3, cve_id=None,
             status=VulnStatus.OPEN,
             description="HTTP Strict-Transport-Security header not set on all endpoints.",
             remediation="Add HSTS header with min-age=31536000."),
        dict(asset=assets[6], title="Dependency confusion — internal package",
             severity=VulnSeverity.MEDIUM, cvss_score=6.1, cve_id=None,
             status=VulnStatus.OPEN,
             description="Private package name resolvable from public registry.",
             remediation="Scope private packages under company namespace."),
        dict(asset=assets[1], title="Database user has excessive privileges",
             severity=VulnSeverity.MEDIUM, cvss_score=5.5, cve_id=None,
             status=VulnStatus.OPEN,
             description="App DB user has SUPERUSER role instead of minimal required grants.",
             remediation="Revoke SUPERUSER and grant only SELECT/INSERT/UPDATE on required tables."),
        dict(asset=assets[5], title="SPF record allows all IPs (v=spf1 +all)",
             severity=VulnSeverity.LOW, cvss_score=3.1, cve_id=None,
             status=VulnStatus.OPEN,
             description="SPF record is too permissive, allowing phishing from any IP.",
             remediation="Restrict SPF to known mail servers."),
        dict(asset=assets[7], title="Unencrypted disk on dev workstation",
             severity=VulnSeverity.LOW, cvss_score=2.5, cve_id=None,
             status=VulnStatus.ACCEPTED_RISK,
             description="FileVault not enabled on Alice's machine.",
             remediation="Enable full-disk encryption."),
    ]
    for v in vuln_defs:
        asset = v.pop("asset")
        db.add(Vulnerability(asset_id=asset.id, **v))
    await db.flush()

    # ── Security Scans ────────────────────────────────────────────────────────
    scan_defs = [
        dict(asset=assets[0], scan_type=ScanType.WEB, status=ScanStatus.COMPLETED,
             findings_count=6, risk_score=71,
             started_at=now - timedelta(days=1), completed_at=now - timedelta(hours=22),
             scan_metadata={"engine": "OWASP ZAP", "pages": 142}),
        dict(asset=assets[1], scan_type=ScanType.API, status=ScanStatus.COMPLETED,
             findings_count=3, risk_score=88,
             started_at=now - timedelta(days=2), completed_at=now - timedelta(days=2, hours=-2),
             scan_metadata={"engine": "Burp Suite", "endpoints": 38}),
        dict(asset=assets[3], scan_type=ScanType.CONTAINER, status=ScanStatus.COMPLETED,
             findings_count=12, risk_score=65,
             started_at=now - timedelta(hours=6), completed_at=now - timedelta(hours=5),
             scan_metadata={"engine": "Trivy", "layers": 8}),
        dict(asset=assets[4], scan_type=ScanType.COMPLIANCE, status=ScanStatus.COMPLETED,
             findings_count=4, risk_score=55,
             started_at=now - timedelta(days=3), completed_at=now - timedelta(days=3, hours=-1),
             scan_metadata={"engine": "ScoutSuite", "checks": 300}),
        dict(asset=assets[2], scan_type=ScanType.VULNERABILITY, status=ScanStatus.COMPLETED,
             findings_count=2, risk_score=45,
             started_at=now - timedelta(hours=12), completed_at=now - timedelta(hours=11),
             scan_metadata={"engine": "Nessus", "ports": 4}),
        dict(asset=assets[0], scan_type=ScanType.WEB, status=ScanStatus.RUNNING,
             findings_count=0, risk_score=None,
             started_at=now - timedelta(minutes=15), completed_at=None,
             scan_metadata={"engine": "OWASP ZAP", "pages": 0}),
    ]
    for s in scan_defs:
        asset = s.pop("asset")
        db.add(SecurityScan(target_asset_id=asset.id, **s))
    await db.flush()

    # ── Incidents ─────────────────────────────────────────────────────────────
    inc1 = Incident(
        title="Credential stuffing attack on login endpoint",
        description="Automated attack attempting 45,000 login combinations using leaked credentials. 12 accounts compromised.",
        severity="critical", incident_type=IncidentType.breach,
        status=IncidentStatus.contained,
        affected_asset_ids=[str(assets[0].id)],
        assigned_to="alice@acme.io",
        detected_at=now - timedelta(hours=6),
        contained_at=now - timedelta(hours=4),
        ai_playbook="1. Block source IPs at WAF\n2. Force password reset for 12 affected accounts\n3. Enable CAPTCHA on login\n4. Notify affected users",
    )
    inc2 = Incident(
        title="Suspected data exfiltration via S3",
        description="Unusual volume of S3 GetObject calls from Lambda. 2.3 GB transferred to unknown external IP in 20 minutes.",
        severity="high", incident_type=IncidentType.breach,
        status=IncidentStatus.investigating,
        affected_asset_ids=[str(assets[4].id)],
        assigned_to="bob@acme.io",
        detected_at=now - timedelta(hours=2),
        ai_playbook="1. Suspend Lambda execution role\n2. Enable S3 access logging\n3. Identify destination IP in threat feeds\n4. Engage legal if PII involved",
    )
    inc3 = Incident(
        title="Phishing campaign targeting engineering team",
        description="Spear-phishing emails with malicious Word macros sent to 8 engineers. 2 opened attachment.",
        severity="high", incident_type=IncidentType.phishing,
        status=IncidentStatus.resolved,
        affected_asset_ids=[str(assets[7].id)],
        assigned_to="alice@acme.io",
        detected_at=now - timedelta(days=3),
        contained_at=now - timedelta(days=3, hours=-1),
        resolved_at=now - timedelta(days=2),
        ai_playbook="1. Isolate affected workstations\n2. Re-image machines\n3. Run full AV scan\n4. Report domain to registrar",
    )
    inc4 = Incident(
        title="Misconfigured Kubernetes RBAC — excessive permissions",
        description="Service account in prod namespace had cluster-admin role. No evidence of exploitation but exposure window was 72 hours.",
        severity="medium", incident_type=IncidentType.vulnerability_exploit,
        status=IncidentStatus.closed,
        affected_asset_ids=[str(assets[2].id)],
        assigned_to="charlie@acme.io",
        detected_at=now - timedelta(days=7),
        contained_at=now - timedelta(days=7, hours=-2),
        resolved_at=now - timedelta(days=6),
        ai_playbook="1. Revoke cluster-admin binding immediately\n2. Audit all RBAC bindings\n3. Enable audit logging",
    )
    for inc in [inc1, inc2, inc3, inc4]:
        db.add(inc)
    await db.flush()

    for inc, actions in [
        (inc1, [(ActionType.contained, "Blocked 3 /24 CIDR ranges at WAF"),
                (ActionType.notified, "Password reset emails sent to 12 affected users")]),
        (inc2, [(ActionType.contained, "Lambda execution role suspended"),
                (ActionType.escalated, "Escalated to CISO and legal team")]),
        (inc3, [(ActionType.contained, "2 workstations isolated from network"),
                (ActionType.remediated, "Machines re-imaged with clean OS image")]),
    ]:
        for atype, desc in actions:
            db.add(IncidentAction(
                incident_id=inc.id,
                action_type=atype,
                description=desc,
                performed_by="security-team@acme.io",
                performed_at=now - timedelta(hours=3),
            ))
    await db.flush()

    # ── Policies ──────────────────────────────────────────────────────────────
    policy_defs = [
        dict(title="Password & Multi-Factor Authentication Policy", version="2.1",
             category=PolicyCategory.ACCESS_CONTROL, status=PolicyStatus.PUBLISHED,
             requires_acknowledgment=True, effective_date=today - timedelta(days=90),
             content="All employees must use passwords of 16+ characters with MFA enabled on all corporate accounts. Password reuse prohibited. Annual rotation required for privileged accounts."),
        dict(title="Data Classification & Handling Policy", version="1.3",
             category=PolicyCategory.DATA_PROTECTION, status=PolicyStatus.PUBLISHED,
             requires_acknowledgment=True, effective_date=today - timedelta(days=180),
             content="All data must be classified as Public, Internal, Confidential, or Restricted. PII and payment data require encryption at rest and in transit. Retention: logs 90 days, backups 7 years."),
        dict(title="Incident Response Plan", version="3.0",
             category=PolicyCategory.INCIDENT_RESPONSE, status=PolicyStatus.PUBLISHED,
             requires_acknowledgment=False, effective_date=today - timedelta(days=60),
             content="Incident response follows NIST SP 800-61: Preparation → Detection → Containment → Eradication → Recovery → Post-Incident. P1 < 1h, P2 < 4h, P3 < 24h response SLA."),
        dict(title="Acceptable Use Policy", version="1.0",
             category=PolicyCategory.ACCEPTABLE_USE, status=PolicyStatus.DRAFT,
             requires_acknowledgment=False, effective_date=None,
             content="Corporate devices and accounts must only be used for authorised business purposes. Personal use is limited to incidental use that does not impact security or productivity."),
    ]
    policies: list[Policy] = []
    for p in policy_defs:
        pol = Policy(**p)
        db.add(pol)
        policies.append(pol)
    await db.flush()

    for policy in policies[:2]:
        for email, name in [("alice@acme.io", "Alice Chen"), ("bob@acme.io", "Bob Martinez"), ("charlie@acme.io", "Charlie Kim")]:
            db.add(PolicyAcknowledgment(
                policy_id=policy.id,
                employee_email=email,
                employee_name=name,
                acknowledged_at=now - timedelta(days=30),
                ip_address="10.0.1.5",
            ))
    await db.flush()

    # ── SIEM Events ───────────────────────────────────────────────────────────
    siem_defs = [
        dict(source="AWS-CloudTrail", etype=EventType.CLOUD, sev=SiemSeverity.CRITICAL,
             asset=assets[0], is_anomaly=True, risk_score=92.0,
             raw={"user": "svc-lambda", "action": "iam:AttachRolePolicy", "target": "AdministratorAccess"},
             ai="Service account attempted to attach AdministratorAccess policy — likely privilege escalation.", offset_h=2),
        dict(source="nginx-access-log", etype=EventType.NETWORK, sev=SiemSeverity.HIGH,
             asset=assets[4], is_anomaly=True, risk_score=78.5,
             raw={"bytes_sent": 2411724800, "dest_ip": "185.220.101.45", "duration_s": 1180},
             ai="Unusually large outbound transfer (2.3 GB) to Tor exit node in 20 minutes.", offset_h=2),
        dict(source="auth0-logs", etype=EventType.AUTHENTICATION, sev=SiemSeverity.HIGH,
             asset=assets[0], is_anomaly=True, risk_score=65.0,
             raw={"attempts": 45000, "unique_users": 8300, "source_ips": 142},
             ai="Credential stuffing pattern — 45k failed logins from 142 unique IPs in 30 minutes.", offset_h=6),
        dict(source="auth0-logs", etype=EventType.AUTHENTICATION, sev=SiemSeverity.LOW,
             asset=assets[0], is_anomaly=False, risk_score=5.0,
             raw={"user": "admin@acme.io", "ip": "10.0.1.5", "mfa": True},
             ai=None, offset_h=3),
        dict(source="k8s-audit", etype=EventType.CLOUD, sev=SiemSeverity.MEDIUM,
             asset=assets[2], is_anomaly=False, risk_score=40.0,
             raw={"resource": "ClusterRoleBinding", "action": "create", "role": "cluster-admin"},
             ai="ClusterRoleBinding created granting cluster-admin to prod service account.", offset_h=168),
        dict(source="waf-logs", etype=EventType.APPLICATION, sev=SiemSeverity.MEDIUM,
             asset=assets[0], is_anomaly=True, risk_score=55.0,
             raw={"pattern": "sqli", "requests": 320, "blocked": 318},
             ai="SQL injection pattern detected in request body. WAF blocked 318/320 requests.", offset_h=24),
        dict(source="endpoint-edr", etype=EventType.ENDPOINT, sev=SiemSeverity.HIGH,
             asset=assets[7], is_anomaly=True, risk_score=80.0,
             raw={"file": "invoice_q4.docm", "signature": "DOCM/Macro.Generic.A", "action": "quarantined"},
             ai="Macro-enabled Word document quarantined. Matches phishing campaign IOCs.", offset_h=72),
        dict(source="dlp-monitor", etype=EventType.APPLICATION, sev=SiemSeverity.LOW,
             asset=assets[7], is_anomaly=False, risk_score=15.0,
             raw={"rule": "sensitive-data-email", "user": "alice@acme.io", "recipient": "personal@gmail.com"},
             ai=None, offset_h=48),
    ]
    for s in siem_defs:
        db.add(SiemEvent(
            source_system=s["source"], event_type=s["etype"], severity=s["sev"],
            asset_id=s["asset"].id, is_anomaly=s["is_anomaly"], risk_score=s["risk_score"],
            raw_event=s["raw"], ai_analysis=s.get("ai"),
            occurred_at=now - timedelta(hours=s["offset_h"]),
        ))
    await db.flush()

    # ── Threat Intelligence ───────────────────────────────────────────────────
    feed1 = ThreatFeed(name="Abuse.ch URLhaus", feed_type=FeedType.ip_blocklist,
                       source_url="https://urlhaus-api.abuse.ch/v1/", is_active=True,
                       last_synced=now - timedelta(hours=1), ioc_count=5)
    feed2 = ThreatFeed(name="Internal Threat Feed", feed_type=FeedType.custom,
                       source_url=None, is_active=True,
                       last_synced=now - timedelta(minutes=30), ioc_count=3)
    db.add(feed1); db.add(feed2)
    await db.flush()

    ioc_defs = [
        dict(feed=feed1, ioc_type=IOCType.ip, value="185.220.101.45",
             threat_type="tor_exit_node", confidence_score=0.97),
        dict(feed=feed1, ioc_type=IOCType.domain, value="malicious-update.com",
             threat_type="c2_server", confidence_score=0.91),
        dict(feed=feed1, ioc_type=IOCType.hash,
             value="e3b0c44298fc1c149afbf4c8996fb924",
             threat_type="ransomware_dropper", confidence_score=0.99),
        dict(feed=feed1, ioc_type=IOCType.url,
             value="http://185.220.101.45/payload.exe",
             threat_type="malware_distribution", confidence_score=0.95),
        dict(feed=feed1, ioc_type=IOCType.email, value="noreply@malicious-update.com",
             threat_type="phishing_sender", confidence_score=0.88),
        dict(feed=feed2, ioc_type=IOCType.ip, value="203.0.113.100",
             threat_type="credential_stuffing", confidence_score=0.75),
        dict(feed=feed2, ioc_type=IOCType.domain, value="acme-support-portal.net",
             threat_type="brand_impersonation", confidence_score=0.82),
        dict(feed=feed2, ioc_type=IOCType.cve, value="CVE-2024-1086",
             threat_type="kernel_exploit", confidence_score=0.95),
    ]
    for ioc in ioc_defs:
        feed = ioc.pop("feed")
        db.add(ThreatIOC(feed_id=feed.id, is_active=True,
                         first_seen=now - timedelta(days=7),
                         last_seen=now - timedelta(hours=1), **ioc))
    await db.flush()

    # ── Identities ────────────────────────────────────────────────────────────
    identity_defs = [
        dict(email="alice@acme.io", display_name="Alice Chen", department="Engineering",
             role="Senior Engineer", risk_score=72.0, is_active=True,
             last_seen=now - timedelta(hours=1),
             ai_analysis="Elevated risk: accessed sensitive S3 bucket 3× outside business hours."),
        dict(email="bob@acme.io", display_name="Bob Martinez", department="Security",
             role="Security Analyst", risk_score=18.0, is_active=True,
             last_seen=now - timedelta(minutes=20), ai_analysis=None),
        dict(email="charlie@acme.io", display_name="Charlie Kim", department="DevOps",
             role="Platform Engineer", risk_score=35.0, is_active=True,
             last_seen=now - timedelta(hours=3), ai_analysis=None),
        dict(email="diana@acme.io", display_name="Diana Patel", department="Finance",
             role="CFO", risk_score=55.0, is_active=True,
             last_seen=now - timedelta(hours=8),
             ai_analysis="Failed auth attempt from unrecognised IP 203.0.113.55. Investigate."),
        dict(email="eve@acme.io", display_name="Eve Johnson", department="HR",
             role="HR Manager", risk_score=22.0, is_active=True,
             last_seen=now - timedelta(days=1), ai_analysis=None),
        dict(email="frank@acme.io", display_name="Frank Torres", department="Engineering",
             role="Intern", risk_score=8.0, is_active=False,
             last_seen=now - timedelta(days=90), ai_analysis=None),
    ]
    identities: list[IdentityProfile] = []
    for d in identity_defs:
        ident = IdentityProfile(**d)
        db.add(ident)
        identities.append(ident)
    await db.flush()

    behavior_defs = [
        (identities[0], BehaviorEventType.DATA_EXPORT, "10.0.5.12", "US", 25.0, True),
        (identities[0], BehaviorEventType.FILE_ACCESS, "10.0.5.12", "US", 10.0, False),
        (identities[0], BehaviorEventType.API_CALL, "10.0.5.12", "US", 5.0, False),
        (identities[1], BehaviorEventType.LOGIN, "10.0.1.8", "US", 0.0, False),
        (identities[1], BehaviorEventType.PRIVILEGE_ESCALATION, "10.0.1.8", "US", 8.0, False),
        (identities[3], BehaviorEventType.FAILED_AUTH, "203.0.113.55", "CN", 40.0, True),
        (identities[3], BehaviorEventType.LOGIN, "192.168.1.10", "US", 0.0, False),
        (identities[2], BehaviorEventType.API_CALL, "10.0.2.5", "US", 5.0, False),
    ]
    for ident, etype, ip, loc, contrib, flagged in behavior_defs:
        db.add(BehaviorEvent(
            identity_id=ident.id, event_type=etype,
            ip_address=ip, location=loc,
            risk_contribution=contrib, is_flagged=flagged,
            occurred_at=now - timedelta(hours=4),
        ))
    await db.flush()

    # ── Pentest Engagements ───────────────────────────────────────────────────
    pt1 = PenTestEngagement(
        name="Q4 External Pentest — Production API",
        methodology=PenTestMethodology.black_box,
        status=EngagementStatus.completed, risk_score=7.8,
        target_description="Production API gateway and web application at api.acme.io",
        scope={"targets": ["api.acme.io", "203.0.113.1"], "out_of_scope": ["DDoS"]},
        start_date=today - timedelta(days=30), end_date=today - timedelta(days=23),
        ai_report="Critical SQL injection found in /api/v1/users/search. Session fixation in auth flow. 3 high severity misconfigurations.",
    )
    pt2 = PenTestEngagement(
        name="Internal Network Segmentation Assessment",
        methodology=PenTestMethodology.white_box,
        status=EngagementStatus.active, risk_score=None,
        target_description="Internal network segmentation between prod and dev VLANs",
        scope={"targets": ["10.0.0.0/16"], "out_of_scope": ["10.0.99.0/24"]},
        start_date=today - timedelta(days=5), end_date=today + timedelta(days=5),
    )
    db.add(pt1); db.add(pt2)
    await db.flush()

    finding_defs = [
        dict(eng=pt1, title="SQL Injection — /api/v1/users/search", severity="critical",
             cvss_score=9.8, status=FindingStatus.open,
             description="Unsanitised `q` parameter allows UNION-based SQL injection. Full database dump possible.",
             attack_vector="GET /api/v1/users/search?q=' UNION SELECT ...",
             remediation_steps="Use ORM parameterised queries. Add WAF rule for SQL meta-characters.",
             proof_of_concept="' UNION SELECT username, password FROM users--"),
        dict(eng=pt1, title="Broken Session Fixation — auth flow", severity="high",
             cvss_score=7.3, status=FindingStatus.open,
             description="Session ID not regenerated post-login, allowing session fixation attacks.",
             attack_vector="Pre-auth session ID persists after successful login.",
             remediation_steps="Regenerate session ID immediately after authentication.",
             proof_of_concept=None),
        dict(eng=pt1, title="Server version disclosure in X-Powered-By", severity="low",
             cvss_score=2.1, status=FindingStatus.remediated,
             description="Server exposes 'Express/4.18.2' in response headers.",
             attack_vector="HTTP response header enumeration.",
             remediation_steps="app.disable('x-powered-by')",
             proof_of_concept=None),
        dict(eng=pt2, title="VLAN hopping possible via trunk port", severity="high",
             cvss_score=7.5, status=FindingStatus.open,
             description="Switch trunk port accessible from dev VLAN, allowing 802.1Q double-tagging.",
             attack_vector="802.1Q double-tagging to jump from VLAN 10 to VLAN 20.",
             remediation_steps="Disable DTP on access ports. Set native VLAN to unused VLAN 999.",
             proof_of_concept=None),
    ]
    for f in finding_defs:
        eng = f.pop("eng")
        db.add(PenTestFinding(engagement_id=eng.id, **f))
    await db.flush()

    # ── Secret Scans ──────────────────────────────────────────────────────────
    job1 = SecretScanJob(
        scan_target="dclawstack/backend-service",
        scan_type=ScanTargetType.git_repo,
        status=SecretScanStatus.completed,
        files_scanned=1284, secrets_found=3,
        started_at=now - timedelta(hours=2),
        completed_at=now - timedelta(hours=1, minutes=50),
    )
    job2 = SecretScanJob(
        scan_target="/app/config/settings.py",
        scan_type=ScanTargetType.config_file,
        status=SecretScanStatus.completed,
        files_scanned=12, secrets_found=1,
        started_at=now - timedelta(hours=5),
        completed_at=now - timedelta(hours=4, minutes=55),
    )
    db.add(job1); db.add(job2)
    await db.flush()

    secret_finding_defs = [
        dict(job=job1, file_path="config/database.yml", line_number=14,
             secret_type=SecretType.database_url, severity="critical",
             masked_value="postgresql://prod:s3cr****@prod-db:5432/app", is_revoked=False),
        dict(job=job1, file_path=".env.backup", line_number=3,
             secret_type=SecretType.api_key, severity="critical",
             masked_value="AKIA********************XAMPLE", is_revoked=True),
        dict(job=job1, file_path="scripts/deploy.sh", line_number=22,
             secret_type=SecretType.token, severity="high",
             masked_value="ghp_****************************Ab3x", is_revoked=False),
        dict(job=job2, file_path="/app/config/settings.py", line_number=8,
             secret_type=SecretType.jwt_secret, severity="high",
             masked_value="super-****-secret-key-do-not-share", is_revoked=False),
    ]
    for sf in secret_finding_defs:
        job = sf.pop("job")
        db.add(SecretFinding(job_id=job.id, is_false_positive=False,
                             detected_at=now - timedelta(hours=2), **sf))
    await db.flush()

    # ── Compliance Frameworks ─────────────────────────────────────────────────
    soc2 = ComplianceFramework(name="SOC 2 Type II", slug="soc2-type2", version="2017",
                               description="Trust Services Criteria for security, availability, and processing integrity.",
                               is_active=True)
    gdpr = ComplianceFramework(name="GDPR", slug="gdpr", version="2018",
                               description="EU General Data Protection Regulation.",
                               is_active=True)
    db.add(soc2); db.add(gdpr)
    await db.flush()

    control_defs = [
        dict(fw=soc2, control_id="CC6.1", title="Logical and Physical Access Controls",
             category="Access Control", status=ControlStatus.IMPLEMENTED,
             assigned_to="bob@acme.io", due_date=None,
             description="Restricts logical and physical access to information assets."),
        dict(fw=soc2, control_id="CC6.2", title="New User Access Provisioning",
             category="Access Control", status=ControlStatus.IMPLEMENTED,
             assigned_to="eve@acme.io", due_date=None,
             description="New user access is provisioned with appropriate approvals."),
        dict(fw=soc2, control_id="CC7.1", title="Vulnerability Detection Processes",
             category="Change Management", status=ControlStatus.PARTIALLY_IMPLEMENTED,
             assigned_to="bob@acme.io", due_date=today + timedelta(days=30),
             description="Processes to detect vulnerabilities on an ongoing basis."),
        dict(fw=soc2, control_id="CC9.2", title="Incident Response Plan",
             category="Risk Mitigation", status=ControlStatus.IMPLEMENTED,
             assigned_to="alice@acme.io", due_date=None,
             description="Incident response plan documented and tested annually."),
        dict(fw=gdpr, control_id="Art.5", title="Principles of Data Processing",
             category="Data Protection", status=ControlStatus.IMPLEMENTED,
             assigned_to="diana@acme.io", due_date=None,
             description="Personal data processed lawfully, fairly, and transparently."),
        dict(fw=gdpr, control_id="Art.17", title="Right to Erasure",
             category="Data Subject Rights", status=ControlStatus.PARTIALLY_IMPLEMENTED,
             assigned_to="diana@acme.io", due_date=today + timedelta(days=60),
             description="Mechanism for data subjects to request deletion of personal data."),
        dict(fw=gdpr, control_id="Art.25", title="Data Protection by Design",
             category="Technical Measures", status=ControlStatus.NOT_IMPLEMENTED,
             assigned_to="charlie@acme.io", due_date=today + timedelta(days=90),
             description="Privacy-by-design principles applied to new systems."),
        dict(fw=gdpr, control_id="Art.32", title="Security of Processing",
             category="Technical Measures", status=ControlStatus.IMPLEMENTED,
             assigned_to="bob@acme.io", due_date=None,
             description="Appropriate technical and organisational measures to ensure security."),
    ]
    for c in control_defs:
        fw = c.pop("fw")
        db.add(ComplianceControl(framework_id=fw.id, **c))
    await db.flush()

    await db.commit()

    return {
        "seeded": True,
        "assets": len(asset_defs),
        "vulnerabilities": len(vuln_defs),
        "security_scans": len(scan_defs),
        "incidents": 4,
        "policies": len(policy_defs),
        "siem_events": len(siem_defs),
        "threat_feeds": 2,
        "threat_iocs": len(ioc_defs),
        "identities": len(identity_defs),
        "pentest_engagements": 2,
        "pentest_findings": len(finding_defs),
        "secret_scan_jobs": 2,
        "secret_findings": len(secret_finding_defs),
        "compliance_frameworks": 2,
        "compliance_controls": len(control_defs),
    }


@router.delete("", status_code=200)
async def clear_data(db: AsyncSession = Depends(get_db)):
    """Wipe all data from all DClaw Secure tables."""
    for model in [
        Asset, Incident, Policy, SiemEvent,
        ThreatFeed, IdentityProfile, PenTestEngagement,
        SecretScanJob, ComplianceFramework,
    ]:
        await db.execute(delete(model))
    await db.commit()
    return {"cleared": True}
