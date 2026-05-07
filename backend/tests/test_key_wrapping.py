from __future__ import annotations

from dataclasses import replace

import pytest
from securemed.crypto.aes_gcm import generate_dek
from securemed.crypto.encoding import b64decode, b64encode
from securemed.crypto.key_wrapping import (
    KeyUnwrapFailedError,
    generate_x25519_key_pair,
    release_aad,
    unwrap_dek_from_gateway,
    wrap_dek_for_provider,
)


def _aad() -> dict[str, str]:
    return release_aad(
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        purpose="treatment",
        release_id="rel_001",
    )


def test_x25519_hkdf_aes_gcm_wrap_unwrap_roundtrip() -> None:
    provider = generate_x25519_key_pair()
    dek = generate_dek()

    wrapped = wrap_dek_for_provider(
        dek=dek,
        provider_public_key_b64=provider.public_b64(),
        aad=_aad(),
    )

    assert (
        unwrap_dek_from_gateway(
            wrapped_dek=wrapped,
            provider_private_key_b64=provider.private_b64(),
            expected_aad=_aad(),
        )
        == dek
    )


def test_wrong_provider_private_key_cannot_unwrap() -> None:
    intended_provider = generate_x25519_key_pair()
    wrong_provider = generate_x25519_key_pair()
    wrapped = wrap_dek_for_provider(
        dek=generate_dek(),
        provider_public_key_b64=intended_provider.public_b64(),
        aad=_aad(),
    )

    with pytest.raises(KeyUnwrapFailedError):
        unwrap_dek_from_gateway(
            wrapped_dek=wrapped,
            provider_private_key_b64=wrong_provider.private_b64(),
            expected_aad=_aad(),
        )


def test_tampered_wrapped_dek_fails() -> None:
    provider = generate_x25519_key_pair()
    wrapped = wrap_dek_for_provider(
        dek=generate_dek(),
        provider_public_key_b64=provider.public_b64(),
        aad=_aad(),
    )
    tampered = bytearray(b64decode(wrapped.wrapped_dek_b64))
    tampered[0] ^= 1

    with pytest.raises(KeyUnwrapFailedError):
        unwrap_dek_from_gateway(
            wrapped_dek=replace(wrapped, wrapped_dek_b64=b64encode(bytes(tampered))),
            provider_private_key_b64=provider.private_b64(),
            expected_aad=_aad(),
        )


def test_tampered_release_aad_fails() -> None:
    provider = generate_x25519_key_pair()
    wrapped = wrap_dek_for_provider(
        dek=generate_dek(),
        provider_public_key_b64=provider.public_b64(),
        aad=_aad(),
    )
    tampered_aad = _aad()
    tampered_aad["purpose"] = "insurance"

    with pytest.raises(KeyUnwrapFailedError):
        unwrap_dek_from_gateway(
            wrapped_dek=wrapped,
            provider_private_key_b64=provider.private_b64(),
            expected_aad=tampered_aad,
        )
