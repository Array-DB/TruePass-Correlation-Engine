from datetime import UTC,datetime,timedelta
import pytest
from truepass.privacy import DataDomain,GovernancePolicy,RetentionPolicy,Sensitivity

def test_retention_decision():
    p=GovernancePolicy([RetentionPolicy(DataDomain.TELEMETRY,30,Sensitivity.CONFIDENTIAL)])
    created=datetime(2026,1,1,tzinfo=UTC)
    assert p.decision(DataDomain.TELEMETRY,created,now=created+timedelta(days=31)).delete

def test_naive_timestamp_rejected():
    p=GovernancePolicy([RetentionPolicy(DataDomain.TELEMETRY,1,Sensitivity.INTERNAL)])
    with pytest.raises(ValueError):p.decision(DataDomain.TELEMETRY,datetime(2026,1,1))
