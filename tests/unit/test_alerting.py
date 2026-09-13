from truepass.alerting import AlertEngine, AlertRule
from truepass.models.events import Event,EventSource,EventType,Provenance,Severity

def event():
    return Event(source=EventSource.SDR,sensor_id="sdr-1",event_type=EventType.RF_ANOMALY,severity=Severity.HIGH,provenance=Provenance(collector="test",method="synthetic"))

def test_alert_dedup_and_cooldown():
    now=[10.0]
    rule=AlertRule("r1","investigate",Severity.HIGH,frozenset({EventType.RF_ANOMALY}),30.0)
    engine=AlertEngine([rule],clock=lambda:now[0])
    e=event()
    assert len(engine.evaluate(e))==1
    assert engine.evaluate(e)==[]
    now[0]=41.0
    assert len(engine.evaluate(e))==1

def test_rule_filters_type():
    rule=AlertRule("r","x",event_types=frozenset({EventType.INCIDENT}))
    assert AlertEngine([rule]).evaluate(event())==[]
