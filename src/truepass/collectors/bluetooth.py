"""Best-effort Bluetooth adapter state observation."""
from __future__ import annotations
import platform, shutil, socket, subprocess
from dataclasses import dataclass
from truepass.models.events import Event, EventSource, EventType, Provenance, Severity
@dataclass(frozen=True, slots=True)
class BluetoothState:
    available:bool=False; powered:bool|None=None; devices:tuple[str,...]=()
class BluetoothCollector:
    def __init__(self,*,sensor_id:str="bluetooth-local",host:str|None=None)->None:self.sensor_id=sensor_id; self.host=host or socket.gethostname(); self._previous:BluetoothState|None=None
    def snapshot(self)->BluetoothState:
        if platform.system()=="Linux" and shutil.which("bluetoothctl"):
            show=subprocess.run(["bluetoothctl","show"],capture_output=True,text=True,timeout=5,check=False)
            powered=None
            for line in show.stdout.splitlines():
                if "Powered:" in line: powered=line.split("Powered:",1)[1].strip().lower()=="yes"
            dev=subprocess.run(["bluetoothctl","devices"],capture_output=True,text=True,timeout=5,check=False)
            return BluetoothState(True,powered,tuple(sorted(x.strip() for x in dev.stdout.splitlines() if x.strip())))
        return BluetoothState()
    def poll(self)->list[Event]:
        cur=self.snapshot()
        if self._previous is None:self._previous=cur;return []
        if cur==self._previous:return []
        old=self._previous;self._previous=cur
        return [Event(source=EventSource.BLUETOOTH,sensor_id=self.sensor_id,host=self.host,event_type=EventType.BLUETOOTH_EVENT,severity=Severity.INFO,confidence=1.0,features={"previous":{"available":old.available,"powered":old.powered,"devices":list(old.devices)},"current":{"available":cur.available,"powered":cur.powered,"devices":list(cur.devices)}},metadata={"read_only":True},provenance=Provenance(collector="bluetooth",method="platform_adapter",platform=platform.platform()))]
