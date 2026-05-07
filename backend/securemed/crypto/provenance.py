"""ECDSA P-256 provenance signing and verification."""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from securemed.crypto.canonical import canonical_json_bytes


class ProvenanceVerificationError(ValueError):
    """Raised when a provenance signature is invalid."""


def generate_signing_key() -> ec.EllipticCurvePrivateKey:
    """Generate an ephemeral P-256 signing key for the local demo."""
    return ec.generate_private_key(ec.SECP256R1())


def sign_manifest(
    private_key: ec.EllipticCurvePrivateKey,
    manifest: dict[str, object],
) -> bytes:
    """Sign a provenance manifest using deterministic JSON bytes."""
    return private_key.sign(canonical_json_bytes(manifest), ec.ECDSA(hashes.SHA256()))


def verify_manifest_signature(
    public_key: ec.EllipticCurvePublicKey,
    manifest: dict[str, object],
    signature: bytes,
) -> None:
    """Verify a provenance manifest signature."""
    try:
        public_key.verify(
            signature,
            canonical_json_bytes(manifest),
            ec.ECDSA(hashes.SHA256()),
        )
    except InvalidSignature as exc:
        raise ProvenanceVerificationError("provenance signature is invalid") from exc


def public_key_pem(public_key: ec.EllipticCurvePublicKey) -> str:
    """Serialize a public key for manifests or API responses."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def load_public_key_pem(value: str) -> ec.EllipticCurvePublicKey:
    """Load a P-256 public key from PEM."""
    key = serialization.load_pem_public_key(value.encode("ascii"))
    if not isinstance(key, ec.EllipticCurvePublicKey):
        raise TypeError("provenance public key must be an elliptic-curve key")
    return key
