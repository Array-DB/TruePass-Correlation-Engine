"""Passive local network and listening-port telemetry."""
from __future__ import annotations
import platform, socket, time
from dataclasses import dataclass
from typing import Any
import psutil
from truepass.models.events import Event, EventSource, EventType, Provenance, Severity

@dataclass(frozen=True, slots=True)
class NetworkSocketSnapshot:
    family: int; type: int; local_ip: str; local_port: int; remote_ip: str|None; remote_port: int|None; status: str; pid: int|None

class NetworkCollector:
    def __init__(self, *, sensor_id: str="network-local", host: str|None=None) -> None:
        self.sensor_id=sensor_id; self.host=host or socket.gethostname(); self._previous:set[NetworkSocketSnapshot]|None=None
    def snapshot(self) -> set[NetworkSocketSnapshot]:
        out:set[NetworkSocketSnapshot]=set()
        for c in psutil.net_connections(kind="inet"):
            if not c.laddr: continue
            lip,lport=_addr(c.laddr); rip,rport=_addr(c.raddr) if c.raddr else (None,None)
            out.add(NetworkSocketSnapshot(int(c.family),int(c.type),lip,int(lport),rip,rport,c.status or "NONE",c.pid))
        return out
    def poll(self) -> list[Event]:
        current=self.snapshot()
        if self._previous is None: self._previous=current; return []
        added=current-self._previous; self._previous=current
        return [self._event(s) for s in sorted(added,key=lambda x:(x.local_port,x.pid or -1,x.remote_ip or ""))]
    def _event(self,s:NetworkSocketSnapshot)->Event:
        listening=s.status.upper()=="LISTEN"
        return Event(timestamp_ns=time.time_ns(),received_timestamp_ns=time.time_ns(),source=EventSource.NETWORK,sensor_id=self.sensor_id,host=self.host,event_type=EventType.LISTENING_PORT if listening else EventType.NETWORK_CONNECTION,severity=Severity.INFO,confidence=1.0,features={"family":s.family,"socket_type":s.type,"local_ip":s.local_ip,"local_port":s.local_port,"remote_ip":s.remote_ip,"remote_port":s.remote_port,"status":s.status,"pid":s.pid,"passive":True},metadata={"authorized_local_observation":True},provenance=Provenance(collector="network",method="psutil.net_connections",platform=platform.platform()))

def _addr(a:Any)->tuple[str,int]:
    return str(getattr(a,"ip",a[0])),int(getattr(a,"port",a[1]))
