"""TruePass command-line interface."""
from __future__ import annotations
import argparse,json,os,platform,sys,time
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from truepass import __version__
from truepass.collectors.bluetooth import BluetoothCollector
from truepass.collectors.network import NetworkCollector
from truepass.collectors.processes import ProcessCollector
from truepass.collectors.wifi import WiFiCollector
from truepass.config import AppSettings
from truepass.database.models import Base
from truepass.database.session import create_database_engine
from truepass.evidence.ledger import FileEvidenceLedger
from truepass.monitoring.logging import configure_logging
from truepass.sdr.sources import HackRFOneSource,SDRConfig,SyntheticIQSource

def build_parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="truepass",description="Defensive telemetry and forensic-correlation platform.");p.add_argument("--version",action="version",version=f"%(prog)s {__version__}");p.add_argument("--config",default=None); sub=p.add_subparsers(dest="command")
    run=sub.add_parser("run");run.add_argument("--host",default="127.0.0.1");run.add_argument("--port",type=int,default=8000); collect=sub.add_parser("collect"); cs=collect.add_subparsers(dest="collector")
    proc=cs.add_parser("processes");proc.add_argument("--once",action="store_true");proc.add_argument("--interval",type=float)
    for name in ("network","wifi","bluetooth"): q=cs.add_parser(name);q.add_argument("--once",action="store_true");q.add_argument("--interval",type=float)
    sdr=cs.add_parser("sdr-synthetic");sdr.add_argument("--samples",type=int,default=16)
    hackrf=cs.add_parser("sdr-hackrf");hackrf.add_argument("--samples",type=int,default=4096);hackrf.add_argument("--serial",default=None)
    sub.add_parser("status"); verify=sub.add_parser("verify");vs=verify.add_subparsers(dest="verify_command"); ledger=vs.add_parser("ledger");ledger.add_argument("--path",default=None)
    sub.add_parser("doctor");db=sub.add_parser("database");ds=db.add_subparsers(dest="database_command");ds.add_parser("create");ds.add_parser("ping");return p

def main(argv:list[str]|None=None)->int:
    p=build_parser();a=p.parse_args(argv)
    if a.command is None:p.print_help();return 0
    settings=AppSettings.load(a.config);configure_logging(settings.logging.level,json_output=settings.logging.json_output)
    if a.command=="status": print(json.dumps(_safe_settings(settings),indent=2,sort_keys=True));return 0
    if a.command=="doctor":return _doctor(settings)
    if a.command=="database":return _database(settings,a.database_command)
    if a.command=="verify":
        if a.verify_command!="ledger":p.error("choose: truepass verify ledger")
        r=FileEvidenceLedger(a.path or settings.evidence.ledger_path).verify(); print(json.dumps({"valid":r.valid,"records":r.records,"error":r.error},indent=2));return 0 if r.valid else 1
    if a.command=="collect":
        if a.collector=="processes":return _collect_processes(settings,a.once,a.interval)
        if a.collector=="network":return _generic(NetworkCollector(sensor_id=settings.network_collector.sensor_id),a.once,a.interval or settings.network_collector.interval_seconds)
        if a.collector=="wifi":return _generic(WiFiCollector(sensor_id=settings.wifi_collector.sensor_id),a.once,a.interval or settings.wifi_collector.interval_seconds)
        if a.collector=="bluetooth":return _generic(BluetoothCollector(sensor_id=settings.bluetooth_collector.sensor_id),a.once,a.interval or settings.bluetooth_collector.interval_seconds)
        if a.collector=="sdr-synthetic":
            c=settings.sdr; src=SyntheticIQSource(SDRConfig(c.sample_rate,c.center_frequency,c.gain,c.buffer_size,c.device)); samples=src.read_samples(a.samples);print(json.dumps([[x.real,x.imag] for x in samples]));return 0
        if a.collector=="sdr-hackrf":
            c=settings.sdr; cfg=SDRConfig(c.sample_rate,c.center_frequency,c.gain,c.buffer_size,"hackrf")
            try:
                with HackRFOneSource(cfg,serial=a.serial) as src:samples=src.read_samples(a.samples)
            except (RuntimeError,ValueError) as exc:
                print(f"HackRF receive error: {exc}",file=sys.stderr);return 1
            print(json.dumps([[x.real,x.imag] for x in samples]));return 0
        p.error("choose a collector")
    if a.command=="run":
        import uvicorn
        uvicorn.run("truepass.api.server:app",host=a.host,port=a.port,reload=False)
        return 0
    return 0

def _generic(c:object,once:bool,delay:float)->int:
    snapshot=getattr(c,"snapshot");poll=getattr(c,"poll")
    if once: print(json.dumps(_jsonable(snapshot()),indent=2,sort_keys=True));return 0
    poll()
    try:
        while True:
            time.sleep(delay)
            for event in poll():print(event.canonical_bytes().decode(),flush=True)
    except KeyboardInterrupt:return 0

def _jsonable(v:object)->object:
    if isinstance(v,(set,tuple,list)):return [_jsonable(x) for x in v]
    if hasattr(v,"__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(v)
    return v

def _collect_processes(s:AppSettings,once:bool,interval:float|None)->int:
    c=s.process_collector; collector=ProcessCollector(sensor_id=c.sensor_id,include_command_line=c.include_command_line,include_sockets=c.include_sockets)
    if once:
        print(json.dumps([{"pid":x.pid,"ppid":x.ppid,"name":x.name,"executable":x.executable,"username":x.username,"socket_count":len(x.sockets)} for x in sorted(collector.snapshot().values(),key=lambda x:x.pid)],indent=2));return 0
    collector.poll();delay=interval or c.interval_seconds
    try:
        while True:
            time.sleep(delay)
            for e in collector.poll():print(e.canonical_bytes().decode(),flush=True)
    except KeyboardInterrupt:return 0

def _database(s:AppSettings,cmd:str|None)->int:
    if cmd is None:return 2
    e=create_database_engine(s)
    try:
        if cmd=="create":Base.metadata.create_all(e);print("Database tables created.")
        else:
            with e.connect() as c:c.execute(text("SELECT 1"))
            print("Database connection OK.")
        return 0
    except SQLAlchemyError as exc:print(f"Database error: {exc}",file=sys.stderr);return 1
    finally:e.dispose()
def _doctor(s:AppSettings)->int:
    checks={"python":platform.python_version(),"platform":platform.platform(),"config_exists":Path(os.getenv("TRUEPASS_CONFIG","config/truepass.toml")).exists(),"database":"unknown","hackrf_devices":[d.raw for d in HackRFOneSource.enumerate_devices()]};e=create_database_engine(s)
    try:
        with e.connect() as c:c.execute(text("SELECT 1"));checks["database"]="ok"
    except SQLAlchemyError:checks["database"]="unavailable"
    finally:e.dispose()
    print(json.dumps(checks,indent=2,sort_keys=True));return 0 if checks["database"]=="ok" else 1
def _safe_settings(s:AppSettings)->dict[str,object]:
    d=s.model_dump(mode="json");db=d.get("database")
    if isinstance(db,dict) and "url" in db:db["url"]=_redact_database_url(str(db["url"]))
    return d
def _redact_database_url(url:str)->str:
    if "@" not in url or "://" not in url:return url
    scheme,rem=url.split("://",1);cred,host=rem.rsplit("@",1);user=cred.split(":",1)[0];return f"{scheme}://{user}:***@{host}"
