"""Generate password hashes for the Streamlit dashboard.

Usage:
    python tools/create_password_hash.py
    python tools/create_password_hash.py "your-password"
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from auth_utils import hash_password  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a PBKDF2-SHA256 password hash for .streamlit/secrets.toml."
    )
    parser.add_argument("password", nargs="?", help="Password to hash.")
    args = parser.parse_args()

    password = args.password
    if password is None:
        password = getpass.getpass("Password: ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.", file=sys.stderr)
            return 1

    print(hash_password(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
