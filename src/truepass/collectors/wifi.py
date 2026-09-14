"""Best-effort, read-only Wi-Fi state collection with graceful fallbacks."""
from __future__ import annotations
import platform, shutil, socket, subprocess, time
from dataclasses import asdict, dataclass
from truepass.models.events import Event, EventSource, EventType, Provenance, Severity
@dataclass(frozen=True, slots=True)
class WiFiState:
    interface:str|None=None; ssid:str|None=None; bssid:str|None=None; signal_dbm:int|None=None; channel:str|None=None; frequency_mhz:int|None=None; security:str|None=None; connected:bool=False
class WiFiCollector:
    def __init__(self,*,sensor_id:str="wifi-local",host:str|None=None)->None: self.sensor_id=sensor_id; self.host=host or socket.gethostname(); self._previous:WiFiState|None=None
    def snapshot(self)->WiFiState:
        if platform.system()=="Linux" and shutil.which("nmcli"):
            p=subprocess.run(["nmcli","-t","-f","DEVICE,TYPE,STATE,CONNECTION","device"],capture_output=True,text=True,timeout=5,check=False)
            for line in p.stdout.splitlines():
                parts=line.split(":",3)
                if len(parts)==4 and parts[1]=="wifi" and parts[2]=="connected": return WiFiState(interface=parts[0],ssid=parts[3],connected=True)
        return WiFiState()
    def poll(self)->list[Event]:
        cur=self.snapshot()
        if self._previous is None: self._previous=cur; return []
        if cur==self._previous:return []
        old=self._previous; self._previous=cur
        return [Event(source=EventSource.WIFI,sensor_id=self.sensor_id,host=self.host,event_type=EventType.WIFI_EVENT,severity=Severity.INFO,confidence=1.0,features={"previous":asdict(old),"current":asdict(cur)},metadata={"read_only":True},provenance=Provenance(collector="wifi",method="platform_adapter",platform=platform.platform()))]
