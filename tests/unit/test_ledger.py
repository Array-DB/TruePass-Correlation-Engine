import json
from truepass.evidence.ledger import FileEvidenceLedger
from truepass.models.events import Event,EventSource,EventType,Provenance
def event():return Event(source=EventSource.SYSTEM,sensor_id="test",event_type=EventType.EVIDENCE_RECORD,provenance=Provenance(collector="test",method="unit"))
def test_ledger_verifies_and_detects_tampering(tmp_path):
    path=tmp_path/"ledger.jsonl";ledger=FileEvidenceLedger(path);ledger.append(event());ledger.append(event());assert ledger.verify().valid
    rows=path.read_text().splitlines(); data=json.loads(rows[0]);data["canonical_event"]=data["canonical_event"].replace('"confidence":1.0','"confidence":0.5');rows[0]=json.dumps(data);path.write_text("\n".join(rows)+"\n");assert not ledger.verify().valid
