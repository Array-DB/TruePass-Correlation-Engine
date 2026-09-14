"""Typed configuration with TOML loading, environment overrides, and safe defaults."""
from __future__ import annotations
import os, tomllib
from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
class DatabaseSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); url:str="postgresql+psycopg://truepass:truepass@localhost:5432/truepass"; echo:bool=False; pool_size:int=Field(default=5,ge=1,le=100)
class LoggingSettings(BaseModel):
    model_config=ConfigDict(extra="forbid",populate_by_name=True); level:str="INFO"; json_output:bool=Field(default=True,alias="json")
class MetricsSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); enabled:bool=True; host:str="127.0.0.1"; port:int=Field(default=9464,ge=1,le=65535)
class ProcessCollectorSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); sensor_id:str="process-local"; interval_seconds:float=Field(default=2.0,ge=.1,le=3600); include_command_line:bool=False; include_sockets:bool=True
class NetworkCollectorSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); sensor_id:str="network-local"; interval_seconds:float=Field(default=2.0,ge=.1,le=3600)
class WiFiCollectorSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); sensor_id:str="wifi-local"; interval_seconds:float=Field(default=5.0,ge=.1,le=3600)
class BluetoothCollectorSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); sensor_id:str="bluetooth-local"; interval_seconds:float=Field(default=5.0,ge=.1,le=3600)
class EvidenceSettings(BaseModel):
    model_config=ConfigDict(extra="forbid"); ledger_path:str="data/evidence-ledger.jsonl"
class SDRSettings(BaseModel):
    model_config=ConfigDict(extra="forbid")
    sample_rate:float=Field(default=2_000_000.0,gt=0,le=50_000_000)
    center_frequency:float=Field(default=100_000_000.0,ge=0,le=10_000_000_000)
    gain:float=Field(default=0.0,ge=-100,le=100)
    buffer_size:int=Field(default=4096,ge=8,le=10_000_000)
    device:str="synthetic"
class AppSettings(BaseModel):
    model_config=ConfigDict(extra="forbid")
    environment:str="development"; database:DatabaseSettings=Field(default_factory=DatabaseSettings); logging:LoggingSettings=Field(default_factory=LoggingSettings); metrics:MetricsSettings=Field(default_factory=MetricsSettings); process_collector:ProcessCollectorSettings=Field(default_factory=ProcessCollectorSettings); network_collector:NetworkCollectorSettings=Field(default_factory=NetworkCollectorSettings); wifi_collector:WiFiCollectorSettings=Field(default_factory=WiFiCollectorSettings); bluetooth_collector:BluetoothCollectorSettings=Field(default_factory=BluetoothCollectorSettings); evidence:EvidenceSettings=Field(default_factory=EvidenceSettings); sdr:SDRSettings=Field(default_factory=SDRSettings)
    @classmethod
    def load(cls,path:str|Path|None=None)->"AppSettings":
        config_path=Path(path or os.getenv("TRUEPASS_CONFIG","config/truepass.toml")); data:dict[str,Any]={}
        if config_path.exists():
            with config_path.open("rb") as h: parsed=tomllib.load(h)
            if not isinstance(parsed,dict): raise ValueError(f"configuration root must be a table: {config_path}")
            data=parsed
        _apply_environment(data); return cls.model_validate(data)
def _coerce_environment_value(value:str)->Any:
    n=value.strip().lower()
    if n in {"true","false"}:return n=="true"
    try:return int(value)
    except ValueError:pass
    try:return float(value)
    except ValueError:return value
def _apply_environment(data:dict[str,Any])->None:
    for key,raw in os.environ.items():
        if not key.startswith("TRUEPASS_") or key in {"TRUEPASS_CONFIG","TRUEPASS_API_KEY","TRUEPASS_LEDGER_PATH","TRUEPASS_AUTO_COLLECT","TRUEPASS_TEST_DATABASE_URL","TRUEPASS_DOD_SKIP_HARDWARE"}:continue
        path=key.removeprefix("TRUEPASS_").lower().split("__"); cursor=data
        for seg in path[:-1]:
            nxt=cursor.setdefault(seg,{})
            if not isinstance(nxt,dict):raise ValueError(f"environment override conflicts with scalar setting: {key}")
            cursor=nxt
        cursor[path[-1]]=_coerce_environment_value(raw)
