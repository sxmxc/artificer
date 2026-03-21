from __future__ import annotations

import base64
import hashlib
import json
from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from app.config import Settings


def _derive_fernet_key(seed: str) -> bytes:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def _credential_fernet() -> Fernet:
    settings = Settings()
    configured_key = str(settings.credential_encryption_key or "").strip()
    if not configured_key:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY must be configured before credential secrets can be read or written."
        )

    try:
        return Fernet(configured_key.encode("utf-8"))
    except ValueError:
        # Allow a plain seed-like env value and derive a valid Fernet key from it.
        return Fernet(_derive_fernet_key(configured_key))


def validate_credential_crypto_settings() -> None:
    _credential_fernet()


def encrypt_secret_material(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    token = _credential_fernet().encrypt(serialized.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret_material(token: str) -> dict[str, Any]:
    try:
        raw = _credential_fernet().decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Credential secret material could not be decrypted.") from exc

    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Credential secret material is not valid JSON.") from exc

    return decoded if isinstance(decoded, dict) else {}
