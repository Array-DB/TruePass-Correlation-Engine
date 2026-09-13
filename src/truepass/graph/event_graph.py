"""Event/entity graph and candidate entry-path ranking."""
from __future__ import annotations
from dataclasses import dataclass
import networkx as nx
from truepass.models.events import Event

@dataclass(frozen=True, slots=True)
class RankedPath:
    nodes: tuple[str,...]
    score: float

class EventGraph:
    def __init__(self) -> None: self.graph=nx.MultiDiGraph()
    def add_event(self,event:Event)->str:
        eid=f"event:{event.event_id}";self.graph.add_node(eid,kind="EVENT",source=event.source.value,event_type=event.event_type.value)
        host=f"host:{event.host}";self.graph.add_node(host,kind="HOST");self.graph.add_edge(eid,host,relation="OBSERVED_ON",weight=.8)
        pid=event.features.get("pid") or event.metadata.get("pid")
        if pid is not None:
            proc=f"process:{event.host}:{pid}";self.graph.add_node(proc,kind="PROCESS");self.graph.add_edge(host,proc,relation="RUNS",weight=.9);self.graph.add_edge(eid,proc,relation="DERIVED_FROM",weight=.9)
        remote=event.features.get("remote_ip") or event.metadata.get("remote_ip")
        if remote:
            rn=f"remote:{remote}";self.graph.add_node(rn,kind="REMOTE_HOST");self.graph.add_edge(eid,rn,relation="CONNECTED_TO",weight=.8)
        return eid
    def temporally_link(self,a:Event,b:Event,*,window_ms:float=500)->bool:
        if abs(a.timestamp_ns-b.timestamp_ns)>window_ms*1_000_000:return False
        na,nb=self.add_event(a),self.add_event(b);delta=abs(a.timestamp_ns-b.timestamp_ns)/1_000_000
        weight=max(.05,1-delta/window_ms);self.graph.add_edge(na,nb,relation="TEMPORALLY_NEAR",weight=weight);return True
    def rank_paths(self,start:str,target_kind:str="REMOTE_HOST",*,limit:int=5)->tuple[RankedPath,...]:
        if start not in self.graph:return ()
        out=[]
        for node,data in self.graph.nodes(data=True):
            if data.get("kind")!=target_kind:continue
            for path in nx.all_simple_paths(nx.DiGraph(self.graph),start,node,cutoff=6):
                score=1.0
                for x,y in zip(path,path[1:]):
                    edges=self.graph.get_edge_data(x,y) or {};score*=max((float(v.get("weight",.5)) for v in edges.values()),default=.5)
                out.append(RankedPath(tuple(path),score))
        return tuple(sorted(out,key=lambda x:x.score,reverse=True)[:limit])
