from truepass.graph import EventGraph
from truepass.models.events import Event,EventSource,EventType,Provenance

def test_event_graph_ranks_candidate_path():
    e=Event(source=EventSource.NETWORK,sensor_id='n',host='h',event_type=EventType.NETWORK_CONNECTION,features={'pid':7,'remote_ip':'203.0.113.7'},provenance=Provenance(collector='t',method='test'))
    g=EventGraph();start=g.add_event(e);paths=g.rank_paths(start)
    assert paths and paths[0].nodes[-1]=='remote:203.0.113.7'
    assert 0<paths[0].score<=1
