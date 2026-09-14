from truepass.correlation import TemporalCorrelationEngine
from truepass.incidents import IncidentScorer
from truepass.models.events import Event,EventSource,EventType,Provenance,Severity

def mk(src,typ,t,features=None):return Event(timestamp_ns=t,received_timestamp_ns=t,source=src,sensor_id='s',host='host',event_type=typ,features=features or {},provenance=Provenance(collector='t',method='test'))

def test_incident_score_is_bounded_and_explained():
    a=mk(EventSource.SDR,EventType.RF_ANOMALY,1000,{'anomaly_score':.9})
    b=mk(EventSource.PROCESS,EventType.PROCESS_STARTED,2000)
    c=TemporalCorrelationEngine(window_ms=1).correlate(a,[b])
    r=IncidentScorer().score(a,c)
    assert 0<=r.score<=1 and 0<=r.confidence<=1
    assert isinstance(r.severity,Severity)
    assert r.candidate_explanations
