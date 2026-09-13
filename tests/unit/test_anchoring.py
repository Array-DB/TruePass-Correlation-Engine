import asyncio
import json
from truepass.evidence.anchoring import BitcoinAnchor, FileAnchor, NoOpAnchor


def test_noop_anchor_never_broadcasts() -> None:
    receipt = asyncio.run(NoOpAnchor().anchor(bytes.fromhex("33" * 32)))
    assert receipt.status == "not_broadcast"


def test_file_anchor_records_commitment(tmp_path) -> None:
    path = tmp_path / "anchors.jsonl"
    receipt = asyncio.run(FileAnchor(path).anchor(bytes.fromhex("44" * 32)))
    assert receipt.provider == "file"
    row = json.loads(path.read_text().splitlines()[0])
    assert row["digest_hex"] == "44" * 32


def test_bitcoin_anchor_uses_injected_broadcaster_only() -> None:
    seen = []
    def broadcaster(digest: bytes) -> str:
        seen.append(digest)
        return "txid-demo"
    receipt = asyncio.run(BitcoinAnchor(broadcaster).anchor(bytes.fromhex("55" * 32)))
    assert receipt.reference == "txid-demo"
    assert seen == [bytes.fromhex("55" * 32)]
