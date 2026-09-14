"""Security-hardening primitives for replay, clock, secret, and input defenses."""
from __future__ import annotations
from dataclasses import dataclass
import hmac
import time
from collections import OrderedDict

@dataclass(frozen=True, slots=True)
class ClockAssessment:
    healthy: bool
    skew_ns: int
    maximum_allowed_skew_ns: int

class ReplayGuard:
    def __init__(self, capacity: int = 10_000) -> None:
        if capacity < 1: raise ValueError("capacity must be positive")
        self.capacity=capacity; self._seen: OrderedDict[str,None]=OrderedDict()
    def accept(self, token: str) -> bool:
        if token in self._seen:return False
        self._seen[token]=None
        if len(self._seen)>self.capacity:self._seen.popitem(last=False)
        return True

def assess_clock(remote_timestamp_ns: int, *, now_ns: int | None=None, maximum_skew_ns: int=5_000_000_000) -> ClockAssessment:
    now=time.time_ns() if now_ns is None else now_ns
    skew=abs(now-remote_timestamp_ns)
    return ClockAssessment(skew<=maximum_skew_ns,skew,maximum_skew_ns)

def constant_time_secret_matches(candidate: str, expected: str) -> bool:
    return hmac.compare_digest(candidate.encode(), expected.encode())

def redact_secret(value: str, *, visible_suffix: int=4) -> str:
    if visible_suffix < 0: raise ValueError("visible_suffix must be non-negative")
    if not value:return ""
    suffix=value[-visible_suffix:] if visible_suffix else ""
    return "***"+suffix
