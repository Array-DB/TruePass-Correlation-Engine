"""Append-only SHA-256 forensic ledger with full-chain verification."""
from __future__ import annotations
import hashlib,json,time
from dataclasses import asdict,dataclass
from pathlib import Path
from truepass.models.events import Event
ZERO_HASH="0"*64
@dataclass(frozen=True,slots=True)
class LedgerRecord:
    sequence:int; event_id:str; previous_hash:str; event_hash:str; timestamp_ns:int; canonical_event:str; canonicalization_version:str="1"
@dataclass(frozen=True,slots=True)
class LedgerVerification:
    valid:bool; records:int; error:str|None=None
class FileEvidenceLedger:
    """Local append-only JSONL evidence chain. Each line carries canonical event bytes for self-verification."""
    def __init__(self,path:str|Path)->None:self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,event:Event)->LedgerRecord:
        records=self._read();prev=records[-1].event_hash if records else ZERO_HASH;canonical=event.canonical_bytes()
        digest=hashlib.sha256(bytes.fromhex(prev)+canonical).hexdigest();record=LedgerRecord(len(records)+1,str(event.event_id),prev,digest,time.time_ns(),canonical.decode("utf-8"))
        with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(asdict(record),sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n")
        return record
    def verify(self)->LedgerVerification:
        try:records=self._read()
        except Exception as e:return LedgerVerification(False,0,f"parse_error: {e}")
        prev=ZERO_HASH
        for i,r in enumerate(records,1):
            if r.sequence!=i:return LedgerVerification(False,len(records),f"sequence_mismatch_at_{i}")
            if r.previous_hash!=prev:return LedgerVerification(False,len(records),f"previous_hash_mismatch_at_{i}")
            expected=hashlib.sha256(bytes.fromhex(prev)+r.canonical_event.encode("utf-8")).hexdigest()
            if r.event_hash!=expected:return LedgerVerification(False,len(records),f"event_hash_mismatch_at_{i}")
            try:
                event_id=str(json.loads(r.canonical_event)["event_id"])
            except (json.JSONDecodeError,KeyError,TypeError):return LedgerVerification(False,len(records),f"canonical_event_invalid_at_{i}")
            if event_id!=r.event_id:return LedgerVerification(False,len(records),f"event_id_mismatch_at_{i}")
            prev=r.event_hash
        return LedgerVerification(True,len(records))
    def _read(self)->list[LedgerRecord]:
        if not self.path.exists():return []
        return [LedgerRecord(**json.loads(line)) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
