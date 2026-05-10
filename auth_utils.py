"""Authentication helpers for the Streamlit dashboard."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 600_000
SALT_BYTES = 16


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    """Return a PBKDF2-SHA256 password hash suitable for Streamlit secrets."""
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a PBKDF2-SHA256 encoded hash."""
    if not password or not password_hash:
        return False

    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != HASH_ALGORITHM:
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            _decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(_encode(digest), expected)
    except (ValueError, TypeError):
        return False
