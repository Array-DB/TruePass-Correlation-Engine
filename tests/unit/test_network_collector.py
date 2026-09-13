from truepass.collectors.network import NetworkCollector,NetworkSocketSnapshot
from truepass.models.events import EventType
def test_network_poll_emits_new_listening_port(monkeypatch):
    c=NetworkCollector(host="test")
    s=NetworkSocketSnapshot(2,1,"127.0.0.1",8080,None,None,"LISTEN",123)
    snapshots=iter([set(),{s}]);monkeypatch.setattr(c,"snapshot",lambda:next(snapshots))
    assert c.poll()==[]; events=c.poll();assert len(events)==1;assert events[0].event_type==EventType.LISTENING_PORT;assert events[0].features["local_port"]==8080
