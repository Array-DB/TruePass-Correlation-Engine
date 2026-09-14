from truepass.correlation import TemporalCorrelationEngine
from truepass.models.events import Event,EventSource,EventType,Provenance

def e(source,etype,t,pid=None):
    return Event(timestamp_ns=t,received_timestamp_ns=t,source=source,sensor_id='s',host='h',event_type=etype,features={} if pid is None else {'pid':pid},provenance=Provenance(collector='t',method='test'))

def test_cross_domain_correlation_is_explainable():
    a=e(EventSource.SDR,EventType.RF_ANOMALY,1_000_000_000)
    b=e(EventSource.NETWORK,EventType.NETWORK_CONNECTION,1_040_000_000,42)
    r=TemporalCorrelationEngine(window_ms=100).correlate(a,[b])
    assert 0<r.score<=1
    assert any(x.code=='cross_domain' for x in r.reasons)
    assert len(r.evidence_ids)==2
