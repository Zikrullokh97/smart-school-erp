from __future__ import annotations

import pytest

from smart_school.auth.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    password = "SuperSecure123!"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash)
    assert not verify_password("WrongPassword", password_hash)


def test_refresh_token_hash_is_deterministic() -> None:
    refresh_token = create_refresh_token()
    assert hash_refresh_token(refresh_token) == hash_refresh_token(refresh_token)
    assert hash_refresh_token(refresh_token) != hash_refresh_token(create_refresh_token())


def test_access_token_encode_decode() -> None:
    access_token, expires_in = create_access_token("11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222")
    payload = decode_jwt_token(access_token, expected_type=ACCESS_TOKEN_TYPE)

    assert payload["sub"] == "11111111-1111-1111-1111-111111111111"
    assert payload["tenant_id"] == "22222222-2222-2222-2222-222222222222"
    assert payload["type"] == ACCESS_TOKEN_TYPE
    assert expires_in > 0


@pytest.mark.parametrize("unexpected_type", ["refresh", "invalid"])
def test_access_token_rejects_wrong_token_type(unexpected_type: str) -> None:
    access_token, _ = create_access_token("00000000-0000-0000-0000-000000000000", "11111111-1111-1111-1111-111111111111")

    with pytest.raises(Exception):
        decode_jwt_token(access_token, expected_type=unexpected_type)
