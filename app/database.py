import json
import os
from pathlib import Path

import psycopg2

VAULT_DB_FILE = Path("/vault/secrets/db.json")


def get_connection():
    """Create an application connection using the latest Vault credentials."""

    if VAULT_DB_FILE.is_file():
        with VAULT_DB_FILE.open("r", encoding="utf-8") as file:
            credentials = json.load(file)

        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            raise RuntimeError("Vault database credentials are incomplete")

    else:
        # Temporary fallback during Vault migration
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        if not username or not password:
            raise RuntimeError("Database credentials are not configured")

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=username,
        password=password,
        connect_timeout=5,
    )


def get_schema_connection():
    """Use existing static credentials for database schema initialization."""

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )
