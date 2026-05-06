"""AES-256-GCM helpers for fake EMR encryption."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE_BYTES = 12
DEK_SIZE_BITS = 256


class DecryptionFailedError(ValueError):
    """Raised when AES-GCM authentication fails."""


@dataclass(frozen=True)
class EncryptedPayload:
    """AES-GCM encryption result with the authentication tag appended."""

    nonce: bytes
    ciphertext: bytes

    def to_json(self) -> dict[str, str]:
        return {
            "alg": "AES-256-GCM",
            "nonce_b64": base64.b64encode(self.nonce).decode("ascii"),
            "ciphertext_b64": base64.b64encode(self.ciphertext).decode("ascii"),
        }


def generate_dek() -> bytes:
    """Generate a fresh AES-256 data-encryption key."""
    return AESGCM.generate_key(bit_length=DEK_SIZE_BITS)


def encrypt(
    plaintext: bytes, aad: bytes, dek: bytes | None = None
) -> tuple[bytes, EncryptedPayload]:
    """Encrypt plaintext with AES-256-GCM and authenticated context bytes."""
    key = dek if dek is not None else generate_dek()
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return key, EncryptedPayload(nonce=nonce, ciphertext=ciphertext)


def decrypt(payload: EncryptedPayload, aad: bytes, dek: bytes) -> bytes:
    """Decrypt AES-GCM ciphertext and fail closed on authentication errors."""
    try:
        return AESGCM(dek).decrypt(payload.nonce, payload.ciphertext, aad)
    except InvalidTag as exc:
        raise DecryptionFailedError("AES-GCM authentication failed") from exc
