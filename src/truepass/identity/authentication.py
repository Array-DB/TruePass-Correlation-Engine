"""Pluggable identity verification without using identity data as key entropy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True, slots=True)
class FactorResult:
    factor_id: str
    verified: bool
    confidence: float
    reason: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class IdentityFactor(Protocol):
    factor_id: str
    def verify(self, subject_id: str, context: Mapping[str, object]) -> FactorResult: ...


@dataclass(frozen=True, slots=True)
class IdentityPolicy:
    threshold: float = 0.75
    minimum_factors: int = 1

    def __post_init__(self) -> None:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        if self.minimum_factors < 1:
            raise ValueError("minimum_factors must be >= 1")


@dataclass(frozen=True, slots=True)
class IdentityDecision:
    subject_id: str
    authorized: bool
    score: float
    results: tuple[FactorResult, ...]
    reason: str


class ContextAssertionFactor:
    """Verify an externally established boolean assertion in request/session context."""

    def __init__(self, factor_id: str, context_key: str, *, confidence: float = 1.0) -> None:
        self.factor_id = factor_id
        self.context_key = context_key
        self.confidence = confidence

    def verify(self, subject_id: str, context: Mapping[str, object]) -> FactorResult:
        ok = context.get(self.context_key) is True
        return FactorResult(self.factor_id, ok, self.confidence if ok else 0.0, f"external assertion {self.context_key}={'verified' if ok else 'absent'}")


class IdentityVerifier:
    def __init__(self, factors: list[IdentityFactor], policy: IdentityPolicy | None = None) -> None:
        if not factors:
            raise ValueError("at least one identity factor is required")
        self.factors = tuple(factors)
        self.policy = policy or IdentityPolicy()

    def verify(self, subject_id: str, context: Mapping[str, object]) -> IdentityDecision:
        results = tuple(f.verify(subject_id, context) for f in self.factors)
        passed = [r for r in results if r.verified]
        score = sum(r.confidence for r in passed) / len(results)
        authorized = len(passed) >= self.policy.minimum_factors and score >= self.policy.threshold
        reason = f"{len(passed)}/{len(results)} factors verified; policy threshold={self.policy.threshold:.2f}"
        return IdentityDecision(subject_id, authorized, score, results, reason)
