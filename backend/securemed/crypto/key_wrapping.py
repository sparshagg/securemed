"""X25519 + HKDF-SHA256 + AES-GCM DEK wrapping."""

from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from securemed.crypto.canonical import canonical_json_bytes
from securemed.crypto.encoding import b64decode, b64encode

WRAP_NONCE_SIZE_BYTES = 12
WRAP_SALT_SIZE_BYTES = 32
WRAP_KEY_SIZE_BYTES = 32
X25519_PUBLIC_KEY_SIZE_BYTES = 32
X25519_PRIVATE_KEY_SIZE_BYTES = 32


class KeyUnwrapFailedError(ValueError):
    """Raised when wrapped DEK authentication or context validation fails."""


@dataclass(frozen=True)
class X25519KeyPair:
    private_key: x25519.X25519PrivateKey
    public_key: x25519.X25519PublicKey

    def private_bytes(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def public_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def private_b64(self) -> str:
        return b64encode(self.private_bytes())

    def public_b64(self) -> str:
        return b64encode(self.public_bytes())


@dataclass(frozen=True)
class WrappedDEK:
    release_id: str
    gateway_ephemeral_public_key_b64: str
    salt_b64: str
    nonce_b64: str
    wrapped_dek_b64: str
    aad: dict[str, str]
    alg: str = "X25519-HKDF-SHA256-AES-256-GCM"


def generate_x25519_key_pair() -> X25519KeyPair:
    """Generate an X25519 keypair for a demo provider or gateway release."""
    private_key = x25519.X25519PrivateKey.generate()
    return X25519KeyPair(private_key=private_key, public_key=private_key.public_key())


def load_x25519_private_key_b64(value: str) -> x25519.X25519PrivateKey:
    raw = b64decode(value)
    if len(raw) != X25519_PRIVATE_KEY_SIZE_BYTES:
        raise ValueError("X25519 private key must be 32 raw bytes")
    return x25519.X25519PrivateKey.from_private_bytes(raw)


def load_x25519_public_key_b64(value: str) -> x25519.X25519PublicKey:
    raw = b64decode(value)
    if len(raw) != X25519_PUBLIC_KEY_SIZE_BYTES:
        raise ValueError("X25519 public key must be 32 raw bytes")
    return x25519.X25519PublicKey.from_public_bytes(raw)


def release_aad(
    *,
    record_id: str,
    provider_id: str,
    credential_commitment: str,
    purpose: str,
    release_id: str,
) -> dict[str, str]:
    """Build the release context bound to DEK wrapping authentication."""
    return {
        "record_id": record_id,
        "provider_id": provider_id,
        "credential_commitment": credential_commitment,
        "purpose": purpose,
        "release_id": release_id,
    }


def _derive_wrapping_key(
    shared_secret: bytes, salt: bytes, aad: dict[str, str]
) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=WRAP_KEY_SIZE_BYTES,
        salt=salt,
        info=canonical_json_bytes(
            {
                "domain": "securemed-dek-release",
                "aad": aad,
            }
        ),
    ).derive(shared_secret)


def wrap_dek_for_provider(
    *,
    dek: bytes,
    provider_public_key_b64: str,
    aad: dict[str, str],
) -> WrappedDEK:
    """Wrap a per-record DEK to a provider using an ephemeral gateway key."""
    gateway_key_pair = generate_x25519_key_pair()
    provider_public_key = load_x25519_public_key_b64(provider_public_key_b64)
    shared_secret = gateway_key_pair.private_key.exchange(provider_public_key)
    salt = os.urandom(WRAP_SALT_SIZE_BYTES)
    nonce = os.urandom(WRAP_NONCE_SIZE_BYTES)
    wrapping_key = _derive_wrapping_key(shared_secret, salt, aad)
    wrapped_dek = AESGCM(wrapping_key).encrypt(nonce, dek, canonical_json_bytes(aad))
    return WrappedDEK(
        release_id=aad["release_id"],
        gateway_ephemeral_public_key_b64=gateway_key_pair.public_b64(),
        salt_b64=b64encode(salt),
        nonce_b64=b64encode(nonce),
        wrapped_dek_b64=b64encode(wrapped_dek),
        aad=aad,
    )


def unwrap_dek_from_gateway(
    *,
    wrapped_dek: WrappedDEK,
    provider_private_key_b64: str,
    expected_aad: dict[str, str],
) -> bytes:
    """Unwrap a DEK as the intended provider and fail closed on tampering."""
    if wrapped_dek.aad != expected_aad:
        raise KeyUnwrapFailedError("wrapped DEK AAD does not match expected context")
    provider_private_key = load_x25519_private_key_b64(provider_private_key_b64)
    gateway_public_key = load_x25519_public_key_b64(
        wrapped_dek.gateway_ephemeral_public_key_b64
    )
    shared_secret = provider_private_key.exchange(gateway_public_key)
    wrapping_key = _derive_wrapping_key(
        shared_secret, b64decode(wrapped_dek.salt_b64), expected_aad
    )
    try:
        return AESGCM(wrapping_key).decrypt(
            b64decode(wrapped_dek.nonce_b64),
            b64decode(wrapped_dek.wrapped_dek_b64),
            canonical_json_bytes(expected_aad),
        )
    except InvalidTag as exc:
        raise KeyUnwrapFailedError("wrapped DEK authentication failed") from exc


def wrapped_dek_from_json(value: dict[str, object]) -> WrappedDEK:
    """Parse a JSON-compatible wrapped DEK payload."""
    return WrappedDEK(
        release_id=str(value["release_id"]),
        gateway_ephemeral_public_key_b64=str(value["gateway_ephemeral_public_key_b64"]),
        salt_b64=str(value["salt_b64"]),
        nonce_b64=str(value["nonce_b64"]),
        wrapped_dek_b64=str(value["wrapped_dek_b64"]),
        aad={str(key): str(item) for key, item in dict(value["aad"]).items()},
        alg=str(value.get("alg", "X25519-HKDF-SHA256-AES-256-GCM")),
    )


def wrapped_dek_to_json(value: WrappedDEK) -> dict[str, object]:
    """Serialize a wrapped DEK for API responses and local JSON."""
    return {
        "alg": value.alg,
        "release_id": value.release_id,
        "gateway_ephemeral_public_key_b64": value.gateway_ephemeral_public_key_b64,
        "salt_b64": value.salt_b64,
        "nonce_b64": value.nonce_b64,
        "wrapped_dek_b64": value.wrapped_dek_b64,
        "aad": value.aad,
    }
