"""Privacy classification, retention, and deletion planning."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

class DataDomain(StrEnum):
    IDENTITY="identity"; BIOMETRICS="biometrics"; BEHAVIOR="behavior"; SECURITY="security"; TELEMETRY="telemetry"; FORENSICS="forensics"

class Sensitivity(StrEnum):
    PUBLIC="public"; INTERNAL="internal"; CONFIDENTIAL="confidential"; RESTRICTED="restricted"

@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    domain: DataDomain
    days: int
    sensitivity: Sensitivity
    deletion_supported: bool = True
    purpose: str = ""
    def __post_init__(self) -> None:
        if self.days < 0: raise ValueError("days must be non-negative")

@dataclass(frozen=True, slots=True)
class DeletionDecision:
    delete: bool
    reason: str
    expires_at: datetime

class GovernancePolicy:
    def __init__(self, policies: list[RetentionPolicy]) -> None:
        self._policies={p.domain:p for p in policies}
    def decision(self, domain: DataDomain, created_at: datetime, *, now: datetime | None=None) -> DeletionDecision:
        policy=self._policies[domain]
        if created_at.tzinfo is None: raise ValueError("created_at must be timezone-aware")
        current=now or datetime.now(UTC)
        expires=created_at+timedelta(days=policy.days)
        if not policy.deletion_supported:return DeletionDecision(False,"retention expired but storage class is immutable; remove local source and retain commitment only",expires)
        return DeletionDecision(current>=expires,"retention period expired" if current>=expires else "within retention period",expires)

DEFAULT_POLICIES=[
    RetentionPolicy(DataDomain.IDENTITY,90,Sensitivity.RESTRICTED,True,"authentication and access control"),
    RetentionPolicy(DataDomain.BIOMETRICS,30,Sensitivity.RESTRICTED,True,"optional consented verification"),
    RetentionPolicy(DataDomain.BEHAVIOR,30,Sensitivity.RESTRICTED,True,"optional research observations"),
    RetentionPolicy(DataDomain.SECURITY,180,Sensitivity.CONFIDENTIAL,True,"incident investigation"),
    RetentionPolicy(DataDomain.TELEMETRY,30,Sensitivity.CONFIDENTIAL,True,"operational correlation"),
    RetentionPolicy(DataDomain.FORENSICS,365,Sensitivity.RESTRICTED,True,"evidence preservation"),
]
