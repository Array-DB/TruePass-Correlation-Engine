"""Cryptographic signing for evidence commitments.

Evidence signing is deliberately separate from identity verification and wallet
key generation. Private signing keys never enter event metadata or logs.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


@dataclass(frozen=True, slots=True)
class SignatureEnvelope:
    algorithm: str
    key_id: str
    digest_hex: str
    signature_hex: str
    public_key_hex: str


class EvidenceSigner(Protocol):
    @property
    def key_id(self) -> str: ...
    def sign_digest(self, digest: bytes) -> SignatureEnvelope: ...


class Ed25519EvidenceSigner:
    """Sign 32-byte evidence digests with Ed25519."""

    algorithm = "Ed25519"

    def __init__(self, private_key: Ed25519PrivateKey, *, key_id: str = "local-ed25519") -> None:
        self._private_key = private_key
        self._key_id = key_id

    @property
    def key_id(self) -> str:
        return self._key_id

    @classmethod
    def generate(cls, *, key_id: str = "local-ed25519") -> "Ed25519EvidenceSigner":
        return cls(Ed25519PrivateKey.generate(), key_id=key_id)

    @classmethod
    def load_pem(cls, path: str | Path, *, password: bytes | None = None, key_id: str = "local-ed25519") -> "Ed25519EvidenceSigner":
        key = serialization.load_pem_private_key(Path(path).read_bytes(), password=password)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("PEM key is not Ed25519")
        return cls(key, key_id=key_id)

    def private_key_pem(self, *, password: bytes | None = None) -> bytes:
        enc: serialization.KeySerializationEncryption = (
            serialization.NoEncryption() if password is None else serialization.BestAvailableEncryption(password)
        )
        return self._private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            enc,
        )

    def sign_digest(self, digest: bytes) -> SignatureEnvelope:
        if len(digest) != 32:
            raise ValueError("evidence digest must be exactly 32 bytes")
        signature = self._private_key.sign(digest)
        public = self._private_key.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        return SignatureEnvelope(self.algorithm, self.key_id, digest.hex(), signature.hex(), public.hex())


def verify_signature(envelope: SignatureEnvelope) -> bool:
    if envelope.algorithm != "Ed25519":
        return False
    try:
        digest = bytes.fromhex(envelope.digest_hex)
        signature = bytes.fromhex(envelope.signature_hex)
        public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(envelope.public_key_hex))
        if len(digest) != 32:
            return False
        public.verify(signature, digest)
        return True
    except (ValueError, InvalidSignature):
        return False
