from truepass.evidence.signing import Ed25519EvidenceSigner, SignatureEnvelope, verify_signature


def test_ed25519_evidence_signature_round_trip() -> None:
    signer = Ed25519EvidenceSigner.generate(key_id="test-key")
    env = signer.sign_digest(bytes.fromhex("ab" * 32))
    assert env.key_id == "test-key"
    assert verify_signature(env)


def test_signature_tamper_is_detected() -> None:
    signer = Ed25519EvidenceSigner.generate()
    env = signer.sign_digest(bytes.fromhex("11" * 32))
    bad = SignatureEnvelope(env.algorithm, env.key_id, "22" * 32, env.signature_hex, env.public_key_hex)
    assert not verify_signature(bad)
