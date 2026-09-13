from truepass.collectors.wifi import WiFiCollector,WiFiState
from truepass.collectors.bluetooth import BluetoothCollector,BluetoothState
from truepass.models.events import EventType
def test_wifi_change(monkeypatch):
    c=WiFiCollector(host="h"); values=iter([WiFiState(),WiFiState(interface="wlan0",ssid="lab",connected=True)]);monkeypatch.setattr(c,"snapshot",lambda:next(values));assert c.poll()==[];assert c.poll()[0].event_type==EventType.WIFI_EVENT
def test_bluetooth_change(monkeypatch):
    c=BluetoothCollector(host="h");values=iter([BluetoothState(),BluetoothState(True,True,("Device AA:BB lab",))]);monkeypatch.setattr(c,"snapshot",lambda:next(values));assert c.poll()==[];assert c.poll()[0].event_type==EventType.BLUETOOTH_EVENT
